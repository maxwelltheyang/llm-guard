#!/bin/bash
set -e

# activate venv
source .venv/bin/activate

# install deps
pip install -r requirements.txt

# run experiment
python -u experiment.py \
    --prompt_file prompts/llm_multiturn_vulnerability_prompts.json \
    --result_dir results \
    --llm_config OAI_CONFIG_LIST \
    --max_workers 10 \
    --max_turns 10 \
    --semgrep_rag \
    --bandit_rag \
    --provide_deps \
    > execution.log 2>&1

deactivate
