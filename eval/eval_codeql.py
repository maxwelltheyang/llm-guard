import json
from collections import defaultdict, OrderedDict
from pathlib import Path

with open("../prompts/llm_multiturn_vulnerability_prompts.json") as f:
    prompts = json.load(f)

all_scenarios = set()
for prompt in prompts:
    scenario = prompt.get("ScenarioNumber", "")
    prompt_number = prompt.get("PromptNumber", "")
    if scenario:
        all_scenarios.add(f"{scenario}-{prompt_number}")

with open("python.sarif") as f:
    sarif = json.load(f)

runs = sarif["runs"]
nested_summary = defaultdict(lambda: defaultdict(int))

for run in runs:
    for result in run["results"]:
        rule = result["ruleId"]
        message = result["message"]["text"]
        location = result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]

        path = Path(location)
        directory = path.parent.name if path.parent.name else "root"
        filename = path.stem

        nested_summary[directory][filename] += 1

summary = {}
for directory in sorted(nested_summary.keys()):

    dir_dict = OrderedDict()
    for scenario in sorted(all_scenarios):
        dir_dict[scenario] = nested_summary[directory].get(scenario, 0)
    
    dir_dict["total"] = sum(dir_dict.values())
    summary[directory] = dir_dict

with open("codeql_vulnerability_summary.json", "w") as f:
    json.dump(summary, f, indent=4)
