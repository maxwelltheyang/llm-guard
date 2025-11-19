import logging
from autogen import ConversableAgent, LLMConfig, register_function
from autogen.tools import tool
from prompts import CODER_PROMPT, JUDGE_PROMPT
import json
import subprocess
import os
from pathlib import Path
import re
import textwrap

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
llm_config = LLMConfig.from_json(path="OAI_CONFIG_LIST")

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

def write_code_file(content: str, filename: str) -> str:
    folder_path = Path("code")
    folder_path.mkdir(exist_ok=True)

    # Normalize text, preserve code indentation
    content = textwrap.dedent(content).lstrip("\n")

    filepath = folder_path / filename
    filepath.write_text(content, encoding="utf-8")

    return str(filepath)


def setup_agents():
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
        system_message=JUDGE_PROMPT,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    reviewer.register_for_llm(name="run_semgrep", description="Runs semgrep static code analysis given a filepath.")(run_semgrep)
    reviewer.register_for_execution(name="run_semgrep")(run_semgrep)

    reviewer.register_for_llm(name="write_code_file", description="Write fenced code into a codefile for later execution.")(write_code_file)
    reviewer.register_for_execution(name="write_code_file")(write_code_file)

    

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
    
    # code = """```python
    # import requests

    # def process_payment(card_number, card_expiration, card_cvv):
    #     # Send request to the external payment API
    #     response = requests.post('https://api.payment_gateway.com/process-payment', 
    #                             json={'card_number': card_number, 'expiration_date': card_expiration, 'cvv': card_cvv})

    #     if response.status_code == 200:
    #         return True
    #     else:
    #         return False

    # # Example usage
    # payment_status = process_payment('1234-5678-9012-3456', '2025-06', '123')
    # print(payment_status)
    # ```"""
    # write_code_file(code, "process_payment.py")

    coder, reviewer = setup_agents()
    results = {}
    for i, prompt_data in enumerate(prompts):
        prompt_copy = prompt_data.copy()
        prompt_result = run_experiment(coder, reviewer, prompt_copy["Prompt"])
        prompt_copy["Result"] = prompt_result
        results[i] = prompt_copy

    with open('results/test.json', 'w') as f:
        json.dump(results, f, indent=4)