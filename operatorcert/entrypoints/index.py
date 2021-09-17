import argparse
import logging

from operatorcert import iib, utils
from typing import Any
import time
import os
from datetime import datetime, timedelta


LOGGER = logging.getLogger("operator-cert")


def setup_argparser() -> argparse.ArgumentParser:
    """
    Setup argument parser

    Returns:
        Any: Initialized argument parser
    """
    parser = argparse.ArgumentParser(description="Publish bundle to index image")
    parser.add_argument(
        "--organization",
        required=True,
        help="Organization index where bundle is released",
    )
    parser.add_argument(
        "--bundle-pullspec", required=True, help="Operator bundle pullspec"
    )
    parser.add_argument("--from-index", required=True, help="Base index pullspec")
    parser.add_argument(
        "--iib-url",
        default="https://iib.engineering.redhat.com",
        help="Base URL for IIB API",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    return parser


def wait_for_results(args: Any, build_id: int, timout=30 * 60, delay=20) -> Any:
    """
    Wait for IIB build till it finishes

    Args:
        args (Any): CLI arguments
        build_id (int): IIB build identifier
        timout ([type], optional): Maximum wait time. Defaults to 30*60.
        delay (int, optional): Delay between build pollin. Defaults to 20.

    Returns:
        Any: Build response
    """
    start_time = datetime.now()
    loop = True

    while loop:
        response = iib.get_build(args.iib_url, build_id)
        build_state = response.get("state")

        if build_state == "complete":
            LOGGER.info(f"IIB build completed successfully: {build_id}")
            return response
        elif build_state == "failed":
            LOGGER.error(f"IIB build failed: {build_id} - {build_state}")
            state_history = response.get("state_history", [])
            if state_history:
                reason = state_history[0].get("state_reason")
                LOGGER.info(f"Reason: {reason}")
            return response

        LOGGER.debug(f"Waiting for IIB build: {build_id}. Currently in '{build_state}'")
        if datetime.now() - start_time > timedelta(seconds=timout):
            LOGGER.error(f"Timeout: Waiting for IIB build failed: {build_id}.")
            break

        LOGGER.info(f"Waiting for IIB build to finish: {build_id} - {build_state}")
        time.sleep(delay)
    return None


def publish_bundle(args: Any) -> None:
    """
    Publish a bundle to index image using IIB

    Args:
        args (Any): CLI arguments

    Raises:
        Exception: Exception is raised when IIB build fails
    """

    user = os.getenv("QUAY_USER")
    token = os.getenv("QUAY_TOKEN")

    cnd_token = os.getenv("CNR_TOKEN")

    payload = {
        "from_index": args.from_index,
        "bundles": [args.bundle_pullspec],
        "cnr_token": f"basis {cnd_token}",
        "force_backport": True,
        "organization": args.organization,
        "overwrite_from_index": True,
        "add_arches": ["amd64", "s390x", "ppc64le"],
        "overwrite_from_index_token": f"{user}:{token}",
    }

    resp = iib.add_build(args.iib_url, payload)

    build_id = resp["id"]
    response = wait_for_results(args, build_id)
    if response is None or response.get("state") != "complete":
        raise Exception("IIB build failed")


def main() -> None:  # pragma: no cover
    """
    Main func
    """
    parser = setup_argparser()
    args = parser.parse_args()

    log_level = "INFO"
    if args.verbose:
        log_level = "DEBUG"
    logging.basicConfig(level=log_level)

    utils.set_client_keytab(os.environ.get("KRB_KEYTAB_FILE", "/etc/krb5.krb"))

    publish_bundle(args)


if __name__ == "__main__":  # pragma: no cover
    main()
