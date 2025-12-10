@echo off
call .venv\scripts\activate
call uv pip install -r requirements.txt

python -u experiment.py ^
    --prompt_file prompts/llm_multiturn_vulnerability_prompts.json ^
    --result_dir results/experiment ^
    --llm_config LLAMA_CONFIG_LIST ^
    --max_workers 10 ^
    --max_turns 10 ^
    --semgrep_rag ^
    --bandit_rag ^
    --provide_deps ^
    > execution.log 2>&1

call deactivate