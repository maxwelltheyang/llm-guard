import logging
from autogen import ConversableAgent, LLMConfig
from prompts import CODER_PROMPT, JUDGE_PROMPT
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
llm_config = LLMConfig.from_json(path="LLAMA_CONFIG_LIST")

def setup_agents():
    coder = ConversableAgent(
        name="coder",
        system_message=CODER_PROMPT,
        is_termination_msg=lambda x: "SATISFACTORY" in x["content"],
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    reviewer = ConversableAgent(
        name="judge",
        system_message=JUDGE_PROMPT,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    return coder, reviewer

def run_experiment(prompt):
    coder, reviewer = setup_agents()
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

    results = {}
    for i, prompt_data in enumerate(prompts):
        prompt_copy = prompt_data.copy()
        prompt_result = run_experiment(prompt_copy["Prompt"])
        prompt_copy["Result"] = prompt_result
        results[i] = prompt_copy

    with open('results/test.json', 'w') as f:
        json.dump(results, f, indent=4)