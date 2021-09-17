from typing import Any, Dict
from urllib.parse import urljoin
from requests_kerberos import HTTPKerberosAuth
import requests
import logging

LOGGER = logging.getLogger("operator-cert")


def get_session(kerberos_auth=True) -> Any:
    """
    Get IIB requests session

    Args:
        kerberos_auth (bool, optional): Session uses kerberos auth. Defaults to True.

    Returns:
        Any: IIB session
    """
    session = requests.Session()

    if kerberos_auth:
        session.auth = HTTPKerberosAuth()

    return session


def add_build(base_url: str, body: Dict[str, Any]) -> Any:
    """
    Add IIB build

    Args:
        base_url (str): Base URL of IIB API
        body (Dict[str, Any]): Add build request payload

    Returns:
        Any: IIB api response
    """
    session = get_session()

    add_build_url = urljoin(base_url, f"api/v1/builds/add")

    resp = session.post(add_build_url, json=body)

    try:
        resp.raise_for_status()
    except requests.HTTPError:
        LOGGER.exception(
            f"IIB POST query failed with {add_build_url} - {resp.status_code} - {resp.text}"
        )
        raise
    return resp.json()


def get_build(base_url: str, build_id: int) -> Any:
    """
    Get IIB build

    Args:
        base_url (str): Base URL of IIB API
        build_id (int): Build identifier

    Returns:
        Any: Build API response
    """

    session = get_session(False)

    add_build_url = urljoin(base_url, f"api/v1/builds/{build_id}")

    resp = session.get(add_build_url)

    try:
        resp.raise_for_status()
    except requests.HTTPError:
        LOGGER.exception(
            f"IIB GET query failed with {add_build_url} - {resp.status_code} - {resp.text}"
        )
        raise
    return resp.json()
