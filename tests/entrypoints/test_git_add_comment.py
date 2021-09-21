from unittest.mock import MagicMock, patch
from typing import Any
import textwrap

from operatorcert.entrypoints import git_add_comment


@patch("operatorcert.entrypoints.git_add_comment.http.client")
def test_github_add_comment(mock_client: MagicMock, monkeypatch: Any) -> None:
    monkeypatch.setenv("GITHUBTOKEN", "123")
    args = MagicMock()
    args.request_url = "https://github.com/repo/pull/1"
    args.comment_or_file = "demo comment on PR"
    args.test_result = "failure"
    args.comment_file = "false"
    args.old_comment = ""
    args.new_comment = ""

    git_add_comment.github_add_comment(args)
