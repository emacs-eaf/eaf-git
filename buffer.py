#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2018 Andy Stewart
#
# Author:     Andy Stewart <lazycat.manatee@gmail.com>
# Maintainer: Andy Stewart <lazycat.manatee@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import os
import shutil
from copy import copy
from io import StringIO

import pygit2
from app.git.utils import get_git_https_url
from charset_normalizer import from_bytes, from_path
from core.utils import PostGui, eval_in_emacs, get_emacs_func_result, get_emacs_var, get_emacs_vars, interactive, message_to_emacs
from core.webengine import BrowserBuffer
from pygit2 import GIT_BRANCH_REMOTE, GIT_CHECKOUT_FORCE, GIT_STATUS_CONFLICTED, GIT_STATUS_CURRENT, GIT_STATUS_IGNORED, GIT_STATUS_INDEX_DELETED, GIT_STATUS_INDEX_MODIFIED, GIT_STATUS_INDEX_NEW, GIT_STATUS_INDEX_RENAMED, GIT_STATUS_INDEX_TYPECHANGE, GIT_STATUS_WT_DELETED, GIT_STATUS_WT_MODIFIED, GIT_STATUS_WT_NEW, GIT_STATUS_WT_RENAMED, GIT_STATUS_WT_TYPECHANGE, GIT_STATUS_WT_UNREADABLE, IndexEntry, Oid, Repository
from pygit2._pygit2 import GitError
from PyQt6 import QtCore
from PyQt6.QtCore import QMimeDatabase, QThread, QTimer
from PyQt6.QtGui import QColor
from unidiff import LINE_TYPE_ADDED, LINE_TYPE_CONTEXT, LINE_TYPE_REMOVED, Hunk, PatchSet

GIT_STATUS_DICT = {
    GIT_STATUS_CURRENT: "Current",
    GIT_STATUS_INDEX_NEW: "New",
    GIT_STATUS_INDEX_MODIFIED: "Modified",
    GIT_STATUS_INDEX_DELETED: "Deleted",
    GIT_STATUS_INDEX_RENAMED: "Renamed",
    GIT_STATUS_INDEX_TYPECHANGE: "Typechange",
    GIT_STATUS_WT_NEW: "New",
    GIT_STATUS_WT_MODIFIED: "Modified",
    GIT_STATUS_WT_DELETED: "Deleted",
    GIT_STATUS_WT_TYPECHANGE: "Typechange",
    GIT_STATUS_WT_RENAMED: "Renamed",
    GIT_STATUS_WT_UNREADABLE: "Unreadable",
    GIT_STATUS_IGNORED: "Ignored",
    GIT_STATUS_CONFLICTED: "Conflicted"
}

GIT_STATUS_INDEX_CHANGES = [
    GIT_STATUS_INDEX_NEW,
    GIT_STATUS_INDEX_MODIFIED,
    GIT_STATUS_INDEX_DELETED,
    GIT_STATUS_INDEX_RENAMED,
    GIT_STATUS_INDEX_TYPECHANGE,
]

NO_PREVIEW = "Previewing binary data is not supported now. \n"

def pretty_date(time):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    diff = 0

    if isinstance(time, int):
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    else:
        return ""

    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff // 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff // 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff // 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff // 30) + " months ago"
    return str(day_diff // 365) + " years ago"

def bytes_decode(str_encode_bytes):
    return str(from_bytes(str_encode_bytes).best())

def is_binary(filename_or_bytes):
    """
    Return true if the given file or content appears to be binary.
    File is considered to be binary if it contains a NULL byte.
    FIXME: This approach incorrectly reports UTF-16 as binary.
    """
    if isinstance(filename_or_bytes, str):
        with open(filename_or_bytes, 'rb') as f:
            for block in f:
                if b'\0' in block:
                    return True
            return False
    else:
        for b in filename_or_bytes:
            if b == 0:
                return True
            return False

def get_command_result(command_string, input_text=None):
    import subprocess
    process = subprocess.Popen(command_string, shell=True, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if input_text:
        out, err = process.communicate(input=input_text)
        ret = process.returncode
        return out if ret == 0 else err
    else:
        ret = process.wait()
        return "".join((process.stdout if ret == 0 else process.stderr).readlines())

def patch_stream(instream, hunks):
    hunks = iter(hunks)
    srclineno = 1
    lineends = {"\n":0, "\r\n":0, "\r":0}
    def get_line():
        line = instream.readline()
        if line.endswith("\r\n"):
            lineends["\r\n"] += 1
        elif line.endswith("\n"):
            lineends["\n"] += 1
        elif line.endswith("\r"):
            lineends["\r"] += 1
        return line

    for hno, h in enumerate(hunks):
        while srclineno < h.source_start:
            yield get_line()
            srclineno += 1

        for hline in h:
            # TODO: check \ No newline at the end of file
            hline = str(hline)
            if hline.startswith("-") or hline.startswith("\\"):
                get_line()
                srclineno += 1
                continue
            else:
                if not hline.startswith("+"):
                    get_line()
                    srclineno += 1
                line2write = hline[1:]
                # Detect if line ends are consistent in source file
                if sum([bool(lineends[x]) for x in lineends]) == 1:
                    newline = [x for x in lineends if lineends[x] != 0][0]
                    yield line2write.rstrip("\r\n") + newline
                else: # Newlines are mixed
                    yield line2write
    for line in instream:
        yield line

def parse_patch(patches, highlight):
    patch_set = []
    for patch in patches:
        patch_set.append({
            "path": patch.path,
            "patch_info": "".join(patch.patch_info),
            "diff_hunks": [highlight(str(hunk)) for hunk in patch]
        })
    return patch_set

def status_is_include(status, file_info):
    "Check if status1 has file_info"
    for stat in status:
        if stat["file"] == file_info["file"]:
            return True

    return False

class AppBuffer(BrowserBuffer):
    def __init__(self, buffer_id, url, arguments):
        BrowserBuffer.__init__(self, buffer_id, url, arguments, False)

        self.stage_status = []
        self.unstage_status = []
        self.untrack_status = []
        self.branch_status = []
        self.raw_patch_set = []

        self.nav_current_item = "Dashboard"

        self.mime_db = QMimeDatabase()

        self.search_log_cache_path = ""
        self.search_submodule_cache_path = ""

        self.temp_files = []

        self.thread_reference_list = []

        self.log_compare_branch = ""

        self.url = os.path.expanduser(self.url)
        self.repo = Repository(self.url)
        self.repo_root = self.url

        eval_in_emacs('eaf--change-default-directory', [self.buffer_id, self.url])

        self.repo_path = os.path.sep.join(list(filter(lambda x: x != '', self.repo_root.split(os.path.sep)))[-2:])

        self.change_title("Git [{}]".format(self.repo_path))

        self.last_commit = None
        self.last_commit_id = ""
        self.last_commit_message = ""

        if self.repo.head_is_unborn:
            message_to_emacs("There is no commit yet")
        else:
            self.last_commit_id = str(self.repo.head.target)
            self.last_commit = self.repo.revparse_single(str(self.repo.head.target))
            try:
                self.last_commit_message = bytes_decode(self.last_commit.raw_message).splitlines()[0]
            except:
                pass

        self.highlight_style = "monokai"

        self.load_index_html(__file__)

    def init_app(self):
        self.init_vars()
        self.update_git_info()

    def update_git_info(self):
        self.fetch_unpush_info()
        self.fetch_status_info()
        self.fetch_log_info()
        self.fetch_stash_info()
        self.fetch_submodule_info()
        self.fetch_branch_info()

    def init_vars(self):
        (layout, statusState, untrackState, unstageState, stageState, stashState, unpushState) = get_emacs_vars([
            "eaf-git-layout",
            "eaf-git-status-initial-state",
            "eaf-git-untracked-initial-state",
            "eaf-git-unstaged-initial-state",
            "eaf-git-staged-initial-state",
            "eaf-git-stash-initial-state",
            "eaf-git-unpushed-initial-state"
        ])

        if self.theme_mode == "dark":
            if self.theme_background_color == "#000000":
                select_color = "#333333"
            else:
                select_color = QColor(self.theme_background_color).darker(120).name()

            self.highlight_style = get_emacs_var("eaf-git-dark-highlight-style")
        else:
            if self.theme_background_color == "#FFFFFF":
                select_color = "#EEEEEE"
            else:
                select_color = QColor(self.theme_background_color).darker(110).name()

            self.highlight_style = get_emacs_var("eaf-git-light-highlight-style")

        (text_color, nav_item_color, info_color, date_color, id_color, match_color, author_color) = get_emacs_func_result(
            "get-emacs-face-foregrounds",
            ["default",
             "font-lock-function-name-face",
             "font-lock-keyword-face",
             "font-lock-builtin-face",
             "font-lock-comment-face",
             "font-lock-string-face",
             "font-lock-negation-char-face"])

        self.buffer_widget.eval_js_function("init",
            layout,
            {
                "status": statusState,
                "untrack": untrackState,
                "unstage": unstageState,
                "stage": stageState,
                "stash": stashState,
                "unpush": unpushState
            },
            self.theme_background_color, self.theme_foreground_color, select_color, QColor(self.theme_background_color).darker(110).name(),
            text_color, nav_item_color, info_color,
            date_color, id_color, author_color, match_color,
            self.repo_path, self.last_commit_id,
            {"lastCommit": self.last_commit_message},
            self.get_keybinding_info())

    def some_view_show(self):
        # Automatically refresh the Git status when the interface is displayed.
        self.update_git_info()

    @interactive
    def update_theme(self):
        super().update_theme()
        self.init_vars()

    def fetch_status_info(self, adjust_selection=False):
        thread = FetchStatusThread(self.repo, self.repo_root, self.mime_db)

        # If adjust_selection is True, update both status_info and the selection of status.
        if adjust_selection:
            thread.fetch_result.connect(self.update_status_info_and_selection)
        else:
            thread.fetch_result.connect(self.update_status_info)

        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def update_status_info(self, stage_status, unstage_status, untrack_status, select=None):
        if select is None:
            self.buffer_widget.eval_js_function("updateStatusInfo", stage_status, unstage_status, untrack_status)
        else:
            select_item_index = -1
            select_item_type = ""

            if len(untrack_status) > 0:
                select_item_type = "untrack"
            elif len(unstage_status) > 0:
                select_item_type = "unstage"
            elif len(stage_status) > 0:
                select_item_type = "stage"

            self.buffer_widget.eval_js_function("updateSelectInfo", stage_status, unstage_status, untrack_status, select_item_type, select_item_index)

        QTimer().singleShot(300, self.init_diff)

    @PostGui()
    def update_status_info_and_selection(self, stage_status, unstage_status, untrack_status):
        self.update_status_info(stage_status, unstage_status, untrack_status, True)

    def init_diff(self):
        if len(self.untrack_status) > 0:
            self.update_diff("untrack", "")
        elif len(self.unstage_status) > 0:
            self.update_diff("unstage", "")
        elif len(self.stage_status) > 0:
            self.update_diff("stage", "")

    def get_keybinding_info(self):
        js_keybindig = get_emacs_var("eaf-git-js-keybinding")
        js_keybindig_dict = {}

        for keybindig_list in js_keybindig:
            module_name = keybindig_list[0]
            module_keybinding_dict = {}

            for key_value in keybindig_list[1:][0]:
                module_keybinding_dict[key_value[0]] = {
                    "command": key_value[1][0],
                    "description": key_value[1][1]
                }

            js_keybindig_dict[module_name] = module_keybinding_dict

        return js_keybindig_dict

    def fetch_unpush_info(self):
        thread = FetchUnpushThread(self.repo, self.repo_root)
        thread.fetch_result.connect(self.update_unpush_info)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def update_unpush_info(self, unpush_list):
        self.buffer_widget.eval_js_function("updateUnpushInfo", unpush_list)

    @QtCore.pyqtSlot()
    def fetch_log_info(self):
        if self.repo.head_is_unborn: return  # noqa: E701
        thread = FetchLogThread(self.repo, self.repo.head, True)
        thread.fetch_result.connect(self.update_log_info)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def update_log_info(self, branch_name, log, search_cache_path, append):
        if self.search_log_cache_path != "" and os.path.exists(self.search_log_cache_path):
            if self.search_log_cache_path not in self.temp_files:
                self.temp_files.append(self.search_log_cache_path)

        self.search_log_cache_path = search_cache_path
        self.buffer_widget.eval_js_function("updateLogInfo", branch_name, log, append)

    def fetch_compare_log_info(self, branch_name):
        branch = self.repo.branches.get(branch_name)

        thread = FetchLogThread(self.repo, branch)
        thread.fetch_result.connect(self.update_compare_log_info)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def update_compare_log_info(self, branch_name, log, search_cache_path, append):
        self.buffer_widget.eval_js_function("updateCompareLogInfo", branch_name, log, append)

    @QtCore.pyqtSlot()
    def grep_log_info(self):
        self.send_input_message("Grep log with: ", "grep_log", "string")

    def handle_grep_log(self, keyword):
        if self.repo.head_is_unborn: return  # noqa: E701

        message_to_emacs(f"Grep log with keyword: {keyword}...")

        thread = GrepLogThread(self.repo, self.repo.head, keyword, True)
        thread.fetch_result.connect(self.update_grep_log_info)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def update_grep_log_info(self, keyword, branch_name, log, search_cache_path):
        if self.search_log_cache_path != "" and os.path.exists(self.search_log_cache_path):
            if self.search_log_cache_path not in self.temp_files:
                self.temp_files.append(self.search_log_cache_path)

        self.search_log_cache_path = search_cache_path
        self.buffer_widget.eval_js_function("updateLogInfo", branch_name, log)

        message_to_emacs(f"Find log match keyword: {keyword}")

    def fetch_stash_info(self):
        thread = FetchStashThread(self.repo)
        thread.fetch_result.connect(self.update_stash_info)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def update_stash_info(self, stash):
        self.buffer_widget.eval_js_function("updateStashInfo", stash)

    def fetch_submodule_info(self):
        thread = FetchSubmoduleThread(self.repo, self.repo_root)
        thread.fetch_result.connect(self.update_submodule_info)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def update_submodule_info(self, submodule, search_cache_path):
        if self.search_submodule_cache_path != "" and os.path.exists(self.search_submodule_cache_path):
            if self.search_submodule_cache_path not in self.temp_files:
                self.temp_files.append(self.search_submodule_cache_path)

        self.search_submodule_cache_path = search_cache_path
        self.buffer_widget.eval_js_function("updateSubmoduleInfo", submodule, True)

    def fetch_branch_info(self):
        thread = FetchBranchThread(self.repo)
        thread.fetch_result.connect(self.update_branch_info)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def update_branch_info(self, branch_list, remote_branch):
        self.update_branch_list(branch_list, remote_branch)

    @interactive
    def search(self):
        if self.nav_current_item == "Log":
            self.search_log_count = 0
            self.send_input_message("Search log: ", "search_log", "search")
        elif self.nav_current_item == "Submodule":
            self.search_submodule_count = 0
            self.send_input_message("Search submodule: ", "search_submodule", "search")

    def search_match_lines(self, search_string, cache_file_path):
        import subprocess

        command = "rg '{}' {} --color='never' --line-number --smart-case -o --replace=''".format(search_string, cache_file_path)
        result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE)

        return list(map(lambda x: int(x[:-1]) - 1, result.stdout.split()))

    def handle_search_log(self, search_string):
        in_minibuffer = get_emacs_func_result("minibufferp", [])

        if in_minibuffer:
            self.search_log_count += 1
            count = self.search_log_count
            QTimer().singleShot(300, lambda : self.try_search_log(count, search_string))
        else:
            self.buffer_widget.eval_js_function("searchLogsFinish")

    def handle_search_submodule(self, search_string):
        in_minibuffer = get_emacs_func_result("minibufferp", [])

        if in_minibuffer:
            self.search_submodule_count += 1
            count = self.search_submodule_count
            QTimer().singleShot(300, lambda : self.try_search_submodule(count, search_string))
        else:
            self.buffer_widget.eval_js_function("searchSubmodulesFinish")

    def try_search_log(self, count, search_string):
        if count == self.search_log_count and search_string.strip() != "":
            if self.search_log_cache_path and os.path.exists(self.search_log_cache_path):
                self.buffer_widget.eval_js_function("searchLogsStart",
                    search_string,
                    self.search_match_lines(search_string, self.search_log_cache_path))

    def try_search_submodule(self, count, search_string):
        if count == self.search_submodule_count and search_string.strip() != "":
            if self.search_submodule_cache_path and os.path.exists(self.search_submodule_cache_path):
                self.buffer_widget.eval_js_function(
                    "searchSubmodulesStart",
                    search_string,
                    self.search_match_lines(search_string, self.search_submodule_cache_path))

    @PostGui()
    def handle_search_forward(self, callback_tag):
        if callback_tag == "search_log":
            self.buffer_widget.eval_js_function("searchLogsJumpNext")
        elif callback_tag == "search_submodule":
            self.buffer_widget.eval_js_function("searchSubmodulesJumpNext")

    @PostGui()
    def handle_search_backward(self, callback_tag):
        if callback_tag == "search_log":
            self.buffer_widget.eval_js_function("searchLogsJumpPrev")
        elif callback_tag == "search_submodule":
            self.buffer_widget.eval_js_function("searchSubmodulesJumpPrev")

    @PostGui()
    def handle_search_finish(self, callback_tag):
        if callback_tag == "search_log":
            self.buffer_widget.eval_js_function("searchLogsFinish")
        elif callback_tag == "search_submodule":
            self.buffer_widget.eval_js_function("searchSubmodulesFinish")

    @QtCore.pyqtSlot()
    def status_copy_change_files_to_mirror_repo(self):
        status = list(filter(lambda info: info[1] != GIT_STATUS_IGNORED, list(self.repo.status().items())))

        if len(status) > 0:
            self.send_input_message("Copy changes file to: ", "copy_changes_file_to_mirror", "file", self.repo_root)
        else:
            message_to_emacs("No file need submitted, nothing to copy.")

    @QtCore.pyqtSlot()
    def status_fetch_pr(self):
        remote_default = next(self.repo.config.get_multivar("remote.pushdefault"), "origin")
        origin_url = get_git_https_url(self.repo.remotes[remote_default].url)

        message_to_emacs("Fetch PR list...")

        thread = FetchPrListThread(origin_url)
        thread.fetch_result.connect(self.read_pr)
        self.thread_reference_list.append(thread)
        thread.start()

    @QtCore.pyqtSlot(list)
    def read_pr(self, pr_list):
        if len(pr_list) > 0:
            self.pr_ids = []
            self.pr_names = []
            for pr in pr_list:
                self.pr_ids.append(pr[0])
                self.pr_names.append(pr[1])

            self.send_input_message("Fetch pull request, please input PR number: ", "fetch_pr", "list", completion_list=self.pr_names)
        else:
            message_to_emacs("No PR found in repo.")

    def handle_fetch_pr(self, pr_name):
        try:
            pr_number = self.pr_ids[self.pr_names.index(pr_name)]

            message_to_emacs("Fetch PR {} ...".format(pr_number))

            get_command_result("cd {}; git fetch origin pull/{}/head:pr_{} && git checkout pr_{}".format(
                self.repo_root,
                pr_number,
                pr_number,
                pr_number))

            self.update_git_info()

            message_to_emacs("Fetch PR {} done.".format(pr_number))
        except:
            message_to_emacs("Input wrong PR: {}".format(pr_name))

    @QtCore.pyqtSlot()
    def remote_copy_url(self):
        remote_default = next(self.repo.config.get_multivar("remote.pushdefault"), "origin")
        origin_url = get_git_https_url(self.repo.remotes[remote_default].url)

        eval_in_emacs('kill-new', [origin_url])
        message_to_emacs("Copy {}".format(origin_url))

    @QtCore.pyqtSlot(str)
    def send_message_to_emacs(self, message):
        message_to_emacs(message)

    @PostGui()
    def handle_input_response(self, callback_tag, result_content):
        from inspect import signature

        handle_function_name = "handle_{}".format(callback_tag)
        if hasattr(self, handle_function_name):
            handle_function = getattr(self, handle_function_name)
            function_argument_number = len(signature(getattr(self, handle_function_name)).parameters)

            if function_argument_number == 1:
                handle_function(result_content)
            else:
                handle_function()

    @PostGui()
    def cancel_input_response(self, callback_tag):
        ''' Cancel input message.'''
        if callback_tag == "search_log":
            self.buffer_widget.eval_js_function("searchLogsCancel")
        elif callback_tag == "search_submodule":
            self.buffer_widget.eval_js_function("searchSubmodulesCancel")

    def handle_copy_changes_file_to_mirror(self, target_repo_dir):
        current_repo_last_commit_id = self.last_commit_id
        target_repo_last_commit_id = str(Repository(target_repo_dir).head.target)

        if target_repo_last_commit_id == current_repo_last_commit_id:
            status = list(filter(lambda info: info[1] != GIT_STATUS_IGNORED, list(self.repo.status().items())))

            for (file, file_type) in status:
                if file_type == GIT_STATUS_WT_DELETED:
                    os.remove(os.path.join(target_repo_dir, file))
                else:
                    target_file = os.path.join(target_repo_dir, file)
                    if not os.path.exists(target_file):
                        os.makedirs(os.path.dirname(target_file), exist_ok=True)

                    shutil.copy(os.path.join(self.repo_root, file), target_file)

            message_to_emacs("Update {} files to {}".format(len(status), os.path.join(target_repo_dir)))
        else:
            message_to_emacs("{} last commit is not same as current repo, stop copy files.".format(target_repo_dir))

    @QtCore.pyqtSlot(str)
    def show_commit_diff(self, commit_id):
        commit = self.repo.revparse_single(commit_id)
        parent_commits = commit.parents
        if len(parent_commits) > 0:
            eval_in_emacs("eaf-git-show-commit-diff", [self.repo.diff(parent_commits[0], commit).patch])
        else:
            eval_in_emacs("eaf-git-show-commit-diff", [commit.tree.diff_to_tree(swap=True).patch])

    @QtCore.pyqtSlot(str)
    def log_revert_commit(self, commit_id):
        self.revert_commit = self.repo.revparse_single(commit_id)
        self.send_input_message("Revert commit '{}' {}".format(commit_id, bytes_decode(self.revert_commit.raw_message)), "log_revert_commit", "yes-or-no")

    def handle_log_revert_commit(self):
        head = self.repo.head.peel()
        try:
            revert_index = self.repo.revert_commit(self.revert_commit, head)
        except:
            # When revert commit is merge commit, we need set mainline with 1 to make sure revert successfully.
            revert_index = self.repo.revert_commit(self.revert_commit, head, 1)

        parent, ref = self.repo.resolve_refish(refish=self.repo.head.name)
        commit_message = bytes_decode(self.revert_commit.raw_message)
        self.repo.create_commit(
            ref.name,
            self.repo.default_signature,
            self.repo.default_signature,
            "Revert {}".format(commit_message),
            revert_index.write_tree(),
            [parent.oid if hasattr(parent, "oid") else parent.id])
        self.fetch_unpush_info()
        self.fetch_status_info()
        self.fetch_log_info()
        message_to_emacs("Revert commit: {} {} ".format(self.revert_commit.id, commit_message))

    @QtCore.pyqtSlot(str)
    def log_revert_to(self, commit_id):
        self.revert_to_commit = self.repo.revparse_single(commit_id)
        self.send_input_message("Revert to commit '{}' {}".format(
            commit_id,
            bytes_decode(self.revert_to_commit.raw_message).splitlines()[0]), "log_revert_to_commit", "yes-or-no")

    def handle_log_revert_to_commit(self):
        short_commit_id = str(self.revert_to_commit.id)[:7]
        revert_to_message = bytes_decode(self.revert_to_commit.raw_message).splitlines()[0]
        result = get_command_result("cd {}; git revert --no-edit -n {}..HEAD".format(self.repo_root, short_commit_id))

        if result == "":
            revert_message = "Revert to commit: {} {}".format(short_commit_id, revert_to_message)
            get_command_result("cd {}; git commit -m '{}'".format(self.repo_root, revert_message))
            message_to_emacs(revert_message)
        else:
            message_to_emacs("Failed to revert to commit: {} reason: {}".format(self.revert_to_commit.id, result))

        self.fetch_unpush_info()
        self.fetch_status_info()
        self.fetch_log_info()

    @QtCore.pyqtSlot(str, str)
    def log_reset_last(self, commit_id, commit_message):
        self.log_commit_reset_last_id = commit_id
        self.send_input_message("Reset last commit '{}' with mode: ".format(commit_message), "log_reset_last", "list", completion_list=["mixed", "soft", "hard"])

    def handle_log_reset_last(self, mode):
        reset_type = pygit2.GIT_RESET_MIXED

        if mode == "soft":
            reset_type = pygit2.GIT_RESET_SOFT
        elif mode == "hard":
            reset_type = pygit2.GIT_RESET_HARD

        commit = self.repo.revparse_single(self.log_commit_reset_last_id)
        parent_commits = commit.parents
        if len(parent_commits) > 0:
            self.repo.reset(parent_commits[0].id, reset_type)

            self.fetch_log_info()
            self.fetch_status_info()
            self.fetch_unpush_info()
            self.fetch_stash_info()

            last_commit = self.repo.revparse_single(str(self.repo.head.target))
            message_to_emacs("Current HEAD is: {}".format(bytes_decode(last_commit.raw_message)).splitlines()[0])

    @QtCore.pyqtSlot(str, str)
    def log_reset_to(self, commit_id, commit_message):
        self.log_commit_reset_to_id = commit_id
        self.log_commit_reset_to_message = commit_message
        self.send_input_message("Reset to commit '{}' with mode: ".format(commit_message), "log_reset_last", "list", completion_list=["mixed", "soft", "hard"])

    def handle_log_reset_to(self, mode):
        reset_type = pygit2.GIT_RESET_MIXED

        if mode == "soft":
            reset_type = pygit2.GIT_RESET_SOFT
        elif mode == "hard":
            reset_type = pygit2.GIT_RESET_HARD

        self.repo.reset(self.log_commit_reset_to_id, reset_type)

        self.fetch_log_info()
        self.fetch_status_info()
        self.fetch_unpush_info()
        self.fetch_stash_info()

        message_to_emacs("Current HEAD is: {}".format(self.log_commit_reset_to_message))

    @QtCore.pyqtSlot()
    def log_merge_branch(self):
        self.send_input_message("Select merge method: ", "log_select_merge_method", "list", completion_list=["merge", "rebase", "squash"])

    def handle_log_select_merge_method(self, method):
        self.merge_method = method
        branches = self.repo.listall_branches()
        self.send_input_message("Merge in {} mode from Branch: ".format(self.merge_method), "log_merge_branch", "list", completion_list=branches)

    def handle_log_merge_branch(self, branch_name):
        if branch_name == self.repo.head.shorthand:
            message_to_emacs("Can't merge branch self.")
        else:
            # normal merge a branch
            merge_branch = self.repo.lookup_branch(branch_name)
            current_branch = self.repo.lookup_branch(self.repo.head.shorthand)
            result = "Merge commits in {} mode from branch {} to {}".format(
                self.merge_method,
                merge_branch.name,
                current_branch.name
            )
            try:
                if self.merge_method == "merge":
                    self.repo.merge(merge_branch.target)
                    tree = self.repo.index.write_tree()
                    self.repo.create_commit(
                        current_branch.name,
                        self.repo.default_signature,
                        self.repo.default_signature,
                        "Merge branch {}".format(branch_name),
                        tree,
                        [current_branch.target, merge_branch.target])
                elif self.merge_method == "rebase":
                    # rebase and merge a branch.
                    self.repo.checkout(current_branch)
                    result = get_command_result("cd {}; git rebase {}".format(self.repo_root, merge_branch.name))
                elif self.merge_method == "squash":
                    # merge a branch and squash target all commits into one commit.
                    merge_base = self.repo.merge_base(current_branch.target, merge_branch.target)
                    current_branch_tree = self.repo.get(current_branch.target).tree
                    merge_branch_tree = self.repo.get(merge_branch.target).tree
                    merge_base_tree = self.repo.get(merge_base).tree
                    self.repo.checkout(current_branch)
                    index = self.repo.merge_trees(merge_base_tree, current_branch_tree, merge_branch_tree)
                    tree = index.write_tree(self.repo)
                    commit = self.repo.create_commit(
                        current_branch.name,
                        self.repo.default_signature,
                        self.repo.default_signature,
                        "Squash merge branch {}".format(branch_name),
                        tree,
                        [current_branch.target])
                    self.repo.reset(commit, pygit2.GIT_RESET_HARD)
                else:
                    message_to_emacs("Unknown merge method.")
                    return
            except Exception as err:
                result = "Failed to merge commits in {} mode from branch {} to {}, Error: {}".format(
                    self.merge_method,
                    merge_branch.name,
                    current_branch.name,
                    err
                )
            self.fetch_log_info()
            message_to_emacs(result)

    @QtCore.pyqtSlot(int)
    def show_stash_diff(self, stash_index):
        stash_item = "stash@" + "{" + str(stash_index) + "}"
        eval_in_emacs("eaf-git-show-commit-diff", [self.repo.diff("{}^".format(stash_item), stash_item).patch])

    @QtCore.pyqtSlot(int, str)
    def stash_apply(self, index, message):
        self.stash_apply_index = index
        self.stash_apply_message = message
        self.send_input_message("Stash apply '{}'".format(message), "stash_apply", "yes-or-no")

    @QtCore.pyqtSlot(int, str)
    def stash_drop(self, index, message):
        self.stash_drop_index = index
        self.stash_drop_message = message
        self.send_input_message("Stash drop '{}'".format(message), "stash_drop", "yes-or-no")

    @QtCore.pyqtSlot(int, str)
    def stash_pop(self, index, message):
        self.stash_pop_index = index
        self.stash_pop_message = message
        self.send_input_message("Stash pop '{}'".format(message), "stash_pop", "yes-or-no")

    def handle_stash_apply(self):
        self.repo.stash_apply(index=self.stash_apply_index)
        message_to_emacs("Stash apply '{}'".format(self.stash_apply_message))

        self.fetch_stash_info()
        self.fetch_status_info()

    def handle_stash_drop(self):
        self.repo.stash_drop(index=self.stash_drop_index)
        message_to_emacs("Stash drop '{}'".format(self.stash_drop_message))

        self.fetch_stash_info()
        self.fetch_status_info()

    def handle_stash_pop(self):
        self.repo.stash_pop(index=self.stash_pop_index)
        message_to_emacs("Stash pop '{}'".format(self.stash_pop_message))

        self.fetch_stash_info()
        self.fetch_status_info()

    def highlight_diff(self, content):
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import guess_lexer

        return highlight(content, guess_lexer(content), HtmlFormatter(full=True, style=self.highlight_style))

    def highlight_diff_strict(self, content):
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import DiffLexer

        return highlight(content, DiffLexer(), HtmlFormatter(full=True, style=self.highlight_style))

    @QtCore.pyqtSlot(str, str)
    def update_diff(self, type, file):
        import time
        tick = time.time()

        self.diff_type = type
        self.diff_file = file
        self.diff_tick = tick
        thread = HighlightDiffThread(self, type, file, tick)
        thread.fetch_result.connect(self.render_diff)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def render_diff(self, type, file, tick, diff_string, patch_set):
        if self.diff_type == type and self.diff_file == file and self.diff_tick == tick:
            self.buffer_widget.eval_js_function("updateChangeDiff", type, {"diff": diff_string, "patch_set": patch_set})

    @QtCore.pyqtSlot()
    def status_commit_stage(self):
        if len(self.stage_status) > 0:
            self.send_input_message("Commit stage files with message: ", "commit_stage_files")
        else:
            message_to_emacs("No stage files found, please stage file first.")

    @QtCore.pyqtSlot()
    def status_commit_all(self):
        self.send_input_message("Commit all files with message: ", "commit_all_files")

    @QtCore.pyqtSlot()
    def status_commit_and_push(self):
        self.send_input_message("Commit all files and push with message: ", "commit_and_push")

    @QtCore.pyqtSlot()
    def status_commit_and_push_with_ollama(self):
        import shutil

        if shutil.which("ollama"):
            self.send_input_message("Commit all files and push with message: ", "commit_and_push")

            thread = ParseGitDiffThread(self.url)
            thread.fetch_result.connect(self.handle_status_commit_and_push_with_ollama)
            self.thread_reference_list.append(thread)
            thread.start()
        else:
            message_to_emacs("You need to install ollama in order to use AI to generate git commits")

    @PostGui()
    def handle_status_commit_and_push_with_ollama(self, patch_name):
        eval_in_emacs("eaf-git-insert-commit-name", [patch_name])

    @QtCore.pyqtSlot()
    def status_commit_and_push_with_hooks(self):
        self.send_input_message("Commit all files and push with message: ", "commit_and_push")

        eval_in_emacs("eaf-git-run-commit-and-push-hook", [])

    @QtCore.pyqtSlot(str, int)
    def status_view_file(self, type, file_index):
        if type == "untrack":
            if file_index == -1:
                message_to_emacs("Please select file to view.")
            else:
                self.status_open_file(self.untrack_status[file_index]["file"])
        elif type == "unstage":
            if file_index == -1:
                message_to_emacs("Please select file to view.")
            else:
                self.status_open_file(self.unstage_status[file_index]["file"])
        elif type == "stage":
            if file_index == -1:
                message_to_emacs("Please select file to view.")
            else:
                self.status_open_file(self.stage_status[file_index]["file"])

    def status_open_file(self, filename):
        filepath = os.path.join(self.repo_root, filename)

        if os.path.isdir(filepath):
            eval_in_emacs('eaf-open-in-file-manager', [filepath])
        else:
            eval_in_emacs("find-file", [filepath])

    @QtCore.pyqtSlot(str, int)
    def status_stage_file(self, type, file_index):
        if type == "untrack":
            if file_index == -1:
                self.stage_untrack_files()
            else:
                self.stage_untrack_file(self.untrack_status[file_index])
        elif type == "unstage":
            if file_index == -1:
                self.stage_unstage_files()
            else:
                self.stage_unstage_file(self.unstage_status[file_index])
        elif type == "stage":
            if file_index == -1:
                self.unstage_staged_files()
            else:
                self.unstage_staged_file(self.stage_status[file_index])

    @QtCore.pyqtSlot(str, int, int)
    def status_delete_hunk(self, type, patch_index, hunk_index):
        if patch_index >= 0 and hunk_index >= 0:
            self.patch_index = patch_index
            self.hunk_index = hunk_index
            if type == "unstage":
                self.send_input_message("Discard this unstage hunk", "discard_unstage_hunk", "yes-or-no")
            elif type == "stage":
                self.send_input_message("Discard this stage hunk", "discard_stage_hunk", "yes-or-no")
        else:
            message_to_emacs("Please select an valid hunk.")

    def handle_discard_unstage_hunk(self):
        patch = copy(self.raw_patch_set[self.patch_index])
        hunk = patch[self.hunk_index]
        hunk_str = str(hunk)

        # Add diff header
        hunk_str = f"diff --git a/{patch.path} b/{patch.path}\nindex 1234567..89abcdef 100644\n--- a/{patch.path}\n+++ b/{patch.path}\n{hunk_str}"
        result = get_command_result("cd {}; git apply --reverse".format(self.repo_root), hunk_str)

        if result == "":
            message_to_emacs("Discard unstage hunk successfully!")
        else:
            message_to_emacs("Failed to discard this unstage hunk! {}".format(result))

        self.fetch_status_info(True)

    def handle_discard_stage_hunk(self):
        patch = copy(self.raw_patch_set[self.patch_index])
        hunk = patch[self.hunk_index]
        hunk_str = str(hunk)

        # Add diff header
        hunk_str = f"diff --git a/{patch.path} b/{patch.path}\nindex 1234567..89abcdef 100644\n--- a/{patch.path}\n+++ b/{patch.path}\n{hunk_str}"
        result = get_command_result("cd {}; git apply --reverse --cached".format(self.repo_root), hunk_str)
        if result == "":
            get_command_result("cd {}; git update-index --refresh")
            result = get_command_result("cd {}; git apply --reverse".format(self.repo_root), hunk_str)

        if result == "":
            message_to_emacs("Discard this stage hunk successfully!")
        else:
            message_to_emacs("Failed to discard this stage hunk! {}".format(result))

        self.fetch_status_info(True)

    @QtCore.pyqtSlot(str, int, int)
    def status_manage_hunk(self, type, patch_index, hunk_index):
        if patch_index >= 0 and hunk_index >= 0:
            if type == "unstage":
                self.stage_unstage_hunk(patch_index, hunk_index)
            elif type == "stage":
                self.unstage_stage_hunk(patch_index, hunk_index)
        else:
            message_to_emacs("Please select an valid hunk.")

    def git_add_file(self, path):
        index = self.repo.index

        try:
            expand_path = os.path.join(self.repo_root, path)
            if os.path.exists(expand_path):
                index.add(path)
            else:
                index.remove(path)

            index.write()
        except Exception:
            import traceback
            message_to_emacs(traceback.format_exc())

    def git_reset_file(self, path):
        index = self.repo.index

        # Remove path from the index
        if path in index:
            index.remove(path)

        # Restore object from db
        # Use try because the file can be untrack, so there's no HEAD info for it
        try:
            obj = self.repo.revparse_single('HEAD').tree[path] # Get object from db
            index.add(IndexEntry(path, obj.id, obj.filemode)) # Add to index
        except KeyError:
            pass

        # Write index
        index.write()

    def git_checkout_file(self, paths=[]):
        checkout_file_paths = list(map(lambda p: os.path.join(self.repo_root, p), paths))

        self.repo.checkout(self.repo.lookup_reference(self.repo.head.name), paths=paths, strategy=GIT_CHECKOUT_FORCE)

        eval_in_emacs("eaf-git-checkout-files", [checkout_file_paths])

    def git_checkout_branch(self, branch_name):
        branch = self.repo.lookup_branch(branch_name)
        ref = self.repo.lookup_reference(branch.name)
        self.repo.checkout(ref)

    def stage_unstage_hunk(self, patch_index, hunk_index):
        self.apply_hunk(patch_index, hunk_index)

    def unstage_stage_hunk(self, patch_index, hunk_index):
        self.apply_hunk(patch_index, hunk_index, revert=True)

    def apply_hunk(self, patch_index, hunk_index, revert=False):
        index = self.repo.index
        path = self.raw_patch_set[patch_index].path
        blob_id = index[path].id
        blob_data = self.repo[blob_id].data

        hunk = self.raw_patch_set[patch_index][hunk_index]

        if revert:
            revert_hunk = Hunk(
                src_start=hunk.target_start,
                src_len=hunk.target_length,
                tgt_start=hunk.source_start,
                tgt_len=hunk.source_length,
                section_header=hunk.section_header)
            for line in hunk:
                new_line = copy(line)
                new_line.source_line_no, new_line.target_line_no = new_line.target_line_no, new_line.source_line_no
                new_line.line_type = LINE_TYPE_ADDED if line.is_removed else LINE_TYPE_REMOVED if line.is_added else LINE_TYPE_CONTEXT
                revert_hunk.append(new_line)
            hunk = revert_hunk

        new_content = StringIO()
        new_content.writelines(patch_stream(StringIO(bytes_decode(blob_data)), [hunk]))
        new_id = self.repo.write(pygit2.GIT_OBJ_BLOB, new_content.getvalue())
        new_entry = IndexEntry(path, new_id, pygit2.GIT_FILEMODE_BLOB)
        index.add(new_entry)
        index.write()
        self.fetch_status_info(True)

    def stage_untrack_files(self):
        untrack_status = self.untrack_status

        for file_info in untrack_status:
            self.git_add_file(file_info["file"])

        self.fetch_status_info(True)

    def stage_unstage_files(self):
        unstage_status = self.unstage_status

        for file_info in unstage_status:
            self.git_add_file(file_info["file"])

        self.fetch_status_info(True)

    def unstage_staged_files(self):
        stage_status = self.stage_status

        for file_info in stage_status:
            self.git_reset_file(file_info["file"])

        self.fetch_status_info(True)

    def stage_untrack_file(self, file_info):
        untrack_status = self.untrack_status
        unstage_status = self.unstage_status
        stage_status = self.stage_status
        refresh_status = False

        self.git_add_file(file_info["file"])

        if not status_is_include(stage_status, file_info):
            stage_status.append(file_info)
        untrack_file_index = untrack_status.index(file_info)
        untrack_status.remove(file_info)

        select_item_type = ""
        select_item_index = -1
        if len(untrack_status) > 0:
            select_item_type = "untrack"
            select_item_index = max(untrack_file_index - 1, 0)
        elif len(unstage_status) > 0:
            select_item_type = "unstage"
        else:
            select_item_type = "stage"

        self.buffer_widget.eval_js_function("updateSelectInfo", stage_status, unstage_status, untrack_status, select_item_type, select_item_index)

        if refresh_status:
            self.fetch_status_info()

    def stage_unstage_file(self, file_info):
        untrack_status = self.untrack_status
        unstage_status = self.unstage_status
        stage_status = self.stage_status
        refresh_status = False

        self.git_add_file(file_info["file"])

        if status_is_include(stage_status, file_info):
            refresh_status = True
        else:
            stage_status.append(file_info)
        unstage_file_index = unstage_status.index(file_info)
        unstage_status.remove(file_info)

        select_item_type = ""
        select_item_index = -1
        if len(unstage_status) > 0:
            select_item_type = "unstage"
            select_item_index = max(unstage_file_index - 1, 0)
        else:
            select_item_type = "stage"

        self.buffer_widget.eval_js_function("updateSelectInfo", stage_status, unstage_status, untrack_status, select_item_type, select_item_index)

        if refresh_status:
            self.fetch_status_info()

    def unstage_staged_file(self, file_info):
        untrack_status = self.untrack_status
        unstage_status = self.unstage_status
        stage_status = self.stage_status
        refresh_status = False

        self.git_reset_file(file_info["file"])

        stage_file_index = 0

        # Use try to get the type of file after unstaging
        try:
            self.repo.revparse_single('HEAD').tree[file_info["file"]]
        except KeyError:
            if status_is_include(untrack_status, file_info):
                refresh_status = True
            else:
                untrack_status.append(file_info)
        else:
            if status_is_include(unstage_status, file_info):
                refresh_status = True
            else:
                unstage_status.append(file_info)

        stage_file_index = stage_status.index(file_info)
        stage_status.remove(file_info)

        select_item_type = ""
        select_item_index = -1
        if len(stage_status) > 0:
            select_item_type = "stage"
            select_item_index = max(stage_file_index - 1, 0)
        elif len(unstage_status) > 0:
            select_item_type = "unstage"
        elif len(untrack_status) > 0:
            select_item_type = "untrack"

        self.buffer_widget.eval_js_function("updateSelectInfo", stage_status, unstage_status, untrack_status, select_item_type, select_item_index)

        if refresh_status:
            self.fetch_status_info()

    @QtCore.pyqtSlot(str, int)
    def status_delete_file(self, type, file_index):
        if type == "untrack":
            if file_index == -1:
                self.send_input_message("Discard untracked files?", "delete_untrack_files", "yes-or-no")
            else:
                self.delete_untrack_file(self.untrack_status[file_index])
        elif type == "unstage":
            if file_index == -1:
                self.send_input_message("Discard unstaged files?", "delete_unstage_files", "yes-or-no")
            else:
                self.delete_unstage_file(self.unstage_status[file_index])
        elif type == "stage":
            if file_index == -1:
                self.send_input_message("Discard staged files?", "delete_stage_files", "yes-or-no")
            else:
                self.delete_stage_file(self.stage_status[file_index])

    def delete_untrack_file(self, file_info):
        self.delete_untrack_mark_file = file_info
        self.send_input_message("Discard untracked changes in {}?".format(file_info["file"]), "delete_untrack_file", "yes-or-no")

    def delete_unstage_file(self, file_info):
        self.delete_unstage_mark_file = file_info
        self.send_input_message("Discard unstaged changes in {}?".format(file_info["file"]), "delete_unstage_file", "yes-or-no")

    def delete_stage_file(self, file_info):
        self.delete_stage_mark_file = file_info
        self.send_input_message("Discard staged changes in {}?".format(file_info["file"]), "delete_stage_file", "yes-or-no")

    def handle_delete_untrack_files(self):
        untrack_status = self.untrack_status
        unstage_status = self.unstage_status
        stage_status = self.stage_status

        delete_file_number = len(self.untrack_status)

        for untrack_file in self.untrack_status:
            untrack_path = os.path.join(self.repo_root, untrack_file["file"])
            os.remove(untrack_path)
            self.clean_dir_without_files(untrack_path)

        untrack_status = []

        select_item_type = ""
        select_item_index = -1
        if len(unstage_status) > 0:
            select_item_type = "unstage"
        else:
            select_item_type = "stage"

        self.buffer_widget.eval_js_function("updateSelectInfo", stage_status, unstage_status, untrack_status, select_item_type, select_item_index)

        if delete_file_number > 1:
            message_to_emacs("Delete {} files.".format(delete_file_number))
        else:
            message_to_emacs("Delete 1 file.")

    def handle_delete_unstage_files(self):
        untrack_status = self.untrack_status
        unstage_status = self.unstage_status
        stage_status = self.stage_status

        for file_info in unstage_status:
            self.git_checkout_file([file_info["file"]])

        unstage_status = []

        select_item_type = ""
        select_item_index = -1
        if len(untrack_status) > 0:
            select_item_type = "untrack"
        else:
            select_item_type = "stage"

        self.buffer_widget.eval_js_function("updateSelectInfo", stage_status, unstage_status, untrack_status, select_item_type, select_item_index)

    def handle_delete_stage_files(self):
        untrack_status = self.untrack_status
        unstage_status = self.unstage_status
        stage_status = self.stage_status

        for file_info in stage_status:
            self.git_reset_file(file_info["file"])
            self.git_checkout_file([file_info["file"]])

        stage_status = []

        select_item_type = ""
        select_item_index = -1
        if len(unstage_status) > 0:
            select_item_type = "unstage"
        elif len(untrack_status) > 0:
            select_item_type = "untrack"

        self.buffer_widget.eval_js_function("updateSelectInfo", stage_status, unstage_status, untrack_status, select_item_type, select_item_index)

    def handle_commit_stage_files(self, message):
        self.handle_commit(message)
        self.fetch_unpush_info()
        self.fetch_log_info()

        untrack_status = self.untrack_status
        unstage_status = self.unstage_status
        stage_status = self.stage_status

        stage_status = []

        select_item_type = ""
        select_item_index = -1
        if len(unstage_status) > 0:
            select_item_type = "unstage"
        elif len(untrack_status) > 0:
            select_item_type = "untrack"

        self.buffer_widget.eval_js_function("updateSelectInfo", stage_status, unstage_status, untrack_status, select_item_type, select_item_index)

        message_to_emacs("Commit stage files with: {}".format(message))

    def handle_commit_all_files(self, message):
        try:
            self.repo.index.add_all()
            self.repo.index.write()
            self.handle_commit(message)

            self.fetch_unpush_info()
            self.fetch_log_info()
            self.fetch_submodule_info()

            self.buffer_widget.eval_js_function("updateSelectInfo", [], [], [], "", -1)

            message_to_emacs("Commit stage files with: {}".format(message))

            return True
        except pygit2.GitError:
            import traceback
            message_to_emacs(traceback.format_exc())

        return False

    def handle_commit(self, message):
        tree = self.repo.index.write_tree()
        # Used for the case with no-commit-repo
        parent = []
        ref = 'refs/heads/master'

        try:
            parent, ref = self.repo.resolve_refish(refish=self.repo.head.name)
            parent = [parent.oid if hasattr(parent, "oid") else parent.id]
            ref = ref.name
        except GitError:
            pass

        self.repo.create_commit(
            ref,
            self.repo.default_signature,
            self.repo.default_signature,
            message,
            tree,
            parent)

    def handle_commit_and_push(self, message):
        if self.handle_commit_all_files(message):
            self.status_push()

    def clean_dir_without_files(self, begin_path):
        # only clean directory inside repo directory.
        begin_path = os.path.abspath(begin_path)
        if not begin_path.startswith(self.repo_root) or begin_path == self.repo_root:
            return

        begin_dir = os.path.dirname(begin_path) if os.path.isfile(begin_path) else begin_path
        if os.path.exists(begin_dir):
            for _, _, files in os.walk(begin_dir, topdown=False):
                if files:
                    return
            shutil.rmtree(begin_dir, ignore_errors=True)

        self.clean_dir_without_files(os.path.dirname(begin_dir))

    def handle_delete_untrack_file(self):
        untrack_status = self.untrack_status
        unstage_status = self.unstage_status
        stage_status = self.stage_status

        untrack_file_index = untrack_status.index(self.delete_untrack_mark_file)
        untrack_status.remove(self.delete_untrack_mark_file)
        untrack_path = os.path.join(self.repo_root, self.delete_untrack_mark_file["file"])
        os.remove(untrack_path)
        self.clean_dir_without_files(untrack_path)

        select_item_type = ""
        select_item_index = -1
        if len(untrack_status) > 0:
            select_item_type = "untrack"
            select_item_index = max(untrack_file_index - 1, 0)
        elif len(unstage_status) > 0:
            select_item_type = "unstage"
        else:
            select_item_type = "stage"

        self.buffer_widget.eval_js_function("updateSelectInfo", stage_status, unstage_status, untrack_status, select_item_type, select_item_index)

        message_to_emacs("Delete file {}".format(self.delete_untrack_mark_file["file"]))

    def handle_delete_unstage_file(self):
        untrack_status = self.untrack_status
        unstage_status = self.unstage_status
        stage_status = self.stage_status

        self.git_checkout_file([self.delete_unstage_mark_file["file"]])

        unstage_file_index = unstage_status.index(self.delete_unstage_mark_file)
        unstage_status.remove(self.delete_unstage_mark_file)

        select_item_type = ""
        select_item_index = -1
        if len(unstage_status) > 0:
            select_item_type = "unstage"
            select_item_index = max(unstage_file_index - 1, 0)
        else:
            select_item_type = "stage"

        self.buffer_widget.eval_js_function("updateSelectInfo", stage_status, unstage_status, untrack_status, select_item_type, select_item_index)

    def handle_delete_stage_file(self):
        untrack_status = self.untrack_status
        unstage_status = self.unstage_status
        stage_status = self.stage_status

        self.git_reset_file(self.delete_stage_mark_file["file"])
        self.git_checkout_file([self.delete_stage_mark_file["file"]])

        stage_file_index = stage_status.index(self.delete_stage_mark_file)
        stage_status.remove(self.delete_stage_mark_file)

        select_item_type = ""
        select_item_index = -1
        if len(stage_status) > 0:
            select_item_type = "stage"
            select_item_index = max(stage_file_index - 1, 0)
        elif len(unstage_status) > 0:
            select_item_type = "unstage"
        elif len(untrack_status) > 0:
            select_item_type = "untrack"

        self.buffer_widget.eval_js_function("updateSelectInfo", stage_status, unstage_status, untrack_status, select_item_type, select_item_index)

    @QtCore.pyqtSlot(list)
    def vue_update_stage_status(self, stage_status):
        self.stage_status = stage_status

    @QtCore.pyqtSlot(list)
    def vue_update_unstage_status(self, unstage_status):
        self.unstage_status = unstage_status

    @QtCore.pyqtSlot(list)
    def vue_update_untrack_status(self, untrack_status):
        self.untrack_status = untrack_status

    @QtCore.pyqtSlot(list)
    def vue_update_branch_status(self, branch_status):
        self.branch_status = branch_status

    @QtCore.pyqtSlot(str)
    def vue_update_nav_current_item(self, nav_current_item):
        self.nav_current_item = nav_current_item

    @QtCore.pyqtSlot()
    def status_pull(self):
        if not self.repo.head_is_unborn:
            message_to_emacs("Git pull {}...".format(self.repo.head.name))
        thread = GitPullThread(self.repo_root)
        thread.pull_result.connect(self.handle_status_pull)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def handle_status_pull(self, result):
        self.fetch_log_info()
        message_to_emacs("Git pull: {}".format(result.strip()))

    @QtCore.pyqtSlot()
    def status_push_branch(self):
        remote_branch_names = self.repo.listall_branches(GIT_BRANCH_REMOTE)
        self.send_input_message("Push remote: ", "status_push", "list", completion_list=remote_branch_names)

    def handle_status_push(self, remote):
        message_to_emacs("Git push {} to {}...".format(self.repo.head.name, remote))
        thread = GitPushThread(self.repo, self.repo_root, remote)
        thread.push_result.connect(self.handle_status_push_report)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def handle_status_push_report(self, message):
        self.fetch_unpush_info()
        self.fetch_log_info()

        message_to_emacs(message)

    @QtCore.pyqtSlot()
    def open_in_browser(self):
        remote_default = next(self.repo.config.get_multivar("remote.pushdefault"), "origin")
        origin_url = get_git_https_url(self.repo.remotes[remote_default].url)

        eval_in_emacs("eaf-open-browser", [origin_url])

    @QtCore.pyqtSlot()
    def status_push(self):
        self.handle_status_push("origin/{}".format(self.repo.head.shorthand))

    @QtCore.pyqtSlot()
    def status_checkout_all(self):
        self.send_input_message("Checkout all changes.", "checkout_all_files", "yes-or-no")

    @QtCore.pyqtSlot()
    def status_stash_push(self):
        self.send_input_message("Stash push with message: ", "stash_push")

    def handle_stash_push(self, message):
        try:
            self.repo.stash(self.repo.default_signature, message, include_untracked=True)

            self.fetch_status_info()
            self.fetch_stash_info()

            message_to_emacs("Stash push '{}'".format(message))
        except:
            message_to_emacs("There is nothing to stash")

    def handle_checkout_all_files(self):
        self.git_checkout_file()

        self.buffer_widget.eval_js_function("updateSelectInfo", [], [], [], "", -1)

        message_to_emacs("Checkout all.")

    @QtCore.pyqtSlot()
    def log_show_compare_branch(self):
        branches = self.repo.listall_branches()
        self.send_input_message("Show compare branch: ", "log_show_compare_branch", "list", completion_list=branches)

    @QtCore.pyqtSlot()
    def log_hide_compare_branch(self):
        self.log_compare_branch = ""
        self.buffer_widget.eval_js_function("updateCompareLogInfo", "", [])
        message_to_emacs("Hide compare branch.")

    @QtCore.pyqtSlot(list)
    def log_cherry_pick(self, commits):
        self.log_cherry_pick_commits = commits
        branches = self.repo.listall_branches()
        self.send_input_message("Copy commit to branch: ", "log_cherry_pick", "list", completion_list=branches)

    def handle_log_cherry_pick(self, new_branch):
        if new_branch == self.repo.head.shorthand:
            message_to_emacs("You can't copy commit to current branch.")
        else:
            current_branch_name = self.repo.head.shorthand

            self.git_checkout_branch(new_branch)

            for commit in self.log_cherry_pick_commits:
                cherry_id = Oid(hex=commit["id"])
                self.repo.cherrypick(cherry_id)

                if self.repo.index.conflicts is None:
                    tree_id = self.repo.index.write_tree()

                    cherry = self.repo.get(cherry_id)

                    parent, ref = self.repo.resolve_refish(refish=self.repo.head.name)
                    self.repo.create_commit(
                        ref.name,
                        self.repo.default_signature,
                        self.repo.default_signature,
                        cherry.message,
                        tree_id,
                        [ref.target])

                    self.repo.state_cleanup()

            try:
                self.git_checkout_branch(current_branch_name)

                self.fetch_log_info()
                if self.log_compare_branch != "":
                    self.handle_log_show_compare_branch(new_branch)

                if len(self.log_cherry_pick_commits) == 1:
                    message_to_emacs("Copy '{}' to branch {}".format(self.log_cherry_pick_commits[0]["message"], new_branch))
                else:
                    message_to_emacs("Copy {} commits to branch {}".format(len(self.log_cherry_pick_commits), new_branch))
            except pygit2.GitError:
                import traceback
                message_to_emacs(traceback.format_exc())

    def handle_log_show_compare_branch(self, branch):
        self.log_compare_branch = branch
        self.fetch_compare_log_info(branch)
        message_to_emacs("Show compare branch {}".format(branch))

    @QtCore.pyqtSlot(str)
    def log_commit_amend(self, commit_amend_id):
        self.commit_amend_id = commit_amend_id
        self.send_input_message("Commit amend to: ", "log_commit_amend", "string")

    def handle_log_commit_amend(self, new_message):
        self.repo.amend_commit(self.commit_amend_id, "HEAD", message=new_message)
        message_to_emacs("Commit to: {}".format(new_message))
        self.fetch_unpush_info()
        self.fetch_status_info()
        self.fetch_log_info()

    @QtCore.pyqtSlot()
    def branch_new(self):
        self.send_input_message("New branch: ", "new_branch")

    def handle_new_branch(self, branch_name):
        if branch_name in self.branch_status:
            message_to_emacs("Branch '{}' already exists.".format(branch_name))
        else:
            branch_list = self.branch_status
            branch_list.append({
                "index": len(self.branch_status),
                "name": branch_name,
                "foregroundColor": "",
                "backgroundColor": ""
            })

            self.repo.branches.local.create(branch_name, self.repo.revparse_single('HEAD'))
            self.update_local_branch_list(branch_list)

            message_to_emacs("Create branch '{}'.".format(branch_name))

    @QtCore.pyqtSlot(str)
    def branch_rename(self, branch_name):
        self.old_branch_name = branch_name
        self.send_input_message("Rename branch '{}' to: ".format(branch_name), "rename_branch", "string", branch_name)

    def handle_rename_branch(self, new_branch_name):
        if new_branch_name in self.branch_status:
            message_to_emacs("Branch '{}' already exists.".format(new_branch_name))
        else:
            old_branch = self.repo.branches.local.get(self.old_branch_name)
            if old_branch:
                old_branch.rename(new_branch_name)
                # After renaming branch, branch list need resort by branch name and date.
                # So fetch branch list again would better than update branch list dynamically.
                self.fetch_branch_info()
                message_to_emacs("Rename branch '{}' to '{}'.".format(self.old_branch_name, new_branch_name))
            else:
                message_to_emacs("Branch '{}' not found.".format(self.old_branch_name))

    @QtCore.pyqtSlot(str)
    def branch_delete(self, branch_name):
        self.delete_branch_name = branch_name
        self.send_input_message("Delete branch '{}': ".format(branch_name), "delete_branch", "yes-or-no")

    def handle_delete_branch(self):
        branch_list = self.branch_status

        for branch in branch_list:
            if branch["name"] == self.delete_branch_name:
                branch_list.remove(branch)
                break

        self.repo.branches.local.delete(self.delete_branch_name)

        self.update_local_branch_list(branch_list)

        message_to_emacs("Delete branch '{}'".format(self.delete_branch_name))

    def update_local_branch_list(self, local_branch_list):
        if not self.repo.head_is_unborn:
            self.buffer_widget.eval_js_function("updateLocalBranchInfo", self.repo.head.shorthand, local_branch_list)

    def update_branch_list(self, local_branch_list, remote_branch_list=[]):
        if not self.repo.head_is_unborn:
            self.buffer_widget.eval_js_function("updateBranchInfo", self.repo.head.shorthand, local_branch_list, remote_branch_list)

    @QtCore.pyqtSlot(str)
    def branch_switch(self, branch_name):
        # Tips
        # When switch the branch, the uncommitted changes will be copied over to the new branch.
        # However you cannot pull/fetch/rebase, unless you stash or commit.
        # Because Git will prevent that to stop from overwriting any uncommitted code.
        self.git_checkout_branch(branch_name)

        self.update_git_info()

        message_to_emacs("Switch to branch '{}'".format(branch_name))

    @QtCore.pyqtSlot(str)
    def submodule_view(self, module_path):
        eval_in_emacs('eaf-open-in-file-manager', [os.path.join(self.repo_root, module_path)])

    @QtCore.pyqtSlot(str)
    def submodule_open(self, module_path):
        eval_in_emacs('eaf-open', [os.path.join(self.repo_root, module_path), "git"])

    @QtCore.pyqtSlot()
    def submodule_add(self):
        self.send_input_message("Input submodule type: ", "select_submodule_type", "list", completion_list=["path", "url"])

    def handle_select_submodule_type(self, type):
        if type == "url":
            self.send_input_message("Add submodule url: ", "submodule_add_url")
        else:
            # git clone support local git repositiory.
            self.send_input_message("Add submodule repositiory: ", "submodule_add_url", "directory", self.repo_root)

    def handle_submodule_add_url(self, url):
        self.submodule_add_url = url
        self.send_input_message("Set submodule path: ", "submodule_add_path", "directory", self.repo_root)

    def handle_submodule_add_path(self, path):
        message_to_emacs("Add submodule {}...".format(self.submodule_add_url))
        thread = AddSubmoduleThread(self.repo, self.submodule_add_url, path)
        thread.finished.connect(self.handle_add_submodule_finish)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def handle_add_submodule_finish(self, url, path):
        message_to_emacs("Add submodule {} to {}".format(url, path))

        self.fetch_status_info()
        self.fetch_submodule_info()

    @QtCore.pyqtSlot(str)
    def submodule_remove(self, module_path):
        self.submodule_remove_path = module_path
        self.send_input_message("Remove submodule {} ?".format(module_path), "submodule_remove", "yes-or-no")

    def handle_submodule_remove(self):
        import configparser

        # Remove submodule path if submodule path exists in index.
        shutil.rmtree(os.path.join(self.repo_root, self.submodule_remove_path), ignore_errors=True)

        # git rm and write index.
        try:
            list(map(lambda entry: self.repo.index.remove(entry.path),
                    filter(lambda entry : entry.path == self.submodule_remove_path, self.repo.index)))
            self.repo.index.write()
        except KeyError:
            pass

        # Remove submodule path from .git/modules/ directory.
        shutil.rmtree(os.path.join(self.repo_root, ".git", "modules", self.submodule_remove_path), ignore_errors=True)

        # Update .gitmodules if submodule path in .gitmodules sections.
        mod_config = configparser.ConfigParser()
        gitmodules_path = os.path.join(self.repo_root, ".gitmodules")
        mod_config.read(gitmodules_path)
        for section in mod_config.sections():
            if mod_config[section].get("path") == self.submodule_remove_path:
                mod_config.remove_section(section)

        with open(gitmodules_path, 'w') as f:
            mod_config.write(f)

        # Update .git/config if submodule path in .git/config sections.
        config = configparser.ConfigParser()
        gitconf_path = os.path.join(self.repo_root, ".git", "config")
        config.read(gitconf_path)
        for section in config.sections():
            if section == "submodule \"{}\"".format(self.submodule_remove_path):
                config.remove_section(section)

        with open(gitconf_path, 'w') as f:
            config.write(f)

        message_to_emacs("Remove submodule {}".format(self.submodule_remove_path))

        self.fetch_status_info()
        self.fetch_submodule_info()

    @QtCore.pyqtSlot(str)
    def submodule_update(self, module_path):
        self.submodule_update_path = module_path
        self.send_input_message("Update submodule {} ?".format(module_path), "submodule_update", "yes-or-no")

    def handle_submodule_update(self):
        submodule_path = os.path.join(self.repo_root, self.submodule_update_path)

        message_to_emacs("Update submodule {}...".format(self.submodule_update_path))
        thread = GitPullThread(submodule_path)
        thread.pull_result.connect(self.handle_submodule_update_finish)
        self.thread_reference_list.append(thread)
        thread.start()

    @QtCore.pyqtSlot(str)
    def submodule_move(self, module_path):
        self.submodule_move_path = module_path
        self.send_input_message("Move submodule {} to new path: ".format(module_path), "submodule_move", "directory",
                                os.path.join(self.repo_root, module_path))

    def handle_submodule_move(self, submodule_new_path):
        submodule_old_path = os.path.join(self.repo_root, self.submodule_move_path)
        message_to_emacs("Git change submodule from {} to {}...".format(submodule_old_path, submodule_new_path))
        thread = GitMoveThread(self.repo_root, submodule_old_path, submodule_new_path)
        thread.move_result.connect(self.handle_status_move_report)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def handle_status_move_report(self, message):
        self.fetch_status_info()
        self.fetch_submodule_info()

        message_to_emacs(message)

    @PostGui()
    def handle_submodule_update_finish(self, message):
        self.fetch_status_info()
        self.fetch_submodule_info()
        message_to_emacs(message)

    @QtCore.pyqtSlot(str, str)
    def submodule_rollback(self, module_path, module_head_id):
        self.submodule_rollback_path = module_path
        self.submodule_rollback_head_id = module_head_id
        self.send_input_message("Rollback submodule {} ?".format(module_path), "submodule_rollback", "yes-or-no")

    def handle_submodule_rollback(self):
        submodule_path = os.path.join(self.repo_root, self.submodule_rollback_path)
        submodule_repo = Repository(submodule_path)

        submodule_repo.reset(self.submodule_rollback_head_id, pygit2.GIT_RESET_HARD)

        message_to_emacs("Rollback {} to version {}".format(self.submodule_rollback_path, self.submodule_rollback_head_id))

        self.fetch_status_info()
        self.fetch_submodule_info()

    @QtCore.pyqtSlot()
    def branch_fetch(self):
        remote_branch_names = self.repo.listall_branches(GIT_BRANCH_REMOTE)
        self.send_input_message("Fetch remote branch: ", "branch_fetch", "list", completion_list=remote_branch_names)

    def handle_branch_fetch(self, remote_branch):
        remote_branch = remote_branch.split("/")[-1]

        thread = GitFetchThread(self.repo_root, remote_branch)
        thread.fetch_result.connect(self.handle_branch_fetch_finish)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def handle_branch_fetch_finish(self, branch_name, result):
        if result == "":
            message_to_emacs("Fetch remote branch {} finish.".format(branch_name))
        else:
            message_to_emacs(result)
            self.fetch_branch_info()

    @QtCore.pyqtSlot()
    def branch_fetch_all(self):
        self.send_input_message("Fetch all remote branches?", "branch_fetch_all", "yes-or-no")

    def handle_branch_fetch_all(self):
        thread = GitFetchThread(self.repo_root)
        thread.fetch_result.connect(self.handle_branch_fetch_all_finish)
        self.thread_reference_list.append(thread)
        thread.start()

    @PostGui()
    def handle_branch_fetch_all_finish(self, branch_name, result):
        if result == "":
            message_to_emacs("Fetch all remote branches finish.")
            self.fetch_branch_info()
        else:
            message_to_emacs(result)

    @QtCore.pyqtSlot()
    def branch_create_from_remote(self):
        remote_branch_names = self.repo.listall_branches(GIT_BRANCH_REMOTE)
        self.send_input_message("Create branch from remote branch: ", "branch_create_from_remote", "list", completion_list=remote_branch_names)

    def handle_branch_create_from_remote(self, remote_branch):
        remote_branch = remote_branch.split("/")[-1]

        get_command_result("cd {}; git switch {}".format(self.repo_root, remote_branch))

        message_to_emacs("Create local branch {} finish.".format(remote_branch))
        self.update_git_info()

    @QtCore.pyqtSlot(str)
    def copy_commit_url(self, commit_id):
        remote_default = next(self.repo.config.get_multivar("remote.pushdefault"), "origin")
        origin_url = get_git_https_url(self.repo.remotes[remote_default].url)

        commit_url = "{}/commit/{}".format(origin_url, commit_id)

        eval_in_emacs('kill-new', [commit_url])
        message_to_emacs("Copy {}".format(commit_url))

    @QtCore.pyqtSlot()
    def exit(self):
        for file in self.temp_files:
            if os.path.exists(file):
                os.remove(file)
        self.temp_files = []

        eval_in_emacs('eaf-git-exit', [self.repo_root])

class AddSubmoduleCallback(pygit2.RemoteCallbacks, QtCore.QObject):

    finished = QtCore.pyqtSignal()

    def __init__(self, url):
        super(pygit2.RemoteCallbacks, self).__init__()
        super(QtCore.QObject, self).__init__()
        self.url = url

    def sideband_progress(self, string):
        print("{} {}".format(self.url, string))

class AddSubmoduleThread(QThread):

    finished = QtCore.pyqtSignal(str, str)

    def __init__(self, repo, url, path):
        QThread.__init__(self)

        self.repo = repo
        self.url = url
        self.path = path

    def run(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.callback = AddSubmoduleCallback(self.url)
        self.callback.finished.connect(lambda : self.finished.emit(self.url, self.path))

        try:
            self.repo.submodules.add(self.url, self.path, callbacks=self.callback)
            self.callback.finished.emit()
        except:
            import traceback
            message_to_emacs(traceback.format_exc())

class FetchLogThread(QThread):

    fetch_result = QtCore.pyqtSignal(str, list, str, bool)

    def __init__(self, repo, branch, search_cache=False):
        QThread.__init__(self)

        self.repo = repo
        self.branch = branch
        self.search_cache = search_cache
        self.cache_file_path = ""
        self.append = False

    def run(self):
        git_log = []

        if self.search_cache:
            import tempfile
            self.cache_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
            self.cache_file_path = self.cache_file.name

        start_time = datetime.datetime.now()

        cache_lines = []
        try:
            index = 0

            for commit in self.repo.walk(self.branch.target):
                id = str(commit.id)
                author = bytes_decode(commit.author.raw_name)
                message_list = bytes_decode(commit.raw_message).splitlines()
                message = message_list[0] if len(message_list) > 0 else ""

                git_log.append({
                    "id": id,
                    "index": index,
                    "time": pretty_date(int(commit.commit_time)),
                    "author": author,
                    "message": message,
                    "marked": "",
                    "foregroundColor": "",
                    "backgroundColor": ""
                })

                if self.search_cache:
                    cache_lines.append("{} {} {}\n".format(id, author, message))

                index += 1

                now = datetime.datetime.now()
                if index == 50 or (now - start_time).total_seconds() > 30:
                    start_time = now
                    self.fetch_result.emit(self.branch.shorthand, git_log, self.cache_file_path, self.append)

                    # We need clean git_log after emit fetch_result signal,
                    # make sure segmented sending log for super big project, such as, Emacs.
                    git_log = []
                    self.append = True

        except KeyError:
            import traceback
            traceback.print_exc()

        # NOTE:
        # Uncomment below code to test log search performance.
        # git_log = git_log * 50
        # cache_lines = cache_lines * 50

        if self.search_cache:
            self.cache_file.writelines(cache_lines)

        self.fetch_result.emit(self.branch.shorthand, git_log, self.cache_file_path, self.append)

class GrepLogThread(QThread):

    fetch_result = QtCore.pyqtSignal(str, str, list, str)

    def __init__(self, repo, branch, keyword, search_cache=False):
        QThread.__init__(self)

        self.repo = repo
        self.branch = branch
        self.keyword = keyword
        self.search_cache = search_cache
        self.cache_file_path = ""

    def run(self):
        git_log = []

        if self.search_cache:
            import tempfile
            self.cache_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
            self.cache_file_path = self.cache_file.name

        cache_lines = []
        try:
            index = 0

            for commit in self.repo.walk(self.branch.target):
                if commit.parents:
                    parent = commit.parents[0]
                    diff = self.repo.diff(parent, commit)

                    for patch in diff:
                        if self.keyword in patch.text:
                            id = str(commit.id)
                            author = bytes_decode(commit.author.raw_name)
                            message = bytes_decode(commit.raw_message).splitlines()[0]

                            git_log.append({
                                "id": id,
                                "index": index,
                                "time": pretty_date(int(commit.commit_time)),
                                "author": author,
                                "message": message,
                                "marked": "",
                                "foregroundColor": "",
                                "backgroundColor": ""
                            })

                            if self.search_cache:
                                cache_lines.append("{} {} {}\n".format(id, author, message))

                            index += 1

                            break
        except KeyError:
            import traceback
            traceback.print_exc()

        if self.search_cache:
            self.cache_file.writelines(cache_lines)

        self.fetch_result.emit(self.keyword, self.branch.shorthand, git_log, self.cache_file_path)

class FetchStashThread(QThread):

    fetch_result = QtCore.pyqtSignal(list)

    def __init__(self, repo):
        QThread.__init__(self)

        self.repo = repo

    def run(self):
        git_stash = []

        try:
            index = 0
            for stash in self.repo.listall_stashes():
                git_stash.append({
                    "id": str(stash.commit_id),
                    "index": index,
                    "message": stash.message
                })

                index += 1
        except KeyError:
            import traceback
            traceback.print_exc()

        self.fetch_result.emit(git_stash)

class FetchSubmoduleThread(QThread):

    fetch_result = QtCore.pyqtSignal(list, str)

    def __init__(self, repo, repo_root):
        QThread.__init__(self)

        self.repo = repo
        self.repo_root = repo_root

    def run(self):
        index = 0
        submodule_infos = []
        submodule_names = self.repo.listall_submodules()

        import tempfile
        cache_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
        cache_file_path = cache_file.name

        cache_lines = []

        for submodule_name in submodule_names:
            if hasattr(self.repo, "lookup_submodule"):
                submodule = self.repo.lookup_submodule(submodule_name)
            else:
                submodule = self.repo.submodules.get(submodule_name)
            head_id = submodule.head_id.__str__()

            submodule_path = os.path.join(self.repo_root, submodule_name)
            submodule_last_commit_date = ""
            submodule_last_commit_message = ""

            try:
                submodule_repo = Repository(submodule_path)
                submodule_last_commit = submodule_repo.revparse_single(str(submodule_repo.head.target))
                submodule_last_commit_date = pretty_date(int(submodule_last_commit.commit_time))
                submodule_last_commit_message = bytes_decode(submodule_last_commit.raw_message).splitlines()[0]
            except:
                print("Fetch last commit date failed on submodule {}".format(submodule_path))

            submodule_infos.append({
                "index": index,
                "name": submodule_name,
                "path": submodule_path,
                "head": submodule_last_commit_message,
                "date": submodule_last_commit_date,
                "head_id": head_id,
                "foregroundColor": "",
                "backgroundColor": ""
            })

            cache_lines.append("{} {} {}\n".format(id, submodule_name, head_id))

            index += 1

        cache_file.writelines(cache_lines)
        self.fetch_result.emit(submodule_infos, cache_file_path)

class FetchBranchThread(QThread):

    fetch_result = QtCore.pyqtSignal(list, list)

    def __init__(self, repo):
        QThread.__init__(self)

        self.repo = repo

    def run(self):
        index = 0
        local_branch_infos = []
        local_branch_names = self.repo.listall_branches()

        for branch_name in local_branch_names:
            local_branch_infos.append({
                "index": index,
                "name": branch_name,
                "foregroundColor": "",
                "backgroundColor": "",
                "isCurrentBranch": branch_name == self.repo.head.shorthand
            })

            index += 1

        index = 0

        remote_branch_infos = []
        remote_branch_names = self.repo.listall_branches(GIT_BRANCH_REMOTE)

        for branch_name in remote_branch_names:
            remote_branch_infos.append({
                "index": index,
                "name": branch_name,
                "foregroundColor": "",
                "backgroundColor": ""
            })

            index += 1

        self.fetch_result.emit(local_branch_infos, remote_branch_infos)

class FetchStatusThread(QThread):

    fetch_result = QtCore.pyqtSignal(list, list, list)

    def __init__(self, repo, repo_root, mime_db):
        QThread.__init__(self)

        self.repo = repo
        self.repo_root = repo_root
        self.mime_db = mime_db

    def run(self):
        status = list(filter(lambda info: info[1] != GIT_STATUS_IGNORED, list(self.repo.status().items())))

        (stage_status, unstage_status, untrack_status) = self.parse_status(status)

        self.fetch_result.emit(stage_status, unstage_status, untrack_status)

    def parse_status(self, status):
        stage_status = []
        unstage_status = []
        untrack_status = []

        for info in status:
            if info[1] in GIT_STATUS_DICT:
                self.append_file_to_status_list(info, info[1], stage_status, unstage_status, untrack_status)
            else:
                first_dict = GIT_STATUS_DICT
                second_dict = GIT_STATUS_DICT

                for first_key in first_dict:
                    for second_key in second_dict:
                        if info[1] == first_key | second_key:
                            self.append_file_to_status_list(info, first_key, stage_status, unstage_status, untrack_status)
                            self.append_file_to_status_list(info, second_key, stage_status, unstage_status, untrack_status)

        return (stage_status, unstage_status, untrack_status)

    def append_file_to_status_list(self, info, type_key, stage_status, unstage_status, untrack_status):
        file = info[0]
        file_path = os.path.join(self.repo_root, file)
        mime = self.mime_db.mimeTypeForFile(file_path).name().replace("/", "-")

        (add_count, delete_count) = self.get_line_info(file, type_key, mime)

        status = {
            "file": file,
            "type": GIT_STATUS_DICT[type_key],
            "mime": mime,
            "add_count": add_count,
            "delete_count": delete_count
        }

        if type_key in GIT_STATUS_INDEX_CHANGES:
            if status not in stage_status:
                stage_status.append(status)
        elif type_key in [GIT_STATUS_WT_NEW]:
            if status not in untrack_status:
                untrack_status.append(status)
        else:
            if status not in unstage_status:
                unstage_status.append(status)

    def get_line_info(self, file, type_key, mime):
        # Used to check if there's no commit in current repo.
        head_unborn = False

        if type_key in GIT_STATUS_INDEX_CHANGES:
            try:
                head_tree = self.repo.revparse_single("HEAD^{tree}")
                stage_diff = self.repo.index.diff_to_tree(head_tree)

                patches = [patch for patch in stage_diff if patch.delta.new_file.path == file]
                for patch in patches:
                    (_, add_count, delete_count) = patch.line_stats
                    return (add_count, delete_count)
            except KeyError:
                head_unborn = True

        if type_key in [GIT_STATUS_WT_NEW] or head_unborn:
            if mime.startswith("text-"):
                file_path =os.path.join(self.repo_root, file)
                return (len(open(file_path, "r", encoding="utf-8", errors="ignore").readlines()), 0)
            else:
                return (0, 0)
        else:
            unstage_diff = self.repo.diff(cached=True)
            patches = [patch for patch in unstage_diff if patch.delta.new_file.path == file]
            for patch in patches:
                (_, add_count, delete_count) = patch.line_stats
                return (add_count, delete_count)

class GitPullThread(QThread):

    pull_result = QtCore.pyqtSignal(str)

    def __init__(self, repo_root):
        QThread.__init__(self)

        self.repo_root = repo_root

    def run(self):
        self.pull_result.emit(get_command_result("cd {}; git pull --rebase".format(self.repo_root)).strip())

class GitPushThread(QThread):

    push_result = QtCore.pyqtSignal(str)

    def __init__(self, repo, repo_root, remote):
        QThread.__init__(self)

        self.repo = repo
        self.repo_root = repo_root
        [self.remote, self.remote_branch] = remote.split('/')

    def run(self):
        result = get_command_result("cd {}; git push {} {}".format(self.repo_root, self.remote, self.remote_branch)).strip()
        if result == "":
            result = "Git push {} to {}/{} successfully.".format(self.repo.head.name, self.remote, self.remote_branch)
        self.push_result.emit(result)

class GitMoveThread(QThread):

    move_result = QtCore.pyqtSignal(str)

    def __init__(self, repo_root, submodule_old_path, submodule_new_path):
        QThread.__init__(self)

        self.repo_root = repo_root
        self.submodule_old_path = submodule_old_path
        self.submodule_new_path = submodule_new_path

    def run(self):
        result = get_command_result("cd {}; git mv {} {}".format(self.repo_root, self.submodule_old_path, self.submodule_new_path)).strip()
        if result == "":
            submodule_old_sub_path = self.submodule_old_path.replace(self.repo_root, "")
            submodule_new_sub_path = self.submodule_new_path.replace(self.repo_root, "")
            result = "Git change submodule from {} to {} successfully.".format(submodule_old_sub_path, submodule_new_sub_path)
        self.move_result.emit(result)

class GitFetchThread(QThread):

    fetch_result = QtCore.pyqtSignal(str, str)

    def __init__(self, repo_root, remote_branch=None):
        QThread.__init__(self)

        self.repo_root = repo_root
        self.remote_branch = remote_branch

    def run(self):
        command = "cd {}; git fetch".format(self.repo_root)
        if self.remote_branch is not None:
            command = "cd {}; git fetch origin {}".format(self.repo_root, self.remote_branch)

        self.fetch_result.emit(self.remote_branch, get_command_result(command).strip())

class FetchUnpushThread(QThread):

    fetch_result = QtCore.pyqtSignal(list)

    def __init__(self, repo, repo_root):
        QThread.__init__(self)

        self.repo = repo
        self.repo_root = repo_root

    def run(self):
        if self.repo.head_is_unborn: return  # noqa: E701

        import subprocess
        result = subprocess.run(
            "cd {}; git log origin/{}..HEAD --pretty=format:'%h %s'".format(self.repo_root, self.repo.head.shorthand),
            shell=True, capture_output=True, text=True).stdout

        self.fetch_result.emit(list(filter(lambda x: x.strip() != "", result.split("\n"))))

class HighlightDiffThread(QThread):

    fetch_result = QtCore.pyqtSignal(str, str, float, str, list)

    def __init__(self, target, type, file, tick):
        QThread.__init__(self)

        self.target = target
        self.type = type
        self.file = file
        self.tick = tick

    def parse_diff_and_color(self, patch_set):
        return parse_patch(patch_set, self.target.highlight_diff_strict)

    def run(self):
        diff_string = ""
        patch_set = []

        if self.type == "untrack" or self.target.repo.head_is_unborn:
            if self.file == "":
                show_whole_diff = get_emacs_var("eaf-git-show-whole-untracked-diff")
                if show_whole_diff:
                    for status in self.target.untrack_status:
                        path = os.path.join(self.target.repo_root, status["file"])
                        if os.path.isfile(path):
                            diff_string += "Untrack file: {}\n\n".format(status["file"])
                            diff_string += str(NO_PREVIEW if is_binary(path) else from_path(path).best())
                            diff_string += "\n"
                        else:
                            # submodule directory
                            diff_string += "Untrack: {}\n\n".format(status["file"])
                            diff_string += "\n"

            else:
                path = os.path.join(self.target.repo_root, self.file)
                if os.path.isfile(path):
                    diff_string = str(NO_PREVIEW if is_binary(path) else from_path(path).best())
                else:
                    diff_string = ""

        elif self.type == "stage":
            head_tree = self.target.repo.revparse_single("HEAD^{tree}")
            stage_diff = self.target.repo.index.diff_to_tree(head_tree)
            if self.file == "":
                diff_string = stage_diff.patch
                self.target.raw_patch_set = PatchSet(diff_string)
                patch_set = self.parse_diff_and_color(self.target.raw_patch_set)
            else:
                patches = [patch for patch in stage_diff if patch.delta.new_file.path == self.file]
                diff_string = "\n".join(map(lambda patch : NO_PREVIEW if is_binary(patch.data) else bytes_decode(patch.data), patches))
                self.target.raw_patch_set = PatchSet(diff_string)
                patch_set = self.parse_diff_and_color(self.target.raw_patch_set)

        elif self.type == "unstage":
            unstage_diff = self.target.repo.diff(cached=True)
            if self.file == "":
                diff_string = unstage_diff.patch
                self.target.raw_patch_set = PatchSet(diff_string)
                patch_set = self.parse_diff_and_color(self.target.raw_patch_set)
            else:
                patches = [patch for patch in unstage_diff if patch.delta.new_file.path == self.file]
                diff_string = "\n".join(map(lambda patch : NO_PREVIEW if is_binary(patch.data) else bytes_decode(patch.data), patches))
                self.target.raw_patch_set = PatchSet(diff_string)
                patch_set = self.parse_diff_and_color(self.target.raw_patch_set)

        diff_string = self.target.highlight_diff(diff_string)
        self.fetch_result.emit(self.type, self.file, self.tick, diff_string, patch_set)

class FetchPrListThread(QThread):
    fetch_result = QtCore.pyqtSignal(list)

    def __init__(self, url):
        QThread.__init__(self)

        self.url = url

    def run(self):
        try:
            import requests
            from bs4 import BeautifulSoup

            html = requests.get("{}/pulls".format(self.url)).content.decode("utf-8")
            soup = BeautifulSoup(html, 'html.parser')
            elements = soup.find_all(class_='Link--primary')

            pr_list = list(map(lambda element: [element.get("href").split("/")[-1], element.text], elements))
            self.fetch_result.emit(pr_list)
        except:
            import traceback
            traceback.print_exc()

class ParseGitDiffThread(QThread):
    fetch_result = QtCore.pyqtSignal(str)

    def __init__(self, url):
        QThread.__init__(self)

        self.url = url

    def run(self):
        try:
            diff_string = get_command_result(f"cd {self.url} ; git diff")

            import requests
            import json

            model = "llama3:8b"

            url = 'http://localhost:11434/api/generate'

            data = {
              "model": model,
              "prompt": '''
	      Your task is to help the user write a good commit message.

              Take the whole conversation in consideration and suggest a good commit message.
              Never say anything that is not your proposed commit message, never appologize.

              - Analysis of patch differences in content
              - Use imperative
              - One line only
              - Be clear and concise
              - Follow standard commit message conventions
              - Do not put message in quotes
              - Just return the commit message, without any explaination
              - Only first word of commit message is capitalization, rest words in commit message is lowercase
              - Use spaces to separate words of commit message

              Always provide only the commit message as answer:

              {}
              '''.format(diff_string)
            }

            result = ""
            with requests.post(url, json=data, stream=True) as response:
                for line in response.iter_lines():
                    if line:
                        json_response = json.loads(line)
                        if not json_response["done"]:
                            result += json_response["response"]


            self.fetch_result.emit(result)
        except:
            import traceback
            traceback.print_exc()
