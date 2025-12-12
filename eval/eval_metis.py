import json
from collections import defaultdict, OrderedDict
from pathlib import Path

with open("../prompts/llm_multiturn_vulnerability_prompts.json") as f:
    prompts = json.load(f)

all_scenarios = set()
for prompt in prompts:
    scenario = prompt.get("ScenarioNumber", "")
    if scenario:
        all_scenarios.add(scenario)

index_file = "metis_summary.json"
with open(index_file) as f:
    data = json.load(f)

baseline_summary = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))
experiment_summary = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))

baseline_files_with_vulns = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
experiment_files_with_vulns = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))

for entry in data["reviews"]:
    file_path = entry["file"]
    reviews = entry.get("reviews", [])

    if len(reviews) == 0:
        continue

    parts = Path(file_path).parts

    is_baseline = parts[0] == "baseline"
    
    if is_baseline:
        if len(parts) >= 3:
            model = parts[1]
            filename = parts[2]
            scenario_prompt = Path(filename).stem
            if "-" in scenario_prompt:
                scenario = scenario_prompt.rsplit("-", 1)[0]
                
                baseline_files_with_vulns[model][scenario][scenario_prompt].add(file_path)

                for review in reviews:
                    severity = review.get("severity", "Unknown")
                    baseline_summary[model][scenario][scenario_prompt][severity] += 1
    else:

        if len(parts) >= 4 and parts[0] == "experiment":
            model_dir = parts[1]
            scenario_dir = parts[2]
            
            model = model_dir
            
            if scenario_dir.startswith("scenario_"):
                scenario = scenario_dir.replace("scenario_", "")
            else:
                scenario = scenario_dir

            if len(parts) >= 5 and parts[3].startswith("prompt_"):
                prompt_num = parts[3].replace("prompt_", "")
            else:
                filename = Path(file_path).stem
                if "prompt_" in filename and "_turn_" in filename:
                    prompt_num = filename.split("_turn_")[-1]
                elif "prompt_" in filename:
                    prompt_num = filename.replace("prompt_", "")
                else:
                    prompt_num = "unknown"
            
            scenario_prompt = f"{scenario}-{prompt_num}"

            experiment_files_with_vulns[model][scenario][scenario_prompt].add(file_path)

            for review in reviews:
                severity = review.get("severity", "Unknown")
                experiment_summary[model][scenario][scenario_prompt][severity] += 1

def build_summary_dict(nested_summary, files_with_vulns_dict):
    summary = OrderedDict()
    
    for model in sorted(nested_summary.keys()):
        model_data = OrderedDict()

        all_severities = set()
        for scenario_dict in nested_summary[model].values():
            for prompt_dict in scenario_dict.values():
                all_severities.update(prompt_dict.keys())

        for scenario in sorted(all_scenarios):
            scenario_prompts = nested_summary[model].get(scenario, {})

            for prompt_key in sorted(scenario_prompts.keys()):
                severity_counts = scenario_prompts[prompt_key]
                model_data[prompt_key] = dict(severity_counts)
    
        model_severity_totals = defaultdict(int)
        total_files_with_vulns = set()
        for scenario_dict in nested_summary[model].values():
            for prompt_dict in scenario_dict.values():
                for severity, count in prompt_dict.items():
                    model_severity_totals[severity] += count
        
        for scenario_dict in files_with_vulns_dict[model].values():
            for file_set in scenario_dict.values():
                total_files_with_vulns.update(file_set)
        
        if model_severity_totals:
            model_data["total"] = dict(model_severity_totals)
            model_data["files_with_vulns"] = len(total_files_with_vulns)
        
        summary[model] = model_data
    
    return summary

baseline_final = build_summary_dict(baseline_summary, baseline_files_with_vulns)
experiment_final = build_summary_dict(experiment_summary, experiment_files_with_vulns)

with open("baseline_metis_vulnerability_summary.json", "w") as f:
    json.dump(baseline_final, f, indent=4)

with open("exp_metis_vulnerability_summary.json", "w") as f:
    json.dump(experiment_final, f, indent=4)
