import pytest
from typing import Any
from unittest.mock import MagicMock, patch

from operatorcert.entrypoints import marketplace_replication


@patch("operatorcert.entrypoints.marketplace_replication.setup_argparser")
@patch("operatorcert.entrypoints.marketplace_replication.call_ibm_webhook")
def test_main(mock_call_ibm_webhook: MagicMock, mock_arg_parser) -> None:
    marketplace_replication.main()
    mock_call_ibm_webhook.assert_called_once()


@patch(
    "operatorcert.entrypoints.marketplace_replication.webhook_twirp.MirrorServiceClient"
)
def test_marketplace_replication_non_marketplace_repo(mock_mirror_client) -> None:
    args = MagicMock()
    args.git_repo_url = "https://github.com/some-other-repo"

    marketplace_replication.call_ibm_webhook(args)
    mock_mirror_client.assert_not_called()


def test_marketplace_replication_no_token() -> None:
    args = MagicMock()
    args.git_repo_url = (
        "git@github.com/redhat-openshift-ecosystem/redhat-marketplace-operators"
    )

    with pytest.raises(SystemExit):
        marketplace_replication.call_ibm_webhook(args)


@patch(
    "operatorcert.entrypoints.marketplace_replication.webhook_twirp.MirrorServiceClient"
)
def test_marketplace_replication(
    mock_mirror_client: MagicMock, monkeypatch: Any
) -> None:
    args = MagicMock()
    args.git_repo_url = (
        "git@github.com/redhat-openshift-ecosystem/redhat-marketplace-operators-preprod"
    )
    args.package = "test-package"
    args.ocp_version = "v1.1"
    args.bundle_image_digest = "test-image-digest"
    args.bundle_image = "test-image"
    args.version = "test-version"
    monkeypatch.setenv("IBM_WEBHOOK_TOKEN", "123")

    marketplace_replication.call_ibm_webhook(args)
    mock_mirror_client.return_value.NewOperatorBundles.assert_called_once()
