from unittest.mock import patch, MagicMock

from operatorcert.entrypoints.create_container_image import (
    check_if_image_already_exists,
    create_container_image,
)


@patch("operatorcert.entrypoints.create_container_image.pyxis.get")
@patch("operatorcert.entrypoints.create_container_image.are_all_deleted")
def test_check_if_image_already_exists(
    mock_check_deleted: MagicMock, mock_get: MagicMock
):
    # Arrange
    mock_check_deleted.return_value = True
    mock_rsp = MagicMock()
    mock_get.return_value = mock_rsp

    args = MagicMock()
    args.pyxis_url = "https://catalog.redhat.com/api/containers/"
    args.isv_pid = "some_isv_pid"
    args.docker_image_digest = "some_digest"

    # Image already exist, and it's not deleted
    mock_rsp.json.return_value = {"data": [{}], "total": 0}

    # Act
    exists = check_if_image_already_exists(args)
    # Assert
    assert exists
    mock_get.assert_called_with(
        "https://catalog.redhat.com/api/containers/v1/images?page_size=1&filter=isv_pid==some_isv_pid"
        ";docker_image_digest==some_digest"
    )

    # Image already exist, and it's deleted
    mock_rsp.json.return_value = {"data": [{"deleted": True}], "total": 0}

    # Act
    exists = check_if_image_already_exists(args)
    # Assert
    assert not exists

    # Image doesn't exist
    mock_rsp.json.return_value = {"data": [], "total": 0}

    # Act
    exists = check_if_image_already_exists(args)
    # Assert
    assert not exists


@patch("operatorcert.entrypoints.create_container_image.pyxis.post")
def test_create_container_image(mock_post: MagicMock):
    # Arrange
    mock_post.return_value = "ok"

    args = MagicMock()
    args.pyxis_url = "https://catalog.redhat.com/api/containers/"
    args.isv_pid = "some_isv_pid"
    args.registry = "some_registry"
    args.repository = "some_repo"
    args.docker_image_digest = "some_digest"

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
                }
            ],
            "certified": True,
            "docker_image_digest": "some_digest",
        },
    )
