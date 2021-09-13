import argparse
import logging
from typing import Any
from urllib.parse import urljoin

from operatorcert import pyxis
from operatorcert.logger import setup_logger

LOGGER = logging.getLogger("operator-cert")


def setup_argparser() -> Any:
    """
    Setup argument parser

    Returns:
        Any: Initialized argument parser
    """
    parser = argparse.ArgumentParser(description="Bundle dockerfile generator.")

    parser.add_argument(
        "--pyxis-url",
        default="https://catalog.redhat.com/api/containers/",
        help="Base URL for Pyxis container metadata API",
    )
    parser.add_argument(
        "--isv-pid", help="isv_pid of the certification project from Red Hat Connect", required=True
    )
    parser.add_argument(
        "--repo-published", help="is the ContainerImage repository published?", required=True
    )
    parser.add_argument(
        "--registry", help="Certification Project Registry", required=True
    )
    # TODO
    parser.add_argument("--repository", help="", required=True)

    parser.add_argument("--certified", help="Is the ContainerImage certified?", required=True)
    parser.add_argument("--docker-image-digest", help="Container Image digest of related Imagestream", required=True)
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    return parser


def check_if_image_already_exists(args) -> bool:
    check_url = urljoin(
        args.pyxis_url, f"v1/images?page_size=1&"
                        f"filter="
                        f"isv_pid=={args.isv_pid};"
                        f"docker_image_digest=={args.docker_image_digest}"
    )

    # Get the list of the ContainerImages with given parameters
    rsp = pyxis.get(check_url)
    rsp.raise_for_status()

    query_results = rsp.json()["data"]
    total_images = rsp.json()["total"]

    if len(query_results) == 0:
        return False

    # Test, if the images that we got are all deleted.
    # To do that, we firstly check if record in response is deleted.
    # If it is not, image already exists. If it is, then we query
    # all the deleted images with given parameters,
    # and compare amount with the original amount.
    # That's most efficient method, since we cannot use `$exists` in Pyxis query.
    if query_results[0].get("deleted", False):
        return not are_all_deleted(args, total_images)
    else:
        LOGGER.info("Image with given docker_image_digest and isv_pid already exists")
        return True


def are_all_deleted(args, total_images):
    get_deleted_url = urljoin(
        args.pyxis_url, f"v1/images?page_size=1&"
                        f"filter="
                        f"isv_pid=={args.isv_pid};"
                        f"docker_image_digest=={args.docker_image_digest};"
                        f"deleted==true"
    )
    rsp = pyxis.get(get_deleted_url)
    rsp.raise_for_status()
    total_deleted = rsp.json()["total"]

    if total_deleted != total_images:
        return False
    return True


def create_container_image(args):
    LOGGER.info("Creating new container image")

    upload_url = urljoin(
        args.pyxis_url, f"v1/images"
    )
    container_image_payload = {
        "isv_pid": args.isv_pid,
        "repositories": [{
            "published": True,
            "registry": args.registry,
            "repository": args.repository,
        }],
        "certified": True,
        "docker_image_digest": args.docker_image_digest
    }

    return pyxis.post(upload_url, container_image_payload)


def main():
    """
    Main func
    """

    parser = setup_argparser()
    args = parser.parse_args()
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logger(log_level)

    exists = check_if_image_already_exists(args)

    if not exists:
        create_container_image(args)


if __name__ == "__main__":
    main()
