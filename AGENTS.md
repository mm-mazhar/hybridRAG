## Generative AI Project

### Project Overview

This is a Python project might be using following framewarks or libraries or modules.
*   **Frameworks**: FastAPI, SQLAlchemy, Pydantic, Langchain, Langgraph etc (not limited). Check Note with (*) sign.
*   **Database**: PostgreSQL, any other relational or non-relational database (not limited). Check Note with (*) sign.
*   **Git:** Canonical rules live in **`.agents/rules/git.md`**. Agents MUST follow that file for branch names, commit messages, staging, and PRs. See **Git conventions** below.
*   **Package Manager**: This project uses `uv` for dependency management. Never use bare python or pip commands. Always prefix Python commands with `uv run`:
    - ALWAYS INSTALL development related with `--dev` flag, e.g. uv add --dev pytest black ruff
    - ALWAYS use `uv` as package manager even if `SKILLS.md` file says otherwise.
*   **Architecture**: Follow the following project structure.

* Note: * Look in the `pyproject.toml` file. If module/lib is installed or BASED ON TASK TYPE/s (You may need to install revelant packages or modules or libraries using `uv` as package manager), ALWAYS first check the `SKILLS` or `POWER/INSTALLED` OR `Powers` FOLDER in `.agent` or `.agents` or `.claude`, `.codex`, `.kilocode`, `.kiro`, `.trae` folders for the corresponding skills/Power and follow the instructions or `SKILL.md` of that `skill` or `Power`. (FIRE IMMEDIATELY WHEN MATCHED).
* **IMPORTANT NOTE:** Skills might also be installed in IDE, so always check for skills. If you don't find skills installed, then let the user know.
---

### Project File Structure Tree
```
`generative_ai_project/`
├── `config/`
│   ├── ! `model_config.yaml`
│   └── ! `logging_config.yaml`
├── `data/`
│   ├── `cache/`
│   ├── `embeddings/`
│   └── `vectordb/`
├── `src/`
│   ├── `core/`
│   │   ├── `base_llm.py`
│   │   ├── `gpt_client.py`
│   │   ├── `claude_client.py`
│   │   ├── `local_llm.py`
│   │   └── `model_factory.py`
│   ├── `prompts/`
│   │   ├── `templates.py`
│   │   └── `chain.py`
│   ├── `rag/`
│   │   ├── `embedder.py`
│   │   ├── `retriever.py`
│   │   ├── `vector_store.py`
│   │   └── `indexer.py`
│   ├── `processing/`
│   │   ├── `chunking.py`
│   │   ├── `tokenizer.py`
│   │   └── `preprocessor.py`
│   └── `inference/`
│       ├── `inference_engine.py`
│       └── `response_parser.py`
├── tests/
│   ├── unit/
│   │   ├── test_processor.py
│   │   └── test_embedder.py
│   ├── integration/
│   │   └── test_rag_flow.py
│   └── conftest.py
├── `docs/`
│   ├── ⓘ `README.md`
│   └── ⓘ `SETUP.md`
├── `scripts/`
│   ├── $ `setup_env.sh`
│   ├── $ `run_tests.sh`
│   ├── `build_embeddings.py`
│   └── `cleanup.py`
├── `.gitignore`
├── `Dockerfile`
├── `docker-compose.yml`
└── `requirements.txt`
```
---

### Project Directory and File Descriptions

#### **Directory: config/**
* `config/` - Project configuration files.
    * `model_config.yaml` - LLM providers, models, & parameters.
    * `logging_config.yaml` - Logging setup and levels.

#### **Directory: data/**
* `data/` - Project data and generated data storage.
    * `cache/` - Cached responses and intermediates.
    * `embeddings/` - Generated vector embeddings.
    * `vectordb/` - Vector database indexes (FAISS, Chroma, etc.).

#### **Directory: src/**
* `src/` - Source code for all project components.

    #### **Sub-Directory: core/**
    * `core/` - LLM abstraction and integrations.
        * `base_llm.py` - Common LLM interface.
        * `gpt_client.py` - OpenAI GPT client.
        * `claude_client.py` - Anthropic Claude client.
        * `local_llm.py` - Local/self-hosted models.
        * `model_factory.py` - Model selection factory.

    #### **Sub-Directory: prompts/**
    * `prompts/` - Manage prompt-related components.
        * `templates.py` - Reusable prompt templates.
        * `chain.py` - Multi-step prompt chaining.

    #### **Sub-Directory: rag/**
    * `rag/` - Retrieval-Augmented Generation components.
        * `embedder.py` - Embedding generation.
        * `retriever.py` - Document retrieval.
        * `vector_store.py` - Vector DB interface.
        * `indexer.py` - Document indexing.

    #### **Sub-Directory: processing/**
    * `processing/` - Text processing and data handling.
        * `chunking.py` - Text splitting.
        * `tokenizer.py` - Tokenization utilities.
        * `preprocessor.py` - Cleaning and normalization.

    #### **Sub-Directory: inference/**
    * `inference/` - Logic for model inference.
        * `inference_engine.py` - Inference orchestration.
        * `response_parser.py` - Output parsing and formatting.

   #### **Description: tests/**
   * `tests/` - Contains all automated tests to ensure code quality and model output consistency.

     * `unit/` - Tests for individual units of code (e.g., checking if the chunking.py correctly splits text).

    * `integration/` - High-level tests that check if components work together (e.g., testing the full flow from user query to RAG retrieval to LLM response).

   * `conftest.py` - A standard file for pytest to define shared fixtures (like a mock LLM client so you don't spend money running tests).

    keep the `run_tests.sh` in `scripts/` folder, which would now point directly to this new directory:
     - `scripts/run_tests.sh` - Executes `pytest tests/` and generates coverage reports.

#### **Directory: docs/**
* `docs/` - Documentation.
    * `README.md` - Overview and usage.
    * `SETUP.md` - Installation and setup.

#### **Directory: scripts/**
* `scripts/` - Shell and utility scripts.
    * `setup_env.sh` - Environment setup.
    * `run_tests.sh` - Test execution.
    * `build_embeddings.py` - Embedding generation.
    * `cleanup.py` - Cleanup tasks.

#### **Section: Root Files**
* **Root Files** - Configuration files at the root of the project.
    * `.gitignore` - Git exclusions.
    * `Dockerfile` - Container configuration.
    * `docker-compose.yml` - Multi-service setup.
    * `requirements.txt` - Dependencies.

---

### 📝 Code Conventions & Style

**Use** `SKILLS.md` of `modern-python`, `python-anti-patterns`, `python-configuration`, `python-observability`, `python-resource-management`, `python-type-safety`, `pydantic` in `skills` or `powers/installed` folders of `.agent` or `.agents` folders


**General Standards**

* **PEP 8**: Follow standard Python styling.
* **Type Hinting**: Mandatory for all function signatures (especially in utility files).
* **Complexity**: Avoid deep nesting. If a function goes beyond two levels of nesting, refactor it.

**Naming & Documentation**

* **Functions/Variables**: `snake_case`
* **Classes**: `PascalCase`
* **Docstrings**: Use the Google Python Style Guide format.

**Bad Example:**
```
def my_function(some_parameter):
    if some_parameter == 'value':
        print(some_parameter)
        return some_parameter
```

**Corrected Example:**
```
def my_function(some_parameter: str) -> None:
    """Prints values if parameter matches.

    Args:
        some_parameter: The string to validate.
    """
    if some_parameter != 'value':
        return

    for i in range(10):
        _process_value(i)

def _process_value(i: int) -> None:
    if i > 5:
        print(i)
```

---

### 🔒 Security Considerations

**1. SQL Injection**: Always use SQLAlchemy's parameterized queries.
**2. Input Sanitization**: Validate all user prompts before processing to prevent prompt injection.
**3. Data Privacy**: Never log PII (Personally Identifiable Information) or sensitive API keys.
**4. Trigger `Skill.md` of `security-patterns` in `skills` or `powers/installed` folders of `.agent` or `.agents` folders

---

### 🧪 Testing Instructions

**Use** `SKILLS.md` of `python-testing-patterns`, `pytest` in `skills` or `powers/installed` folders of `.agent` or `.agents` folders

* **Execution**: Run all tests via `uv run pytest`.
* **Specific Tests**: `uv run pytest tests/unit/test_processor.py`.
* **Preference**: * Use `assert` statements directly.
  * Favor `@pytest.mark.parametrize` for testing multiple input scenarios.
  * Ensure `scripts/run_tests.sh` is updated when new test modules are added.

---

## 🛠️ Agent Skill Summary

| Name | Notes |
| :--- | :--- |
| **uv-package-manager** | Modern Python dependency management. |
| **security-patterns** | AI security and safety best practices. |
| **elevenlabs-tts** | High-quality text-to-speech integration. |
| **deepgram-sdk-patterns** | Optimized audio-to-text AI patterns. |
| **openai-docs** | Official OpenAI API documentation. |
| **airtable-automation** | Airtable API and workflow automation. |
| **gemini-live-api-dev** | Real-time multimodal Gemini API logic. |
| **gemini-interactions-api** | Conversational Gemini API patterns. |
| **gemini-api-dev** | Core Google Gemini API development. |
| **livekit-agents** | Real-time voice agent orchestration. |
| **Error Handling** | Robust Python exception management. |
| **Anti Patterns** | Common coding pitfalls to avoid. |
| **Testing Patterns** | Python testing strategies and mocks. |
| **Type Safety** | Type hints and static analysis logic. |
| **Python SDK** | AI application SDK for 150+ models. |
| **Python-observability** | Monitoring, logs, and telemetry logic. |
| **Python-configuration** | Standardized config management patterns. |
| **async-python-patterns** | Concurrency and asyncio best practices. |
| **fastapi-python** | High-performance web API development. |
| **Python Resource Management** | Context managers and memory safety. |
| **modern-python** | Latest Python 3.11+ features and syntax. |
| **langchain-fundamentals** | Core LangChain concepts and objects. |
| **langchain-rag** | Retrieval-Augmented Generation flows. |
| **langchain-middleware** | Request/Response interceptors for agents. |
| **langchain-dependencies** | Third-party service integrations. |
| **deep-agents-memory** | Advanced state and history persistence. |
| **langgraph-fundamentals** | State machine agent orchestration. |
| **langgraph-persistence** | Checkpointing and graph state saving. |
| **langgraph-human-in-the-loop** | Interactive agent-human workflows. |
| **deep-agents-orchestration** | Complex multi-agent coordination. |
| **framework-selection** | Logic for choosing AI toolsets. |
| **web-research** | Search, scraping, and info gathering. |
| **django-expert** | Django-based AI plugin integration. |
| **django-patterns** | Standard Django enterprise patterns. |
| **pydantic** | Data validation and JSON parsing. |
| **flask-expert** | Flask application development expert. |
| **fastmcp** | Model Context Protocol implementation. |
| **pytest** | Standard Python testing framework. |
| **supabase-python** | Supabase database integration. |
| **security-patterns** | Common security patterns. |
| **pi-planning-with-files** | Project planning and file management. |

---

## Git conventions

See **`.agents/rules/git.md`** for the full canonical rules (commit format, branch naming, staging, PRs, changelog). Agents MUST follow that file for any git, branch, commit, or PR work.

- Never commit directly to `main` / `master`. Create `<type>/<description>` first.
- Stage specific files only — never `git add -A` or `git add .`.
- Never commit `.env` or secrets. Never skip hooks (`--no-verify`).
- PR title uses the same conventional-commit format as commits (squash-merge uses that title on `main`).
- `main` only advances through squash-merged PRs (`protect_main` ruleset). Required checks: `Lint`, `Types`, `Tests`.
- Do not commit or push unless the user asks. When they do, follow `.agents/rules/git.md` exactly.

---

## Phase 0 - Intent Gate

- Trigger Skill or Powers (fire IMMEDIATELY when matched):
- Look in the `pyproject.toml` file. If module/lib is installed or BASED ON TASK TYPE/s, ALWAYS check the `SKILLS` or `POWER/INSTALLED` OR `Powers` FOLDER in `.agent` or `.agents` or `.claude`, `.codex`, `.kilocode`, `.kiro`, `.trae` folders for the corresponding skills/Power and follow the instructions or `SKILL.md` of that `skill` or `Power`.

### Step 1: Classify Request Type

| Type | Signal | Action |
|------|--------|--------|
| **Trivial** | Single file, known location, direct answer | Direct tools only |
| **Explicit** | Specific file/line, clear command | Execute directly |
| **Exploratory** | "How does X work?", "Find Y" | Use available search tools |
| **Open-ended** | "Improve", "Refactor", "Add feature" | **Consult `AGENTS.md` first** |
| **Ambiguous** | Unclear scope, multiple interpretations | Ask ONE clarifying question |

---

## Phase 1 - Codebase Assessment

1. Check config files: linter, formatter, type config.
2. Sample 2-3 similar files for consistency.
3. If codebase appears undisciplined, verify before assuming.
4. ALWAYS plan first: **Use** `SKILLS.md` of `pi-planning-with-files` in `skills` or `powers/installed` folders of `.agent` or `.agents` folders

---

## Phase 2 - Research & Implementation

### Research ("Librarian" & "Explore" Concepts)
**Goal**: Zero Assumptions. Data over guesses.

1.  **External Docs (Librarian)**:
    *   **CHECK FIRST**: Do I have an MCP tool for this? (e.g., `openai`, `google gemini`, `livekit`, `stripe` `supabase`, `langchain`, `langraph`, `supabase-docs` etc).
    *   **Action**: Use the available MCP or MCPs to fetch specific API references (e.g., `openai`, `google gemini`, `livekit`, `stripe` `supabase`, `langchain`, `langraph`, `supabase-docs` etc).
    *   **Fallback**: If no MCP, perform a targeted web search or you may use `ref` or `context7` mcp servers (whichever is available, and prefer to use `ref` mcp server).
    *   **Constraint**: NEVER guess APIs for Stripe, Supabase, Langchain, Langraph, pydantic, fastmcp, langgraph, fastapi, flask, django, openai, google-genai, genai  etc.

2.  **Internal Context (Explore)**:
    *   **Trigger**: Touching 2+ modules or unfamiliar code.
    *   **Action**: Use search tools (`grep`, `ls`, or semantic search MCPs [hint: mostly we will be working on windows system] to map dependencies).
    *   **Constraint**: Do not edit a file without reading its imports and usage first.

### Implementation Rules
1.  **Plan**: If task has 2+ steps → Create todo list IMMEDIATELY.
2.  **Style**: Match existing patterns (if disciplined).
3.  **Safety**: Fix minimally. NEVER refactor while fixing a bug.

---

## Phase 3 - Completion

A task is complete when:
- [ ] All planned todo items marked done
- [ ] Diagnostics clean on changed files
- [ ] User's original request fully addressed
- [ ] Any git/PR work followed `.agents/rules/git.md`

</Behavior_Instructions>

<Constraints>

## Hard Blocks (NEVER violate)
| Constraint | No Exceptions |
|------------|---------------|
| Type error suppression (\`as any\` ) | Never |
| Speculate about unread code | Never |
| Leave code in broken state | Never |

## Soft Guidelines
- Prefer existing libraries over new dependencies.
- Prefer small, focused changes over large refactors.
- **Git/PRs**: Follow `.agents/rules/git.md`. Do not commit or push unless the user asks. When they ask, never commit to `main`, never `git add -A`, never `--no-verify`.