from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FIELDS = (
    "**创建日期**",
    "**最后更新**",
    "**状态**",
    "**topic-id**",
    "AI-TASK-QUEUE",
)


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def topic_readmes(root: Path) -> list[Path]:
    return sorted((root / "docs" / "changes_topic" / "roadmap").glob("*/*/README.md"))


def extract_topic_id(text: str, fallback: str) -> str:
    match = re.search(r"\*\*topic-id\*\*：\s*([A-Za-z0-9\-_]+)", text)
    return match.group(1) if match else fallback


def validate_topic_readme(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    topic_name = path.parent.name

    for field in REQUIRED_FIELDS:
        if field not in text:
            failures.append(f"缺少字段 {field}")

    if topic_name == "nautilus-ctp-adapter-mainline":
        return failures

    header_match = re.search(r"^\|\s*顺序\s*\|(.+)\|$", text, flags=re.MULTILINE)
    if header_match is None:
        failures.append("缺少 Child Change 表头 | 顺序 |")
    elif "状态" not in header_match.group(1):
        failures.append("Child Change 表头缺少 状态 列")

    return failures


def validate_repo_sync(root: Path) -> list[str]:
    failures: list[str] = []
    agents_text = (root / "AGENTS.md").read_text(encoding="utf-8")
    docs_index_text = (root / "docs" / "README.md").read_text(encoding="utf-8")
    topic_index_text = (root / "docs" / "changes_topic" / "README.md").read_text(encoding="utf-8")

    active_topic_match = re.search(r"Current topic roadmap: \[(.+?)\]\((.+?)\)", docs_index_text)
    active_change_match = re.search(r"Active change: \[(.+?)\]\((.+?)\)", docs_index_text)
    if active_topic_match is None:
        failures.append("FAIL repo-sync: docs/README.md 缺少 Current topic roadmap")
        return failures
    if active_change_match is None:
        failures.append("FAIL repo-sync: docs/README.md 缺少 Active change")
        return failures

    active_topic_link = active_topic_match.group(2)
    active_change_label = active_change_match.group(1)
    active_change_link = active_change_match.group(2)

    if active_topic_link not in agents_text:
        failures.append("FAIL repo-sync: AGENTS.md step 5 未指向 docs/README.md 当前活动 topic")
    if active_topic_link not in topic_index_text:
        failures.append("FAIL repo-sync: docs/changes_topic/README.md 未指向当前活动 topic")
    if active_change_label not in topic_index_text and active_change_link not in topic_index_text:
        failures.append("FAIL repo-sync: docs/changes_topic/README.md 未反映当前 active change")

    return failures


def main() -> int:
    root = repository_root()
    failures_total = 0
    readmes = topic_readmes(root)

    for readme in readmes:
        text = readme.read_text(encoding="utf-8")
        topic_id = extract_topic_id(text, readme.parent.name)
        failures = validate_topic_readme(readme)
        if failures:
            failures_total += len(failures)
            for failure in failures:
                print(f"FAIL {topic_id}: {failure}")
        else:
            print(f"PASS {topic_id}")

    repo_failures = validate_repo_sync(root)
    failures_total += len(repo_failures)
    for failure in repo_failures:
        print(failure)

    print(f"SUMMARY topics={len(readmes)} failures={failures_total}")
    return 0 if failures_total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
