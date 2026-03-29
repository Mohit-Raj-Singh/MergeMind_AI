# AI Code Reviewer

> AI-powered pull request reviews using your own LLM API key. Zero infrastructure, zero cost to you.

[![GitHub Action](https://img.shields.io/badge/GitHub%20Action-v1-purple?logo=github)](https://github.com/Mohit-Raj-Singh/MergeMind_AI)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)

---

## What it does

Add this GitHub Action to any repo and every pull request automatically gets:

- **Inline comments** on specific lines with severity levels (error, warning, info, security)
- **A summary comment** with overall assessment, highlights, and key issues
- **Security flags** for vulnerabilities like hardcoded secrets, injection risks, insecure deps

Your code never leaves GitHub's infrastructure. You bring your own API key.

---

## Quickstart (30 seconds)

**1. Add your API key as a GitHub secret**

Go to your repo → Settings → Secrets → Actions → New repository secret

| Provider | Secret name | Get key |
|---|---|---|
| Anthropic | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| OpenAI | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) |
| Google Gemini | `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) |

**2. Create `.github/workflows/ai-review.yml`**

Pick your provider and paste the matching snippet:

**Anthropic (Claude)**
```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write

    steps:
      - uses: Mohit-Raj-Singh/MergeMind_AI@v1
        with:
          provider: anthropic
          api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

**OpenAI (GPT)**
```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write

    steps:
      - uses: Mohit-Raj-Singh/MergeMind_AI@v1
        with:
          provider: openai
          api_key: ${{ secrets.OPENAI_API_KEY }}
```

**Google Gemini**
```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write

    steps:
      - uses: Mohit-Raj-Singh/MergeMind_AI@v1
        with:
          provider: gemini
          api_key: ${{ secrets.GEMINI_API_KEY }}
```

That's it. Open a PR and the review will appear automatically.

---

## Supported providers & models

| Provider | Default model | Override with |
|---|---|---|
| `anthropic` | `claude-sonnet-4-6` | `claude-opus-4-6`, `claude-haiku-4-5-20251001` |
| `openai` | `gpt-4o` | `gpt-4o-mini`, `gpt-4-turbo` |
| `gemini` | `gemini-2.0-flash` | `gemini-2.0-pro`, `gemini-1.5-flash` |

---

## All configuration options

```yaml
- uses: Mohit-Raj-Singh/MergeMind_AI@v1
  with:
    # Required
    provider: anthropic           # anthropic | openai | gemini
    api_key: ${{ secrets.ANTHROPIC_API_KEY }}

    # Optional
    model: claude-sonnet-4-6      # override default model
    review_level: standard        # quick | standard | thorough
    ignore_paths: "*.md,docs/**,**/package-lock.json"
    post_summary: true            # top-level PR summary comment
    post_inline: true             # inline line-level comments
    security_only: false          # only report security issues
```

### `review_level` explained

| Level | What it does | Best for |
|---|---|---|
| `quick` | Errors and security issues only | Draft PRs, WIP branches |
| `standard` | Bugs, security, important style issues | Most PRs (default) |
| `thorough` | Everything: correctness, performance, style, maintainability | Pre-merge on main |

### `ignore_paths` examples

```yaml
# Ignore generated files, docs, and lock files
ignore_paths: "*.md,docs/**,**/package-lock.json,**/*.generated.*,migrations/**"
```

---

## Example output

### Summary comment

> **AI Code Review**
>
> Overall this PR adds a solid authentication layer. Logic is clean and tests are included.
>
> **Highlights**
> - Clear separation of concerns between auth and user management
> - Good use of async/await throughout
>
> **Issues**
> - Missing rate limiting on the login endpoint
> - Token expiry not validated on refresh
>
> **Security flags**
> - JWT secret falls back to a hardcoded default — must be set via environment variable

### Inline comment example

```
🔴 Missing rate limiting

The /login endpoint has no rate limiting. An attacker can brute-force
credentials without restriction.

Suggested fix:
  from slowapi import Limiter
  limiter = Limiter(key_func=get_remote_address)

  @app.post("/login")
  @limiter.limit("5/minute")
  async def login(request: Request, ...):
      ...
```

---

## FAQ

**Is my code sent to anyone other than my chosen LLM provider?**
No. The action runs on GitHub's own runners. Your code goes directly from GitHub to your chosen LLM API. Nothing passes through any third-party server.

**How much does it cost?**
You pay only for the LLM API calls you make. A typical PR review costs $0.01–$0.05 depending on diff size and model. See your provider's pricing page for details.

**Can I use this on private repos?**
Yes. GitHub Actions work identically on private repos.

**The review posted a comment on the wrong line. Why?**
This can happen on very large diffs where the model loses line number precision. Try `review_level: thorough` or split the PR into smaller chunks.

**Can I add custom review rules?**
Not yet — it's on the roadmap for v1.1. You'll be able to add a `.ai-reviewer.yml` to your repo with custom rules and focus areas.

---

## Contributing

Contributions are welcome! The easiest way to contribute is adding support for a new LLM provider — it takes about 30 lines.

### Adding a new provider

1. Create `src/ai_reviewer/providers/your_provider.py`
2. Implement the `LLMProvider` abstract base class (one method: `review`)
3. Add it to the factory in `src/ai_reviewer/providers/__init__.py`
4. Add it to `action.yml` inputs description and `README.md`
5. Open a PR

### Local development

```bash
git clone https://github.com/Mohit-Raj-Singh/MergeMind_AI
cd MergeMind_AI
pip install -e ".[dev]"
pytest
```

### Running locally against a real PR

```bash
# Set your chosen provider (anthropic | openai | gemini)
export PROVIDER=anthropic
export API_KEY=your-key   # ANTHROPIC_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY
export GITHUB_TOKEN=your-github-token
export GITHUB_REPOSITORY=owner/repo
export GITHUB_EVENT_PATH=/path/to/event.json

python -m ai_reviewer.main
```

---

## Roadmap

- [x] GitHub Actions support
- [x] Anthropic, OpenAI, Gemini providers
- [x] Inline + summary comments
- [x] Security-only mode
- [ ] Custom rules via `.ai-reviewer.yml`
- [ ] GitLab CI support
- [ ] Bitbucket Pipelines support
- [ ] Review history & analytics (opt-in)
- [ ] Diff chunking for very large PRs

---

## License

MIT — see [LICENSE](LICENSE)
