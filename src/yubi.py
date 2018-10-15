# encoding: utf-8

import os
import subprocess
import sys
import re

from workflow import Workflow, MATCH_SUBSTRING, ICON_ERROR, util
from workflow.background import run_in_background

GITHUB_SLUG = 'robertoriv/alfred-yubikey-otp'

log = None


def execute(cmd_list):
    new_env = os.environ.copy()
    new_env['PATH'] = '/usr/local/bin:%s' % new_env['PATH']
    cmd, err = subprocess.Popen(cmd_list,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=new_env).communicate()
    if err:
        return err
    return cmd


def get_all_codes():
    formatted_codes = []
    codes = execute(['ykman', 'oath', 'code']).splitlines()
    for code in codes:
        log.info(code)
        code_search = re.search('(.*)(\d{6,8})', code, re.IGNORECASE)
        if code_search:
            entry = {
                "name": code_search.group(1).strip(),
                "code": code_search.group(2).strip()
            }
            formatted_codes.append(entry)
    log.info(formatted_codes)
    return formatted_codes


def key_for_codes(code):
    return code['name']


def filter_available_codes(wf, query):
    available_codes = wf.cached_data('ykman_available_codes', get_all_codes, max_age=10)
    query_filter = query.split()
    if query_filter:
        return wf.filter(query_filter[0], available_codes, key_for_codes, match_on=MATCH_SUBSTRING)
    return available_codes


def yubikey_not_inserted():
    codes = execute(['ykman', 'oath', 'code']).splitlines()
    if 'Error: No YubiKey detected!' in codes:
        return True
    return False


def ykman_installed():
    return os.path.isfile('/usr/local/bin/ykman')


def main(wf):

    if not ykman_installed():
        wf.add_item('Error', 'Please install ykman (brew install ykman)...', icon=ICON_ERROR, valid=True)
    elif yubikey_not_inserted():
        wf.add_item('Error', 'Please insert your Yubikey...', icon=ICON_ERROR, valid=True,)
    else:
        # extract query
        query = wf.args[0] if len(wf.args) else None

        for code in filter_available_codes(wf, query):
            wf.add_item(code['name'], 'Copy to %s clipboard...' % code['code'], arg=code['code'], valid=True,)

    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow(update_settings={'github_slug': GITHUB_SLUG})
    log = wf.logger
    sys.exit(wf.run(main))

