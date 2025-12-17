
# AGENTS Configuration

This file defines rules, conventions, and safety constraints for agents running inside Antigravity.

---

## 1. Browser Access Policy (Strict Mode)

### Allowed Domains (Allowlist)
- `localhost`
- `127.0.0.1`
- `::1`

Agents **MAY** access these domains freely for local testing and development.

### Forbidden Domains (Default)
All external domains are **forbidden unless explicitly added to the allowlist**.
Agents **MUST NOT**:
- Access external websites
- Perform web searches
- Interact with authentication flows (Google, GitHub, banking, etc.)
- Open links in non-sandboxed browsers
- Send any request to an unapproved domain

If a task requires external documentation or resources, the agent must:
1. Generate an artifact explicitly requesting permission.
2. Wait for human approval before continuing.

This ensures predictability, privacy, and full control over external interactions.

---

## 2. Execution Safety Rules
- Agents must verify domain permissions before any network call.
- If unsure, agents must assume **not allowed**.
- Dangerous actions (file deletion, environment modification, registry edits) require explicit human approval.
- Agents must break down complex tasks into clear, safe subtasks.
- Logs must be human-readable and describe the reasoning for any impactful action.

---

## 3. Python Coding Style Guide (Readable, Well-Commented Code)
Agents must write Python code that is:
- **Readable**
- **Well-structured**
- **Well-commented**
- **Consistent**

Below is the enforced style guide.

### 3.1. General Principles
- Use Google Python Style Guide (https://google.github.io/styleguide/pyguide.html).
- Prefer clarity over cleverness.
- Write code for humans first, machines second.
- Keep functions short and focused.

### 3.2. Naming Conventions
- Use `snake_case` for variables and functions.
- Use `PascalCase` for classes.
- Use ALL_CAPS for constants.
- Names should describe purpose, not type, e.g.:
  ```python
  def load_user_profile(path):
      ...
  ```

### 3.3. Comments & Documentation
- Every file must start with a short header explaining its purpose.
- Every function must have a docstring following this template:
  ```python
  def my_function(x: int, y: int) -> int:
      """
      Short description of what the function does.

      Args:
          x: Meaning of x.
          y: Meaning of y.

      Returns:
          Meaning of return value.
      """
  ```
- Add inline comments only for non-obvious logic.
  
### 3.4. Code Formatting
Follow PEP 8 unless overridden here.
- Max line length: 100 chars
- Indent with 4 spaces
- One blank line between logical code blocks

### 3.5. Error Handling
Use explicit, descriptive error messages:
```python
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Config file not found: {config_path}")
```
Avoid bare `except:`.

### 3.6. Logging
Use the `logging` module, not print statements, for any agent-generated logs.
```python
import logging
logger = logging.getLogger(__name__)
```

### 3.7. Type Hints
Always include type hints for:
- Function arguments
- Return values
- Complex variables

Example:
```python
def parse_records(records: list[dict[str, str]]) -> list[UserRecord]:
    ...
```

---

## 4. Task Breakdown Requirements
Agents must output a clear, step-by-step plan before executing code.
Each step must:
- Explain what will be done
- Justify why it is safe
- Await approval for anything risky

---

## 5. Git & File System Rules
- Never modify files outside the project directory.
- Commit messages must be descriptive and follow this format:
  ```
  <type>: <short summary>

  <optional detailed description>
  ```
  Example types: `feat`, `fix`, `refactor`, `docs`, `test`.

---


