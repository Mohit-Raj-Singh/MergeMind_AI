import fnmatch
import json
from pathlib import Path

from github import Auth, Github
from github.PullRequest import PullRequest

from ..models import InlineComment, ReviewResult, Severity

SEVERITY_EMOJI = {
    Severity.ERROR: "🔴",
    Severity.SECURITY: "🚨",
    Severity.WARNING: "🟡",
    Severity.INFO: "🔵",
}


class GitHubClient:
    def __init__(self, token: str, repository: str, event_path: str):
        self.gh = Github(auth=Auth.Token(token))
        self.repo = self.gh.get_repo(repository)
        self.pr = self._load_pr(event_path)

    def _load_pr(self, event_path: str) -> PullRequest:
        event = json.loads(Path(event_path).read_text())
        pr_number = event["pull_request"]["number"]
        return self.repo.get_pull(pr_number)

    def get_diff(self, ignore_patterns: list[str]) -> str:
        """Fetch the PR diff, filtering out ignored paths."""
        files = self.pr.get_files()
        chunks = []
        for f in files:
            if any(fnmatch.fnmatch(f.filename, pat) for pat in ignore_patterns):
                continue
            if f.patch:
                chunks.append(f"--- a/{f.filename}\n+++ b/{f.filename}\n{f.patch}")
        return "\n\n".join(chunks)

    def post_summary(self, result: ReviewResult) -> None:
        """Post a top-level PR review comment with the summary."""
        flags = ""
        if result.summary.security_flags:
            flags = "\n".join(f"- {s}" for s in result.summary.security_flags)
            flags = f"\n\n### 🚨 Security flags\n{flags}"

        highlights = "\n".join(f"- {h}" for h in result.summary.highlights)
        issues = "\n".join(f"- {i}" for i in result.summary.issues)

        body = f"""## AI Code Review

{result.summary.overall}

### Highlights
{highlights}

### Issues
{issues}{flags}

---
*Powered by [MergeMind_AI](https://github.com/Mohit-Raj-Singh/MergeMind_AI)*"""

        self.pr.create_issue_comment(body)

    def post_inline_comments(self, comments: list[InlineComment]) -> None:
        """Post inline review comments on specific lines."""
        if not comments:
            return

        review_comments = []

        for c in comments:
            emoji = SEVERITY_EMOJI.get(c.severity, "💬")
            body = f"{emoji} **{c.title}**\n\n{c.body}"
            review_comments.append({
                "path": c.path,
                "line": c.line,
                "body": body,
            })

        if review_comments:
            self.pr.create_review(
                body="",
                event="COMMENT",
                comments=review_comments,  # type: ignore[arg-type]
            )
