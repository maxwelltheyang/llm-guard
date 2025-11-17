import logging
from autogen import ConversableAgent, LLMConfig
from autogen.tools import tool
from prompts import CODER_PROMPT, JUDGE_PROMPT
import json
import subprocess
import os
from pathlib import Path
from markdown_it import MarkdownIt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
llm_config = LLMConfig.from_json(path="LLAMA_CONFIG_LIST")

@tool(description="Runs semgrep static analysis on the target path.")
def run_semgrep(target_path: str) -> dict:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    result = subprocess.run(
        ["semgrep", "--json", "--config", "p/security-audit", target_path],
        capture_output=True,
        text=True,
        env=env,
    )

    if result.returncode not in (0, 1):
        raise RuntimeError(
            f"Semgrep failed with code {result.returncode}:\n{result.stderr}"
        )

    try:
        raw = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError("Failed to parse Semgrep JSON output.")

    findings = []

    for item in raw.get("results", []):
        findings.append({
            "check_id": item.get("check_id"),
            "path": item.get("path"),
            "severity": item.get("extra", {}).get("severity"),
            "message": item.get("extra", {}).get("message"),
            "line": item.get("start", {}).get("line"),
            "end_line": item.get("end", {}).get("line"),
        })

    return findings

@tool(description="Writes code content to a file and returns the file path.")
def write_code_file(content: str, filename: str) -> str:
    md = MarkdownIt()
    tokens = md.parse(content)

    for tok in tokens:
        if tok.type == "fence":
            language = tok.info.strip().lower()
            code = tok.content

            if language:
                ext = language if language != "text" else "txt"
            else:
                ext = "txt"

            folder_path = Path("code")
            folder_path.mkdir(exist_ok=True)

            filename = f"{filename}.{ext}"
            filepath = folder_path / filename

            filepath.write_text(code, encoding="utf-8")

            return str(filepath)

    raise ValueError("No fenced code block found in the content.")

@tool(description="Extracts code content from a given file path.")
def extract_code_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    return path.read_text(encoding="utf-8")

def setup_agents():
    coder = ConversableAgent(
        name="coder",
        system_message=CODER_PROMPT,
        is_termination_msg=lambda x: "SATISFACTORY" in x["content"],
        llm_config=llm_config,
        functions = [write_code_file],
        human_input_mode="NEVER",
    )

    reviewer = ConversableAgent(
        name="judge",
        system_message=JUDGE_PROMPT,
        llm_config=llm_config,
        functions = [extract_code_file, run_semgrep],
        human_input_mode="NEVER",
    )

    # coder.register_for_llm(name="write_code_file", description="Write Python code to a file.")(write_code_file)
    # coder.register_for_execution(name="write_code_file")(write_code_file)

    # reviewer.register_for_llm(name="extract_code_file", description="Extract code from a file path.")(extract_code_file)
    # reviewer.register_for_execution(name="extract_code_file")(extract_code_file)

    # reviewer.register_for_llm(name="run_semgrep", description="Execute the semgrep tool.")(run_semgrep)
    # reviewer.register_for_execution(name="run_semgrep")(run_semgrep)

    return coder, reviewer

def run_experiment(coder, reviewer, prompt):
    response = reviewer.run(
        recipient=coder,
        message=prompt,
        max_turns=10
    )

    response.process()

    return response.messages[-2]["content"]

if __name__ == '__main__':
    with open('prompts/test.json', 'r') as f:
        prompts = json.load(f)

    coder, reviewer = setup_agents()
    results = {}
    for i, prompt_data in enumerate(prompts):
        prompt_copy = prompt_data.copy()
        prompt_result = run_experiment(coder, reviewer, prompt_copy["Prompt"])
        prompt_copy["Result"] = prompt_result
        results[i] = prompt_copy

    with open('results/test.json', 'w') as f:
        json.dump(results, f, indent=4)