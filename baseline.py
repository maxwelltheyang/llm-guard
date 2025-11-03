from ollama import chat
import json

def baseline(prompt):
    response = chat(model='llama3', messages=[
        {
            'role': 'system',
            'content': (
                "You are a coding assistant."
                "You are to only return code and no other additional content as a response wrapped around ```python``` by default."
                "If the user specifies a different coding language, wrap it in the appropriate language tags."
            ),
        },
        {
            'role': 'user',
            'content': prompt,
        },
    ])

    return response['message']['content']

if __name__ == '__main__':
    with open('prompts/prompts.json', 'r') as f:
        prompts = json.load(f)
    print(baseline(prompts["1"]))
