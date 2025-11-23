@echo off
call .venv\Scripts\activate
call uv pip install -r requirements.txt

python -u experiment.py ^
    --prompt_file prompts/test.json ^
    --result_dir results ^
    --llm_config OAI_CONFIG_LIST ^
    --max_workers 1 ^ 
    --max_turns 10 > execution.log 2>&1

call deactivate