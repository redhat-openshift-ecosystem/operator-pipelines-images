import argparse
from datetime import datetime
import json
import logging
from typing import Any, Dict
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
        default="https://pyxis.engineering.redhat.com",
        help="Base URL for Pyxis container metadata API",
    )
    parser.add_argument(
        "--isv-pid",
        help="isv_pid of the certification project from Red Hat Connect",
        required=True,
    )
    parser.add_argument(
        "--repo-published",
        help="is the ContainerImage repository published?",
        required=True,
    )
    parser.add_argument(
        "--registry", help="Certification Project Registry", required=True
    )
    parser.add_argument(
        "--repository",
        help="Repository name assigned to certification project from Red Hat Connect",
        required=True,
    )
    parser.add_argument(
        "--certified", help="Is the ContainerImage certified?", required=True
    )
    parser.add_argument(
        "--bundle-version",
        help="Operator bundle version",
        required=True,
    )
    parser.add_argument(
        "--docker-image-digest",
        help="Container Image digest of related Imagestream",
        required=True,
    )
    parser.add_argument(
        "--skopeo-result",
        help="File with result of `skopeo inspect` running against image"
        " represented by ContainerImage to be created",
        required=True,
    )
    parser.add_argument(
        "--image-size", help="sum of the size of image layers", required=True
    )
    parser.add_argument("--is-latest", help="Is given version latest?", required=True)
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    return parser


def check_if_image_already_exists(args) -> bool:
    check_url = urljoin(
        args.pyxis_url,
        f"v1/images?page_size=1&"
        f"filter="
        f"isv_pid=={args.isv_pid};"
        f"docker_image_digest=={args.docker_image_digest};"
        f"not(deleted==true)",
    )

    # Get the list of the ContainerImages with given parameters
    rsp = pyxis.get(check_url)
    rsp.raise_for_status()

    query_results = rsp.json()["data"]

    if len(query_results) == 0:
        LOGGER.info(
            "Image with given docker_image_digest and isv_pid doesn't exists yet"
        )
        return False

    LOGGER.info(
        "Image with given docker_image_digest and isv_pid already exists."
        "Skipping the image creation."
    )
    return True


def prepare_parsed_data(skopeo_result_file: str) -> Dict[str, Any]:
    with open(skopeo_result_file) as json_file:
        skopeo_result = json.load(json_file)

        parsed_data = {
            "docker_version": skopeo_result.get("docker_version", ""),
            "layers": skopeo_result.get("Layers", []),
            "architecture": skopeo_result.get("Architecture", ""),
            "env_variables": skopeo_result.get("Env", []),
        }

        return parsed_data


def create_container_image(args):
    LOGGER.info("Creating new container image")

    date_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
    parsed_data = prepare_parsed_data(args.skopeo_result)

    upload_url = urljoin(args.pyxis_url, f"v1/images")
    container_image_payload = {
        "isv_pid": args.isv_pid,
        "repositories": [
            {
                "published": True,
                "registry": args.registry,
                "repository": args.repository,
                "push_date": date_now,
                "tags": [
                    {
                        "added_date": date_now,
                        "name": args.bundle_version,
                    },
                ],
            }
        ],
        "certified": True,
        "docker_image_digest": args.docker_image_digest,
        "architecture": parsed_data["architecture"],
        "parsed_data": parsed_data,
        "sum_layer_size_bytes": int(args.image_size),
        # "freshness_grades": "X",
    }

    if args.is_latest == "true":
        # TODO: remove latest from previous image (if it exists)
        container_image_payload["repositories"][0]["tags"].append(
            {
                "added_date": date_now,
                "name": "latest",
            }
        )

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
