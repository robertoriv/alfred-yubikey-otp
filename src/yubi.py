# encoding: utf-8

import os
import subprocess
import sys
import re
from packaging import version

from workflow import Workflow, MATCH_SUBSTRING, ICON_ERROR, util
from workflow.background import run_in_background
from icons import get_icon_for_service

YKMAN_MIN_VERSION = "4.0.0"
GITHUB_SLUG = "robertoriv/alfred-yubikey-otp"

if os.path.isdir("/opt/homebrew/bin"):
    BREW_BIN_PATH = "/opt/homebrew/bin"  # new homebrew bin folder
else:
    BREW_BIN_PATH = "/usr/local/bin"  # old homebrew bin folder

log = None


def execute(cmd_list):
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
    codes = execute(["ykman", "oath", "accounts", "code"]).splitlines()
    for code in codes:
        log.info(code)
        code_search = re.search(
            r"(.*)((\d{6,8})|(\[Requires Touch\]))", code, re.IGNORECASE
        )
        if code_search:
            entry = {
                "name": code_search.group(1).strip(),
                "code": code_search.group(2).strip(),
            }
            formatted_codes.append(entry)
    log.info(formatted_codes)
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


def get_ykman_version():
    log.info("Getting ykman vesion...")
    v_string = execute(["ykman", "--version"]).splitlines()[0]
    return re.search(r"(\d+\.\d+\.\d+)$", v_string).group(1)


def check_ykman_version():
    v = wf.cached_data("ykman_version", get_ykman_version, max_age=3600)
    parsed_version = version.parse(v)
    log.info("Current ykman version: " + str(parsed_version))
    if parsed_version < version.parse(YKMAN_MIN_VERSION):
        log.info("Clearing the 'ykman_version' cache...")
        wf.cache_data(
            "ykman_version", None
        )  # clear the cache to force a read from the cli next time
        return False
    return True


def yubikey_not_inserted():
    codes = execute(["ykman", "oath", "accounts", "code"]).splitlines()
    if "Error: No YubiKey detected!" in codes:
        return True
    return False


def ykman_installed():
    return os.path.isfile("/usr/local/bin/ykman")


def touch(wf, name):
    new_env = os.environ.copy()
    new_env["PATH"] = "/usr/local/bin:%s" % new_env["PATH"]
    process = subprocess.Popen(
        ["ykman", "oath", "accounts", "code", name], stdout=subprocess.PIPE, env=new_env
    )
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
        # extract query
        query = wf.args[0] if len(wf.args) else None
        codes = filter_available_codes(wf, query)
        for code in codes:
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
