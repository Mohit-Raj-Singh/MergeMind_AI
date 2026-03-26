import asyncio
import sys

from .config import Config
from .git.github import GitHubClient
from .providers import get_provider


async def run() -> None:
    config = Config()

    print(f"[ai-reviewer] Provider: {config.provider} | Model: {config.resolved_model}")
    print(
        f"[ai-reviewer] Review level: {config.review_level} | Security only: {config.security_only}"
    )

    # 1. Fetch diff from GitHub
    gh = GitHubClient(
        token=config.github_token,
        repository=config.github_repository,
        event_path=config.github_event_path,
    )
    diff = gh.get_diff(ignore_patterns=config.ignore_patterns)

    if not diff.strip():
        print("[ai-reviewer] No diff found (all files ignored or empty PR). Skipping.")
        return

    print(f"[ai-reviewer] Diff size: {len(diff)} chars")

    # 2. Run LLM review
    provider = get_provider(config.provider, config.api_key, config.resolved_model)
    result = await provider.review(
        diff=diff,
        review_level=config.review_level,
        security_only=config.security_only,
    )

    print(f"[ai-reviewer] Got {len(result.inline_comments)} inline comments")

    # 3. Post results back to GitHub
    if config.post_summary:
        gh.post_summary(result)
        print("[ai-reviewer] Posted summary comment")

    if config.post_inline and result.inline_comments:
        # Filter to security only if requested
        comments = result.inline_comments
        if config.security_only:
            from .models import Severity
            comments = [c for c in comments if c.severity == Severity.SECURITY]

        gh.post_inline_comments(comments)
        print(f"[ai-reviewer] Posted {len(comments)} inline comments")

    print("[ai-reviewer] Done.")


def main() -> None:
    try:
        asyncio.run(run())
    except Exception as e:
        print(f"[ai-reviewer] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
