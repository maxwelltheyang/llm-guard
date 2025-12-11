import json
from collections import defaultdict, OrderedDict
from pathlib import Path

with open("../prompts/llm_multiturn_vulnerability_prompts.json") as f:
    prompts = json.load(f)

# Get all scenario-prompt combinations from prompts file
all_scenario_prompts = set()
for prompt in prompts:
    scenario = prompt.get("ScenarioNumber", "")
    prompt_num = prompt.get("PromptNumber", "")
    if scenario and prompt_num:
        all_scenario_prompts.add(f"{scenario}-{prompt_num}")

with open("exp_codeql.sarif") as f:
    sarif = json.load(f)

runs = sarif["runs"]
# Structure: nested_summary[model][scenario-prompt] = count
nested_summary = defaultdict(lambda: defaultdict(int))

for run in runs:
    for result in run["results"]:
        rule = result["ruleId"]
        message = result["message"]["text"]
        location = result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]

        parts = Path(location).parts
        
        # Find model, scenario, and prompt from path
        # Path structure: results/timestamp/scenario_X.X/prompt_Y/code/file.py
        model = None
        scenario_dir = None
        prompt_dir = None
        
        for i, part in enumerate(parts):
            if part.startswith("scenario_"):
                scenario_dir = part.replace("scenario_", "")
                # Model is typically the parent directory of scenario
                if i > 0:
                    model = parts[i-1]
            elif part.startswith("prompt_"):
                prompt_dir = part.replace("prompt_", "")
        
        if scenario_dir and prompt_dir:
            scenario_prompt_key = f"{scenario_dir}-{prompt_dir}"
            if model:
                nested_summary[model][scenario_prompt_key] += 1

# Build summary grouped by model
summary = OrderedDict()
for model in sorted(nested_summary.keys()):
    model_data = OrderedDict()
    
    # Add counts for each scenario-prompt combination (0 if no vulnerabilities)
    for scenario_prompt in sorted(all_scenario_prompts):
        model_data[scenario_prompt] = nested_summary[model].get(scenario_prompt, 0)
    
    model_data["total"] = sum(model_data.values())
    model_data["files_with_vulns"] = sum(1 for count in model_data.values() if count > 0 and count != model_data["total"])
    summary[model] = model_data

with open("exp_codeql_vulnerability_summary.json", "w") as f:
    json.dump(summary, f, indent=4)
