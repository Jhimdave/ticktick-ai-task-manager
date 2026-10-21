
# Python and FastAPI Project Instructions

## 1. General Working Rules

- Read the existing code, project structure, README, dependencies and configuration before making changes.
- Understand how the current implementation works before proposing a solution.
- Make the smallest reliable change that solves the actual problem.
- Preserve existing functionality unless the requested task requires changing it.
- Do not rewrite working code, rename files, delete code or change public APIs without a valid reason.
- For architecture changes, dependency changes or changes involving three or more files, explain the plan and wait for my approval before editing.
- For small, targeted changes, implement the fix and explain it afterward.
- Never invent API endpoints, parameters, configuration values or library methods.
- Ask for missing critical information instead of guessing.

## 2. Object-Oriented Programming

- Prefer OOP for business logic, task processing, service classes, external API clients and components that own state or behavior.
- Use classes with clear responsibilities instead of putting all application logic in main.py.
- Keep FastAPI route handlers thin. Validate requests, call the appropriate service and return a response.
- Use Pydantic models for request validation and response schemas where appropriate.
- Use dependency injection for services and external clients when it improves testability and maintainability.
- Avoid global mutable state and tightly coupled components.
- Do not create unnecessary classes for simple, stateless operations just to satisfy OOP.

## 3. Code Style and Formatting

- Prefer compact, readable Python code.
- Keep function calls, argument lists, parameter lists and other parenthesized expressions on one line whenever the complete line is reasonably short, ideally no more than 120 characters.
- Do not put every argument on a separate line just for formatting purposes.
- Avoid unnecessary line breaks, blank lines and excessive vertical spacing.
- Keep short lists and function calls on one line when readable.
- For longer dictionaries, use multiple lines inside curly braces when that improves readability.
- Break long expressions only when necessary for readability, syntax or the project's established formatter.
- Preserve the existing project's formatting conventions unless they conflict with these rules.
- Do not reformat unrelated files or run a formatter across the entire project without approval.
- Use descriptive names, type hints and focused functions.
- Follow Python naming conventions and maintain consistent formatting across modified files.

## 4. Architecture and Separation of Responsibilities

- Keep application startup and route registration in main.py.
- Keep HTTP endpoints in the API routes layer.
- Keep business logic in service classes.
- Keep external API communication in dedicated client classes.
- Keep request and response validation in schemas.
- Keep environment-based settings in the configuration layer.
- Avoid circular imports and unnecessary dependencies between layers.
- Adapt this structure to the existing project instead of moving all files at once.

## 5. FastAPI, Async and Error Handling

- Use async endpoints and asynchronous clients when the underlying operations support them.
- Do not block the event loop with avoidable synchronous network operations.
- Configure appropriate HTTP timeouts and check external API responses.
- Handle network errors, validation failures and expected API errors explicitly.
- Do not silently swallow exceptions or return success when an operation failed.
- Return appropriate HTTP status codes and useful error messages without exposing secrets.
- Reuse external clients appropriately and ensure their lifecycle is managed correctly.
- Keep task-creation operations testable independently of HTTP route handlers.

## 6. Configuration and Security

- Read credentials, API tokens and sensitive settings from environment variables.
- Never hardcode, print or commit real secrets.
- Keep .env in .gitignore and provide a sanitized .env.example when needed.
- Never overwrite existing environment variables or configuration without explaining the impact.
- Avoid adding dependencies unless they solve a real requirement.
- Check the installed library version and existing project configuration before using unfamiliar APIs.

## 7. Change Tracking and Documentation

- Update docs/AI_CHANGELOG.md after every meaningful code change.
- Create the changelog if it does not exist.
- Add the newest entry at the top.
- Include the date, task summary, files changed, reasons for each change, tests performed, and any risks or follow-up steps.
- Explain what changed and why, file by file.
- Keep the explanation brief and focus on changed functions, classes and important logic.
- Do not claim a file was changed unless it was actually modified.
- Do not claim a test passed unless it was actually executed and passed.
- Never create a Git commit automatically.

## 8. Testing and Validation

- Inspect existing tests and test commands before adding new tooling.
- Add or update focused tests when changing important business logic.
- Test success cases and relevant failure cases.
- Run the appropriate tests and checks when possible.
- Report commands that were executed and their actual results.
- Clearly identify tests that were not run and explain why.
- Do not make unrelated changes to fix an unrelated test failure without approval.

## 9. Required Final Response After Code Changes

Always provide:

1. Summary: What was implemented or fixed.
2. Files changed: Each file and a brief explanation of what changed and why.
3. Important logic: Explain significant changes to functions, classes or API flow.
4. Testing: Commands executed and their actual results.
5. Risks or next steps: Mention remaining issues, assumptions or manual setup required.

Do not provide a long explanation of every unchanged line. Focus on meaningful changes and their purpose.
