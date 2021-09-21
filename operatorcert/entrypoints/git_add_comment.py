"""
Script for opening GitHub pull request
"""
import argparse
import logging
import os
import json
from typing import Any, Dict
import http.client
import sys
import urllib.parse


LOGGER = logging.getLogger("git-add-comment")


def setup_argparser() -> Any:
    """
    Setup argument parser

    Returns:
        Any: Initialized argument parser
    """
    parser = argparse.ArgumentParser(
        description="Github add commnent PR hosted pipeline tool."
    )

    parser.add_argument(
        "--git-host-url",
        default="api.github.com",
        help="The GitHub host, adjust this if you run a GitHub enteprise",
    )
    parser.add_argument(
        "--api-path-prefix",
        default="",
        help="The API path prefix, GitHub Enterprise has a prefix e.g. /api/v3",
    )
    parser.add_argument(
        "--request-url",
        required=True,
        help="The GitHub issue or pull request URL where we want to add a new comment",
    )
    parser.add_argument(
        "--comment-or-file",
        required=True,
        help="The actual comment to add or the filename containing comment to post.",
    )
    parser.add_argument(
        "--comment-tag",
        default="",
        help="An invisible tag to be added into the comment.",
    )
    parser.add_argument(
        "--replace",
        default="false",
        help="When a tag is specified, and `REPLACE` is `true`, look for a comment with a matching tag and replace it with the new comment.",
    )

    parser.add_argument(
        "--test-result", help="Result from the preflight test.", required=True
    )

    parser.add_argument(
        "--comment-file",
        help="The optional workspace containing comment file to be posted.",
        required=True,
    )

    parser.add_argument(
        "--old-comment", help="The old text of the comment, if any.", required=True
    )

    parser.add_argument(
        "--new-comment", help="The new text of the comment, if any.", required=True
    )

    return parser


def github_add_comment(args: Any) -> None:
    """
    Add the comment on github PR.

    Args:
        args (Any): CLI arguments

    """

    if args.test_result == "success":
        LOGGER.info("Tests passed successfully.")
        sys.exit(1)
    split_url = urllib.parse.urlparse(args.request_url).path.split("/")
    # This will convert https://github.com/foo/bar/pull/202 to
    # api url path /repos/foo/issues/
    api_url = "{base}/repos/{package}/issues/{id}".format(
        base="", package="/".join(split_url[1:3]), id=split_url[-1]
    )
    commentParamValue = f"""{args.comment_or_file}"""
    # check if workspace is bound and parameter passed is a filename or not
    if args.comment_file == "true" and os.path.exists(commentParamValue):
        commentParamValue = open(commentParamValue, "r").read()
    # If a tag was specified, append it to the comment
    if args.comment_tag:
        commentParamValue += "<!-- {tag} -->".format(tag=args.comment_tag)
    data = {
        "body": commentParamValue,
    }
    # This is for our fake github server
    if args.github_host_url.startswith("http://"):
        conn = http.client.HTTPConnection(args.github_host_url.replace("http://", ""))
    else:
        conn = http.client.HTTPSConnection(args.github_host_url)
    # If REPLACE is true, we need to search for comments first
    matching_comment = ""
    if args.replace == "true":
        if not args.comment_tag:
            LOGGER.debug("REPLACE requested but no COMMENT_TAG specified")
            sys.exit(1)
        github_token = ""
        with open(f"{os.environ['GITHUBTOKEN']}/github_bot_token.txt", "r") as file:
            github_token = file.read()
        r = conn.request(
            "GET",
            api_url + "/comments",
            headers={
                "User-Agent": "TektonCD, the peaceful cat",
                "Authorization": "Bearer " + github_token,
            },
        )
        resp = conn.getresponse()
        if not str(resp.status).startswith("2"):
            LOGGER.debug("Error: %d" % (resp.status))
            LOGGER.debug(resp.read())
            sys.exit(1)
        LOGGER.info(resp.status)
        comments = json.loads(resp.read())
        LOGGER.info(comments)
        # If more than one comment is found take the last one
        matching_comment = [x for x in comments if args.comment_tag in x["body"]][-1:]
        if matching_comment:
            with open(args.old_comment, "w") as result_old:
                result_old.write(str(matching_comment[0]))
            matching_comment = matching_comment[0]["url"]
    if matching_comment:
        method = "PATCH"
        target_url = urllib.parse.urlparse(matching_comment).path
    else:
        method = "POST"
        target_url = api_url + "/comments"
    LOGGER.info("Sending this data to GitHub with {}: ".format(method))
    LOGGER.info(data)
    r = conn.request(
        method,
        target_url,
        body=json.dumps(data),
        headers={
            "User-Agent": "TektonCD, the peaceful cat",
            "Authorization": "Bearer " + os.environ["GITHUBTOKEN"],
        },
    )
    resp = conn.getresponse()
    if not str(resp.status).startswith("2"):
        LOGGER.debug("Error: %d" % (resp.status))
        LOGGER.debug(resp.read())
    else:
        with open(args.new_comment, "wb") as result_new:
            result_new.write(resp.read())
        LOGGER.info(
            "a GitHub comment has been {} to {}".format(
                "updated" if matching_comment else "added"
            ),
            args.request_url,
        )


def main() -> None:
    """
    Main function
    """
    parser = setup_argparser()
    args = parser.parse_args()

    log_level = "INFO"
    logging.basicConfig(level=log_level)

    github_add_comment(args)


if __name__ == "__main__":
    main()
