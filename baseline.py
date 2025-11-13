from ollama import chat
import json
from prompts import BASELINE_PROMPT

def baseline(prompt):
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

if __name__ == '__main__':
    with open('prompts/llm_multiturn_vulnerability_prompts.json', 'r') as f:
        prompts = json.load(f)

    results = {}
    for i, prompt_data in enumerate(prompts):
        prompt_copy = prompt_data.copy()
        prompt_result = baseline(prompt_copy["Prompt"])
        prompt_copy["Result"] = prompt_result
        results[i] = prompt_copy

    with open('results/llama3_baseline_multiturn_results.json', 'w') as f:
        json.dump(results, f, indent=4)
