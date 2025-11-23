import logging
from autogen import ConversableAgent, LLMConfig
from prompts import CODER_PROMPT, judge_prompt
import json
import subprocess
import os
from pathlib import Path
import textwrap
from datetime import datetime
import re
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import redirect_stdout

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_semgrep(target_path: str) -> dict:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONWARNINGS"] = "ignore:invalid escape sequence"

    result = subprocess.run(
        ["semgrep", "--json", "--config", "p/security-audit", target_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )

    if result.returncode not in (0, 1):
        raise RuntimeError(
            f"Semgrep failed with code {result.returncode}:\n{result.stderr}"
        )

    return result.stdout

def write_code_file(content: str, output_path: Path) -> str:
    pattern = r"```[a-zA-Z0-9_+-]+\s*\n([\s\S]*?)```"
    match = re.search(pattern, content)

    if match:
        content = match.group(1)
    content = textwrap.dedent(content).lstrip("\n")
    content = content.encode("utf-8").decode("unicode_escape")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    logger.info(f"Wrote code file to {output_path}")
    return str(output_path)

def setup_agents(llm_config: LLMConfig, working_dir: str):
    coder = ConversableAgent(
        name="coder",
        system_message=CODER_PROMPT,
        is_termination_msg=lambda m: isinstance(m, dict)
            and isinstance(m.get("content"), str)
            and "SATISFACTORY" in m["content"],
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    reviewer = ConversableAgent(
        name="judge",
        system_message=judge_prompt(working_dir),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    reviewer.register_for_llm(
        name="run_semgrep",
        description="Runs semgrep static code analysis given a filepath."
    )(run_semgrep)
    coder.register_for_execution(name="run_semgrep")(run_semgrep)

    reviewer.register_for_llm(
        name="write_code_file",
        description="Write fenced code into a codefile for later execution."
    )(write_code_file)
    coder.register_for_execution(name="write_code_file")(write_code_file)

    return coder, reviewer

def run_single_experiment(i: int, prompt_text: str, llm_config_path: str, base_result_dir: str, timestamp: str, max_turns: int):
    exp_dir = Path(base_result_dir) / f"{timestamp}-{i}"
    exp_dir.mkdir(parents=True, exist_ok=True)

    log_path = exp_dir / f"experiment_{i}.log"

    with log_path.open("w", encoding="utf-8") as log_f, redirect_stdout(log_f):
        print(f"[Experiment {i}] Starting…")
        print(f"[Experiment {i}] Prompt: {prompt_text!r}")

        try:
            llm_config = LLMConfig.from_json(path=llm_config_path)
            coder, reviewer = setup_agents(llm_config, exp_dir)

            response = reviewer.run(
                recipient=coder,
                message=prompt_text,
                max_turns=max_turns,
            )
            response.process()

            result_content = response.summary
            result_obj = {"Prompt": prompt_text, "Result": result_content}

            with (exp_dir / "result.json").open("w", encoding="utf-8") as fh:
                json.dump(result_obj, fh, indent=4, ensure_ascii=False)

            print(f"[Experiment {i}] Completed successfully.")
            return i, result_obj

        except Exception as e:
            print(f"[Experiment {i}] FAILED: {e}")
            return i, {"Prompt": prompt_text, "Error": str(e)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt_file", type=str, default="prompts/test.json")
    parser.add_argument("--result_dir", type=str, default="results")
    parser.add_argument("--llm_config", type=str, default="LLAMA_CONFIG_LIST")
    parser.add_argument("--max_workers", type=int, default=1)
    parser.add_argument("--max_turns", type=int, default=10)
    args = parser.parse_args()

    with open(args.prompt_file, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    Path(args.result_dir).mkdir(parents=True, exist_ok=True)

    results = {}
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = []
        for i, prompt_data in enumerate(prompts):
            prompt_text = prompt_data.get("Prompt", "")
            futures.append(
                executor.submit(
                    run_single_experiment,
                    i,
                    prompt_text,
                    args.llm_config,
                    args.result_dir,
                    timestamp,
                    args.max_turns,
                )
            )

        for fut in as_completed(futures):
            i, result_obj = fut.result()
            results[i] = result_obj

    aggregated_path = Path(args.result_dir) / "test.json"
    with aggregated_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    logger.info(f"Wrote aggregated results to {aggregated_path}")

if __name__ == "__main__":
    main()
