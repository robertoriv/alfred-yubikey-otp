# encoding: utf-8

import os
import subprocess
import sys
import re
from packaging import version

from workflow import Workflow, MATCH_SUBSTRING, ICON_ERROR
from workflow.background import run_in_background
from icons import get_icon_for_service

GITHUB_SLUG = "robertoriv/alfred-yubikey-otp"

if os.path.isdir("/opt/homebrew/bin"):
    BREW_BIN_PATH = "/opt/homebrew/bin"  # new homebrew bin folder
else:
    BREW_BIN_PATH = "/usr/local/bin"  # old homebrew bin folder

YKMAN_MIN_VERSION = "4.0.0"
YKMAN_BIN_PATH = BREW_BIN_PATH + "/ykman"

log = None


def execute(cmd_list):
    log.debug("Executing command: " + str(cmd_list))
    new_env = os.environ.copy()
    new_env["PATH"] = "%s:%s" % (BREW_BIN_PATH, new_env["PATH"])
    cmd, err = subprocess.Popen(
        cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=new_env
    ).communicate()
    if err:
        return err
    return cmd


def get_all_codes():
    formatted_codes = []
    cmd = ["ykman", "oath", "accounts", "code"]
    if ("PASSWORD" in os.environ and os.environ["PASSWORD"]):
        cmd = ["ykman", "oath", "accounts", "code", "-p", os.environ["PASSWORD"]]
    codes = execute(cmd).splitlines()
    for code in codes:
        log.debug("Received: " + code)
        code_search = re.search(
            r"(.*)((\d{6,8})|(\[Requires Touch\]))", code, re.IGNORECASE
        )
        if code_search:
            entry = {
                "name": code_search.group(1).strip(),
                "code": code_search.group(2).strip(),
            }
            formatted_codes.append(entry)
    log.debug("Code objects: " + str(formatted_codes))
    return formatted_codes


def key_for_codes(code):
    return code["name"]


def filter_available_codes(wf, query):
    available_codes = wf.cached_data("ykman_available_codes", get_all_codes, max_age=10)
    if query is not None:
        query_filter = query.split()
        if query_filter:
            return wf.filter(
                query_filter[0],
                available_codes,
                key_for_codes,
                match_on=MATCH_SUBSTRING,
            )
    return available_codes


def exact_match(wf, query):
    available_codes = wf.cached_data("ykman_available_codes", get_all_codes, max_age=10)
    codes = wf.filter(
        query,
        available_codes,
        key_for_codes,
        match_on=MATCH_SUBSTRING,
    )

    if len(codes) == 1:
        return codes
    else:
        log.debug(
            "Search returned more than one code: \n"
            + str([code["name"] for code in codes])
        )

        # Workflow.filter uses fuzzy searching and we need to manually apply our own filter on top
        for code in codes:
            if code["name"] == query:
                return [code]

    raise RuntimeError("Could not find an exact match for: {}".format(query))


def get_ykman_version():
    log.info("Getting ykman vesion...")
    v_string = execute(["ykman", "--version"]).splitlines()[0]
    log.info("Version: " + v_string)
    return re.search(r"(\d+\.\d+\.\d+)$", v_string).group(1)


def check_ykman_version():
    v = wf.cached_data("ykman_version", get_ykman_version, max_age=3600)
    parsed_version = version.parse(v)
    if parsed_version < version.parse(YKMAN_MIN_VERSION):
        log.info("Clearing the 'ykman_version' cache...")
        wf.cache_data(
            "ykman_version", None
        )  # clear the cache to force a read from the cli next time
        return False
    return True


def yubikey_not_inserted():
    cmd = ["ykman", "oath", "accounts", "code"]
    if ("PASSWORD" in os.environ and os.environ["PASSWORD"]):
        cmd = ["ykman", "oath", "accounts", "code", "-p", os.environ["PASSWORD"]]
    codes = execute(cmd).splitlines()
    if "Error: No YubiKey detected!" in codes:
        log.warn("ykman: " + str(codes))
        return True
    return False


def ykman_installed():
    return os.path.isfile(YKMAN_BIN_PATH)


def touch(wf, name):
    new_env = os.environ.copy()
    new_env["PATH"] = "%s:%s" % (BREW_BIN_PATH, new_env["PATH"])
    cmd = ["ykman", "oath", "accounts", "code", name]
    if ("PASSWORD" in os.environ and os.environ["PASSWORD"]):
        cmd = ["ykman", "oath", "accounts", "code", name, "-p", os.environ["PASSWORD"]]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=new_env)
    counter = 0
    for i in iter(process.stdout.readline, "b"):
        code_search = re.search(r"(.*)((\d{6,8}))", i, re.IGNORECASE)
        if code_search:
            wf.add_item(
                name,
                "Copy %s to clipboard" % code_search.group(2).strip(),
                arg=code_search.group(2).strip(),
                icon=get_icon_for_service(name),
                valid=True,
            )
            break
        counter += 1
        if counter == 3:
            wf.add_item(
                name,
                "Timeout",
                arg=name,
                icon=get_icon_for_service(name),
                valid=True,
            )
            break
    process.kill()


def main(wf):
    log.debug("Script was executed with the following args: " + ", ".join(wf.args))

    if not ykman_installed():
        wf.add_item(
            "Error",
            "Please install ykman (brew install ykman)...",
            icon=ICON_ERROR,
            valid=False,
        )
    elif not check_ykman_version():
        wf.add_item(
            "Error",
            "Please upgrade to ykman >= 4.0.0 (brew upgade ykman)...",
            icon=ICON_ERROR,
            valid=False,
        )
    elif yubikey_not_inserted():
        wf.add_item(
            "Error",
            "Please insert your Yubikey...",
            icon=ICON_ERROR,
            valid=False,
        )
    else:
        if wf.args[0] == "search" and len(wf.args) > 1:
            log.debug("Performing search for: " + wf.args[1])
            query = wf.args[1]
            codes = filter_available_codes(wf, query)
        elif wf.args[0] == "exact" and len(wf.args) > 1:
            log.debug("Retrieving exact match: " + wf.args[1])
            query = wf.args[1]
            codes = exact_match(wf, query)
        else:
            log.debug("Retrieving all codes...")
            codes = filter_available_codes(wf, None)

        for code in codes:
            log.debug("Filtered: " + str(code))
            if code["code"] == "[Requires Touch]":
                if len(codes) == 1:
                    touch(wf, code["name"])
                else:
                    wf.add_item(
                        code["name"],
                        "Require Touch",
                        arg=code["name"],
                        icon=get_icon_for_service(code["name"]),
                        valid=True,
                    )
            else:
                wf.add_item(
                    code["name"],
                    "Copy to %s clipboard..." % code["code"],
                    arg=code["code"],
                    icon=get_icon_for_service(code["name"]),
                    valid=True,
                )
    wf.send_feedback()


if __name__ == "__main__":
    wf = Workflow(update_settings={"github_slug": GITHUB_SLUG})
    log = wf.logger
    sys.exit(wf.run(main))
