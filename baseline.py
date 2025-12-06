from ollama import chat
import json
from prompts import BASELINE_PROMPT
from openai import OpenAI
from experiment import extract_code_block, write_code_file

with open("OAI_CONFIG_LIST", "r") as f:
    oai_config_list = json.load(f)

client = OpenAI(oai_config_list[0]["api_key"])


def baseline_llama(prompt):
    response = chat(model='llama3', messages=[
        {
            'role': 'system',
            'content': (
                BASELINE_PROMPT
            ),
        },
        {
            'role': 'user',
            'content': prompt,
        },
    ])

    return response['message']['content']

def baseline_gpt(prompt):
    result = client.responses.create(
        model="gpt-4o",
        instructions=BASELINE_PROMPT,
        input=prompt,
        reasoning={ "effort": "high" },
    )

    return result.output_text

def baseline_deepseek(prompt):
    response = chat(model='deepseek-coder-v2', messages=[
        {
            'role': 'system',
            'content': (
                BASELINE_PROMPT
            ),
        },
        {
            'role': 'user',
            'content': prompt,
        },
    ])

    return response['message']['content']

if __name__ == '__main__':
    with open('prompts/llm_vulnerability_prompts.json', 'r') as f:
        prompts = json.load(f)

    results = {}
    for i, prompt_data in enumerate(prompts):
        prompt_copy = prompt_data.copy()
        prompt_result = baseline_llama(prompt_copy["Prompt"])
        code, _ = extract_code_block(prompt_result)
        write_code_file(code, 'results/baseline/i')
        prompt_copy["Result"] = code
        results[i] = prompt_copy

    with open('results/baseline/llama3.1_baseline.json', 'w') as f:
        json.dump(results, f, indent=4)
