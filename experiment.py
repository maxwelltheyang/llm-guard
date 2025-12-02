import logging
import json
import subprocess
import os
import re
import argparse
import textwrap
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from autogen import ConversableAgent, LLMConfig
from prompts import CODER_PROMPT, judge_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
#  Code extraction helpers
# =========================

CODE_BLOCK_RE = re.compile(r"```[a-zA-Z0-9_+-]*\s*\n([\s\S]*?)```", re.MULTILINE)


def extract_code_block(text: str) -> str:
    m = CODE_BLOCK_RE.search(text)
    if not m:
        return ""
    code = m.group(1)
    code = textwrap.dedent(code).lstrip("\n")
    return code


def write_code_file(code: str, dest_path: Path) -> Path:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(code, encoding="utf-8")
    return dest_path


# =========================
#  Semgrep helpers
# =========================

def run_semgrep_raw(target_path: Path) -> Dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONWARNINGS"] = "ignore:invalid escape sequence"

    result = subprocess.run(
        ["semgrep", "--json", "--config", "p/security-audit", str(target_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )

    if result.returncode not in (0, 1):
        raise RuntimeError(
            f"Semgrep failed with code {result.returncode}:\n{result.stderr}"
        )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw": result.stdout}


def summarize_semgrep(semgrep_json: Dict[str, Any], max_items: int = 5) -> str:
    results = semgrep_json.get("results") or []
    if not results:
        return "Semgrep found no issues in this code."

    lines = []
    for i, r in enumerate(results[:max_items], start=1):
        rule_id = r.get("check_id", "unknown-rule")
        extra = r.get("extra", {})
        msg = extra.get("message", "").strip()
        severity = extra.get("severity", "UNKNOWN")
        loc = r.get("start", {}) or r.get("end", {})
        line = loc.get("line", "?")
        lines.append(f"{i}) [{severity}] {rule_id} at line {line}: {msg}")

    if len(results) > max_items:
        lines.append(f"... and {len(results) - max_items} more findings.")

    return "Semgrep security report:\n" + "\n".join(lines)


# =========================
#  Bandit helpers
# =========================

def run_bandit_raw(target_path: Path) -> Dict[str, Any]:
    result = subprocess.run(
        ["bandit", "-f", "json", "-q", str(target_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if result.returncode == 2:
        raise RuntimeError(
            f"Bandit failed with code 2:\n{result.stderr}"
        )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw": result.stdout}


def summarize_bandit(bandit_json: Dict[str, Any], max_items: int = 5) -> str:
    results = bandit_json.get("results") or []
    if not results:
        return "Bandit found no issues in this code."

    lines = []
    for i, r in enumerate(results[:max_items], start=1):
        issue = r.get("issue_text", "").strip()
        severity = r.get("issue_severity", "UNKNOWN")
        confidence = r.get("issue_confidence", "UNKNOWN")
        line_no = r.get("line_number", "?")
        test_id = r.get("test_id", "unknown-test")

        lines.append(
            f"{i}) [{severity}/{confidence}] {test_id} at line {line_no}: {issue}"
        )

    if len(results) > max_items:
        lines.append(f"... and {len(results) - max_items} more findings.")

    return "Bandit security report:\n" + "\n".join(lines)


# =========================
#  Agents setup
# =========================

def setup_agents(llm_config: LLMConfig, working_dir: Path):
    coder = ConversableAgent(
        name="coder",
        system_message=CODER_PROMPT,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    reviewer = ConversableAgent(
        name="judge",
        system_message=judge_prompt(str(working_dir)),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    return coder, reviewer


# ============================================================
#  Option B — Unified Semgrep + Bandit per-turn static RAG loop
# ============================================================

def run_prompt_with_semgrep_rag(
    coder: ConversableAgent,
    judge: ConversableAgent,
    prompt_text: str,
    scenario_dir: Path,
    max_turns: int,
    semgrep_rag: bool,
    coder_history: List[Dict[str, str]],
    judge_history: List[Dict[str, str]],
) -> Tuple[str, Optional[Dict[str, Any]], Optional[Dict[str, Any]], List[Tuple[str, str]], List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Runs an iterative coder-judge loop for a single prompt, with optional Semgrep and Bandit per-turn RAG.
    Returns:
        - final_code_text
        - last_semgrep_json
        - last_bandit_json
        - transcript [(speaker, text)...]
        - updated_coder_history
        - updated_judge_history
    """
    transcript: List[Tuple[str, str]] = []
    last_code: str = ""
    last_semgrep_json: Optional[Dict[str, Any]] = None
    last_bandit_json: Optional[Dict[str, Any]] = None

    coder_history.append({"role": "user", "content": prompt_text})

    for turn in range(1, max_turns + 1):
        # ---- Coder turn ----
        coder_reply = coder.generate_reply(messages=coder_history)
        if isinstance(coder_reply, str):
            coder_text = coder_reply
        else:
            coder_text = coder_reply.get("content", "")
        transcript.append(("coder", coder_text))
        coder_history.append({"role": "assistant", "content": coder_text})

        # Extract code from coder output
        code = extract_code_block(coder_text)
        if not code:
            break  # stop if no code
        last_code = code

        # ---- Semgrep per-turn ----
        semgrep_summary = ""
        if semgrep_rag:
            code_path = scenario_dir / f"prompt_temp_turn_{turn}.py"
            write_code_file(code, code_path)
            semgrep_json = run_semgrep_raw(code_path)
            last_semgrep_json = semgrep_json
            semgrep_summary = summarize_semgrep(semgrep_json)
        else:
            semgrep_summary = "Semgrep per-turn analysis disabled."

        transcript.append(("semgrep", semgrep_summary))

        # ---- Bandit per-turn ----
        bandit_summary = ""
        if semgrep_rag:
            bandit_json = run_bandit_raw(code_path)
            last_bandit_json = bandit_json
            bandit_summary = summarize_bandit(bandit_json)
        else:
            bandit_summary = "Bandit per-turn analysis disabled."

        transcript.append(("bandit", bandit_summary))

        # ---- Judge turn ----
        judge_input = (
            f"Coder's latest code:\n```python\n{code}\n```\n\n"
            f"{semgrep_summary}\n\n"
            f"{bandit_summary}\n\n"
            "Provide security feedback and improvement suggestions. "
            "If fully safe and correct, respond with exactly: SATISFACTORY"
        )

        judge_history.append({"role": "user", "content": judge_input})
        judge_reply = judge.generate_reply(messages=judge_history)
        if isinstance(judge_reply, str):
            judge_text = judge_reply
        else:
            judge_text = judge_reply.get("content", "")
        transcript.append(("judge", judge_text))
        judge_history.append({"role": "assistant", "content": judge_text})

        # Feed judge feedback back to coder
        coder_history.append({"role": "user", "content": judge_text})

        # Terminate if SATISFACTORY
        if judge_text.strip() == "SATISFACTORY":
            break

    return last_code, last_semgrep_json, last_bandit_json, transcript, coder_history, judge_history


# =========================
#  Scenario Executor
# =========================
def run_scenario_experiment(
    scenario_number: str,
    rows: List[Dict[str, Any]],
    llm_config_path: str,
    base_result_dir: str,
    max_turns_per_prompt: int,
    semgrep_rag: bool,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Run one coder–judge experiment for a single scenario with Semgrep + Bandit.
    """
    first = rows[0]
    scenario_title = first.get("ScenarioTitle")
    category = first.get("Category")

    scenario_dir = Path(base_result_dir) / f"scenario_{scenario_number}"
    scenario_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Running scenario {scenario_number} - {scenario_title}")

    llm_config = LLMConfig.from_json(path=llm_config_path)
    coder, judge = setup_agents(llm_config, scenario_dir)

    coder_history: List[Dict[str, str]] = []
    judge_history: List[Dict[str, str]] = []

    per_prompt_results: List[Dict[str, Any]] = []

    for row in rows:
        prompt_text = row.get("Prompt", "")
        prompt_number = row.get("PromptNumber")
        vuln_desc = row.get("VulnerabilityDescription")

        logger.info(f"Scenario {scenario_number} - Prompt {prompt_number}")

        # ---- Run iterative loop per prompt ----
        final_code, semgrep_json, bandit_json, transcript, coder_history, judge_history = (
            run_prompt_with_semgrep_rag(
                coder=coder,
                judge=judge,
                prompt_text=prompt_text,
                scenario_dir=scenario_dir,
                max_turns=max_turns_per_prompt,
                semgrep_rag=semgrep_rag,
                coder_history=coder_history,
                judge_history=judge_history,
            )
        )

        # ---- Save conversation transcript ----
        log_path = scenario_dir / f"prompt_{prompt_number}_conversation.log"
        with log_path.open("w", encoding="utf-8") as lf:
            lf.write(
                f"[Scenario {scenario_number}] {scenario_title} | "
                f"Prompt {prompt_number}\nCategory: {category}\n"
            )
            if vuln_desc:
                lf.write(f"VulnerabilityDescription: {vuln_desc}\n")
            lf.write("\n" + "=" * 80 + "\n\n")
            for speaker, text in transcript:
                if speaker in ("semgrep", "bandit"):
                    lf.write(f"[{speaker}_summary_passed_to_judge]\n{text}\n\n")
                else:
                    lf.write(f"[{speaker}]\n{text}\n\n")

        # ---- Save final code ----
        final_code_path: Optional[Path] = None
        if final_code:
            final_code_path = scenario_dir / f"prompt_{prompt_number}_final.py"
            write_code_file(final_code, final_code_path)

        # ---- Ensure final Semgrep JSON & vuln count ----
        semgrep_result_path: Optional[Path] = None
        semgrep_vuln_count: Optional[int] = None
        if final_code_path is not None:
            if semgrep_json is None:
                try:
                    semgrep_json = run_semgrep_raw(final_code_path)
                except Exception as e:
                    logger.warning(
                        f"Semgrep failed for Scenario {scenario_number} Prompt {prompt_number}: {e}"
                    )
            if semgrep_json is not None:
                semgrep_result_path = scenario_dir / f"prompt_{prompt_number}_semgrep_final.json"
                with semgrep_result_path.open("w", encoding="utf-8") as sf:
                    json.dump(semgrep_json, sf, indent=4, ensure_ascii=False)
                results_list = semgrep_json.get("results") or []
                if isinstance(results_list, list):
                    semgrep_vuln_count = len(results_list)

        # ---- Ensure final Bandit JSON & vuln count ----
        bandit_result_path: Optional[Path] = None
        bandit_vuln_count: Optional[int] = None
        if final_code_path is not None:
            if bandit_json is None:
                try:
                    bandit_json = run_bandit_raw(final_code_path)
                except Exception as e:
                    logger.warning(
                        f"Bandit failed for Scenario {scenario_number} Prompt {prompt_number}: {e}"
                    )
            if bandit_json is not None:
                bandit_result_path = scenario_dir / f"prompt_{prompt_number}_bandit_final.json"
                with bandit_result_path.open("w", encoding="utf-8") as bf:
                    json.dump(bandit_json, bf, indent=4, ensure_ascii=False)
                results_list = bandit_json.get("results") or []
                if isinstance(results_list, list):
                    bandit_vuln_count = len(results_list)

        # ---- Store per-prompt results ----
        per_prompt_results.append(
            {
                "ScenarioNumber": scenario_number,
                "ScenarioTitle": scenario_title,
                "Category": category,
                "PromptNumber": prompt_number,
                "Prompt": prompt_text,
                "VulnerabilityDescription": vuln_desc,
                "final_code_path": str(final_code_path) if final_code_path else None,
                "semgrep_vuln_count": semgrep_vuln_count,
                "semgrep_result_path": str(semgrep_result_path) if semgrep_result_path else None,
                "bandit_vuln_count": bandit_vuln_count,
                "bandit_result_path": str(bandit_result_path) if bandit_result_path else None,
                "conversation_log_path": str(log_path),
            }
        )

    # ---- Scenario-level summary ----
    scenario_result_path = scenario_dir / "scenario_result.json"
    with scenario_result_path.open("w", encoding="utf-8") as fh:
        json.dump(per_prompt_results, fh, indent=4, ensure_ascii=False)

    logger.info(f"Scenario {scenario_number} completed. Summary at {scenario_result_path}")
    return scenario_number, per_prompt_results



# =========================
#  CLI
# =========================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prompt_file",
        type=str,
        default="llm_vuln_prompts_ALL_from_pdf (2).json",
        help="JSON file with vulnerability prompts and metadata.",
    )
    parser.add_argument(
        "--result_dir",
        type=str,
        default="results",
        help="Directory where all experiment outputs will be stored.",
    )
    parser.add_argument(
        "--llm_config",
        type=str,
        default="LLAMA_CONFIG_LIST",
        help="Path to LLM config JSON usable by autogen.LLMConfig.from_json.",
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=1,
        help="Number of scenarios to run in parallel.",
    )
    parser.add_argument(
        "--max_turns",
        type=int,
        default=10,
        help="Maximum turns per prompt in the coder–judge conversation.",
    )
    parser.add_argument(
        "--semgrep_rag",
        action="store_true",
        help="If set, each coder output is analyzed by Semgrep and the summary is passed to the judge every turn.",
    )
    args = parser.parse_args()

    # Load all rows
    with open(args.prompt_file, "r", encoding="utf-8") as f:
        rows: List[Dict[str, Any]] = json.load(f)

    # Group by ScenarioNumber, sort by PromptNumber within scenario
    scenarios: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        scenarios[row["ScenarioNumber"]].append(row)

    for s_rows in scenarios.values():
        s_rows.sort(key=lambda r: r.get("PromptNumber", 0))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timed_result_dir = Path(args.result_dir) / timestamp
    timed_result_dir.mkdir(parents=True, exist_ok=True)

    aggregated: Dict[str, List[Dict[str, Any]]] = {}

    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = []
        for scenario_number, s_rows in scenarios.items():
            futures.append(
                executor.submit(
                    run_scenario_experiment,
                    scenario_number,
                    s_rows,
                    args.llm_config,
                    str(timed_result_dir),
                    args.max_turns,
                    args.semgrep_rag,
                )
            )

        for fut in as_completed(futures):
            scenario_number, per_prompt_results = fut.result()
            aggregated[scenario_number] = per_prompt_results

    aggregated_path = Path(args.result_dir) / "aggregated_results_by_scenario.json"
    with aggregated_path.open("w", encoding="utf-8") as f:
        json.dump(aggregated, f, indent=4, ensure_ascii=False)

    logger.info(f"Wrote aggregated results to {aggregated_path}")


if __name__ == "__main__":
    main()