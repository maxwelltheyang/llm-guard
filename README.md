# LLM-Guard

With Large Language Model (LLM) innovation speeding up rapidly, it is important to address security issues regarding generative or agentic outputs. Giving AI no guardrails and protections leaves the door open for various mistakes and vulnerabilities. We introduce LLM-Guard, an AI agent that continuously checks model outputs and verifies that the code outputs are legitimate and safe.

## Motivation

Large Language Models (LLMs) are capable of writing working code, however it is not rare that the code they generate **unwittingly introduce security vulnerabilities, risks, and defects** in various contexts. Despite this issue, no existing work currently leverages additional LLMs themselves as a method of *continuously auditing* an LLM's code during its conversations with the user. As such, we seek to answer the question: 

**_Can an LLM moderator improve the security of interactive, multi-domain code generation?_**

We seek to answer this question by building a pipeline where one LLM (**LLM1**) acts as a **code generation assistant** for user-given tasks, then another LLM (**LLM2**) will act as a **security reviewer and assistant** to examine the generated code for weaknesses. If issues are flagged, then LLM2 will alert LLM1 of them as well as possibly suggest fixes and LLM1 will then proceed to regenerate the output, *iterating until either LLM2 approves of the code, or a time or iteration limit we impose is reached*. 

This system will be evaluated across several domains from web apps to low level C code and measure how the **vulnerability count changes relative to an unmoderated baseline**. The main metrics we would like to measure are:

1. **Effectiveness**: How many vulnerabilities remain after moderation
2. **Efficiency**: How effectiveness is affected by the amount of iterations allowed  
3. **Versatility**: How effectiveness varies across task domains

We hypothesize that *iterative review-regeneration will lower the final vulnerability rate*, at the cost of additional time, and that performance will depend on the task complexity and LLM capability.

## Experiments

put something here later

## Setup
### Prerequisites

- **Python 3.10+** (tested with 3.12)
- **Ollama** (for Llama models) - [Install Ollama](https://ollama.ai)
- **Semgrep** - `pip install semgrep`
- **Bandit** - `pip install bandit`
- **OpenAI API Key** (for GPT models)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/maxwelltheyang/llm-guard.git
   cd llm-guard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Configure API Keys**
   Create `OAI_CONFIG_LIST` file for OpenAI:
   ```json
   [
     {
       "model": "gpt-4o",
       "api_key": "sk-YOUR-API-KEY-HERE"
     }
   ]
   ```

   Create `LLAMA_CONFIG_LIST` file for local models:
   ```json
   [
     {
       "model": "llama3.1",
       "api_type": "ollama",
       "base_url": "http://localhost:11434" //or whatever port your local models are hosted on
     }
   ]
   ```

5. **Pull Ollama models** (if using Llama/DeepSeek)
   ```bash
   ollama pull llama3.1
   ollama pull deepseek-coder-v2
   ```

## Usage

### Using Run Scripts (Recommended)

The project includes convenient run scripts for both Unix and Windows systems.

#### Linux/macOS

```bash
chmod +x run.sh
./run.sh
```

The `run.sh` script will:
- Activate the virtual environment
- Install/update dependencies
- Run the experiment with default settings
- Log output to `execution.log`

#### Windows

```cmd
run.bat
```

The `run.bat` script performs the same steps for Windows environments.

### Manual Execution

#### Run Baseline Tests

Test raw LLM output without review:

```bash
python baseline.py
```

This will:
- Process all prompts in `prompts/llm_vulnerability_prompts.json`
- Generate code using the default model (Llama 3.1)
- Save results to `results/baseline/`

#### Run Multi-Agent Experiments

Full experiment with iterative review:

```bash
python experiment.py \
    --prompt_file prompts/test.json \
    --result_dir results \
    --llm_config LLAMA_CONFIG_LIST \
    --max_workers 1 \
    --max_turns 10 \
    --semgrep_rag \
    --bandit_rag
```

**Arguments:**
- `--prompt_file`: JSON file containing test prompts (default: `prompts/test.json`)
- `--result_dir`: Directory to save results (default: `results`)
- `--llm_config`: Path to LLM config file (default: `LLAMA_CONFIG_LIST`)
- `--max_workers`: Number of parallel workers (default: 1)
- `--max_turns`: Maximum review iterations per prompt (default: 10)
- `--semgrep_rag`: Enable Semgrep results in Judge feedback
- `--bandit_rag`: Enable Bandit results in Judge feedback (if Python)
- `--provide_deps`: Include dependency suggestions in prompts (if Python)

### Output Structure

Each experiment run creates:
- **Timestamped directory** Per prompt
- **scenario_result.json**: Full conversation transcript
- **prompt_i.py**: Final generated code
- **requirements.txt**: Modules pertinent to the generated code (if the file is .py)
- **prompt_temp_turn_j.py**: Temporary code files during the agent's workflow
- **prompt_i_conversation.json**: Coder and judge conversation history

### Analyzing Results

After running experiments, use the following tools to analyze the generated code for vulnerabilities:

#### Using Metis (AI-Powered Code Analysis)

[Metis](https://github.com/arm/metis) is an AI-powered code understanding tool that can analyze your generated code.

1. **Install Metis**:
   ```bash
   pip install git+https://github.com/arm/metis.git
   ```

2. **Configure Metis** (create `metis.yml` in project root):
   ```yaml
   metis_engine:
     metisignore_file: .metisignore
   
   llm_provider:
     name: "ollama"
     model: "llama3.1"
     base_url: "http://localhost:11434/v1"
     code_embedding_model: "all-minilm"
     docs_embedding_model: "all-minilm"
   ```

3. **Pull required Ollama models**:
   ```bash
   ollama pull llama3.1
   ollama pull all-minilm
   ```

4. **Run Metis on generated code**:
   ```bash
   uv run metis --codebase-path results/experiment
   
   # Or analyze baseline results
   uv run metis --codebase-path results/baseline

   # Run the following commands in once in the metis CLI
   index
   review_code
   ```
   This will create a .json file with relevant results, look in eval/exp_metis_vulnerability_summary.json for a comprehensive example.

#### Using CodeQL (GitHub's Code Analysis)

CodeQL performs deep semantic analysis to find vulnerabilities using GitHub Actions.

1. **Run CodeQL Analysis via GitHub Actions**:
   - The repository includes a CodeQL workflow in `.github/workflows/codeql.yml`
   - Go to your repository: `https://github.com/maxwelltheyang/llm-guard`
   - Click the **Actions** tab
   - Select **CodeQL** workflow from the left sidebar
   - Click **Run workflow** dropdown
   - Select the branch you want to analyze
   - Click **Run workflow**

2. **View Results in GitHub**:
   - Once the workflow completes, go to the **Security** tab
   - Click **Code scanning** in the left sidebar
   - View all detected vulnerabilities with severity levels and descriptions
   - Click on any alert to see:
     - Detailed explanation of the vulnerability
     - Exact code location
     - Suggested fixes
     - Related CWE numbers

3. **Download SARIF Results**:
   - Go to the completed workflow run in the **Actions** tab
   - Scroll down to the **Artifacts** section
   - Download the **codeql-results** artifact (contains the SARIF file)
   - Extract the `.sarif` file from the downloaded zip

4. **Analyze specific directories**:
   To analyze specific result directories (like `results/baseline`), modify the workflow file to scan that path:
   ```yaml
   # In .github/workflows/codeql.yml
   - name: Perform CodeQL Analysis
     uses: github/codeql-action/analyze@v3
     with:
       category: "/language:python"
       paths: "results/baseline"  # Add this line
   ```

#### Using Evaluation Scripts

Place all relevant json or sarif files in the `eval/` directory. Then run the evaluation scripts in the `eval/` directory to aggregate and analyze results:

```bash
cd eval
# Modify target and output directories in eval files
python eval_codeql.py
# and/or
python eval_metis.py 
```

## Configuration

### Prompt Files

Create custom prompt sets in `prompts/` directory. Format:

```json
[
  {
    "id": 1,
    "Category": "Web Applications & APIs", //optional: for aggregation and tracking
    "ScenarioNumber": 1, //optional: for aggregation and tracking
    "ScenarioTitle": "User Authentication System", //optional: for aggregation and tracking
    "Prompt": "Create a login system with username and password validation."
  }
]
```

### Model Configuration

Modify system prompts in `prompts.py`:
- `BASELINE_PROMPT`: Instructions for baseline tests
- `CODER_PROMPT`: Instructions for the code generation agent
- `JUDGE_PROMPT`: Instructions for the review agent

### Static Analysis

Configure Semgrep rules by changing the config in `experiment.py`:
```python
["semgrep", "--json", "--config", "p/security-audit", target_path]
```

Available rule sets: `p/security-audit`, `p/owasp-top-ten`, `p/cwe-top-25`, etc.

## Acknowledgments

Built with:
- [Autogen](https://github.com/microsoft/autogen) - Multi-agent framework
- [Semgrep](https://semgrep.dev) - Static analysis
- [Bandit](https://bandit.readthedocs.io) - Python security linter
- [Ollama](https://ollama.ai) - Local LLM runtime