import json
from datetime import datetime
from unittest import mock
from unittest.mock import patch, MagicMock

from operatorcert.entrypoints.create_container_image import (
    check_if_image_already_exists,
    create_container_image,
    prepare_parsed_data,
)


@patch("operatorcert.entrypoints.create_container_image.pyxis.get")
def test_check_if_image_already_exists(mock_get: MagicMock):
    # Arrange
    mock_rsp = MagicMock()
    mock_get.return_value = mock_rsp

    args = MagicMock()
    args.pyxis_url = "https://catalog.redhat.com/api/containers/"
    args.isv_pid = "some_isv_pid"
    args.docker_image_digest = "some_digest"

    # Image already exist
    mock_rsp.json.return_value = {"data": [{}]}

    # Act
    exists = check_if_image_already_exists(args)
    # Assert
    assert exists
    mock_get.assert_called_with(
        "https://catalog.redhat.com/api/containers/v1/images?page_size=1&filter=isv_pid==some_isv_pid"
        ";docker_image_digest==some_digest;not(deleted==true)"
    )

    # Image doesn't exist
    mock_rsp.json.return_value = {"data": []}

    # Act
    exists = check_if_image_already_exists(args)
    # Assert
    assert not exists


@patch("operatorcert.entrypoints.create_container_image.pyxis.post")
@patch("operatorcert.entrypoints.create_container_image.prepare_parsed_data")
@patch("operatorcert.entrypoints.create_container_image.datetime")
def test_create_container_image(
    mock_datetime: MagicMock, mock_prepare_parsed: MagicMock, mock_post: MagicMock
):
    # Arrange
    mock_post.return_value = "ok"
    mock_prepare_parsed.return_value = {"architecture": "ok"}

    # mock date
    mock_datetime.now = MagicMock(return_value=datetime(1970, 10, 10, 10, 10, 10))

    args = MagicMock()
    args.pyxis_url = "https://catalog.redhat.com/api/containers/"
    args.isv_pid = "some_isv_pid"
    args.registry = "some_registry"
    args.repository = "some_repo"
    args.docker_image_digest = "some_digest"
    args.bundle_version = "some_version"

    # Act
    rsp = create_container_image(args)

    # Assert
    assert rsp == "ok"
    mock_post.assert_called_with(
        "https://catalog.redhat.com/api/containers/v1/images",
        {
            "isv_pid": "some_isv_pid",
            "repositories": [
                {
                    "published": True,
                    "registry": "some_registry",
                    "repository": "some_repo",
                    "push_date": "1970-10-10T10:10:10.000000+00:00",
                    "tags": [
                        {
                            "added_date": "1970-10-10T10:10:10.000000+00:00",
                            "name": "some_version",
                        }
                    ],
                }
            ],
            "certified": True,
            "docker_image_digest": "some_digest",
            "architecture": "ok",
            "parsed_data": {"architecture": "ok"},
            "sum_layer_size_bytes": 1,
        },
    )


def test_prepare_parsed_data():
    # Arrange
    file_content = json.dumps(
        {
            "DockerVersion": "1",
            "Layers": ["1", "2"],
            "Architecture": "test",
            "Env": ["a=test"],
        }
    )
    mock_open = mock.mock_open(read_data=file_content)

    # Act
    with mock.patch("builtins.open", mock_open):
        parsed_data = prepare_parsed_data("nonexisting_file.json")

    # Assert
    assert parsed_data == {
        "architecture": "test",
        "docker_version": "1",
        "env_variables": ["a=test"],
        "layers": ["1", "2"],
    }
