#!/bin/bash
set -e

# activate venv
source .venv/bin/activate

# install deps
pip install -r requirements.txt

# run experiment
python -u experiment.py \
    --prompt_file prompts/test.json \
    --result_dir results \
    --llm_config LLAMA_CONFIG_LIST \
    --max_workers 1 \
    --max_turns 10 \
    --semgrep_rag \
    --bandit_rag \
    > execution.log 2>&1

deactivate
