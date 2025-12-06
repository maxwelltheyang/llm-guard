from ollama import chat
import json
from prompts import BASELINE_PROMPT
from openai import OpenAI
from experiment import extract_code_block, write_code_file
from pathlib import Path
import concurrent.futures

with open("OAI_CONFIG_LIST", "r") as f:
    oai_config_list = json.load(f)

client = OpenAI(api_key=oai_config_list[0]["api_key"])


def baseline_llama(prompt):
    response = chat(model='llama3.1', messages=[
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

    def process_prompt(args):
        i, prompt_data = args
        prompt_copy = prompt_data.copy()
        prompt_result = baseline_llama(prompt_copy["Prompt"])
        code, ext = extract_code_block(prompt_result)
        dest_path = Path(f'results/baseline/llama/{prompt_copy["ScenarioNumber"]}.{ext}')
        write_code_file(code, dest_path)
        prompt_copy["Result"] = code
        return i, prompt_copy

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_prompt, (i, prompt_data)) for i, prompt_data in enumerate(prompts)]
        for future in concurrent.futures.as_completed(futures):
            i, prompt_copy = future.result()
            results[i] = prompt_copy

    with open('results/baseline/llama3.1_baseline.json', 'w') as f:
        json.dump(results, f, indent=4)
