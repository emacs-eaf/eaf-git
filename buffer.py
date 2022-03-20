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

from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QThread
from core.webengine import BrowserBuffer
from core.utils import get_emacs_func_result, get_emacs_var, PostGui
from pygit2 import (Repository, GIT_SORT_TOPOLOGICAL,
                    GIT_STATUS_CURRENT,
                    GIT_STATUS_INDEX_NEW,
                    GIT_STATUS_INDEX_MODIFIED,
                    GIT_STATUS_INDEX_DELETED,
                    GIT_STATUS_INDEX_RENAMED,
                    GIT_STATUS_INDEX_TYPECHANGE,
                    GIT_STATUS_WT_NEW,
                    GIT_STATUS_WT_MODIFIED,
                    GIT_STATUS_WT_DELETED,
                    GIT_STATUS_WT_TYPECHANGE,
                    GIT_STATUS_WT_RENAMED,
                    GIT_STATUS_WT_UNREADABLE,
                    GIT_STATUS_IGNORED,
                    GIT_STATUS_CONFLICTED,
                    discover_repository)
from datetime import datetime
from pathlib import Path
import os
import json

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

class AppBuffer(BrowserBuffer):
    def __init__(self, buffer_id, url, arguments):
        BrowserBuffer.__init__(self, buffer_id, url, arguments, False)

        self.fetch_status_threads = []
        self.fetch_log_threads = []
        self.fetch_submodule_threads = []
        self.fetch_branch_threads = []

        self.repo = Repository(self.url)
        self.repo_root = discover_repository(self.url)
        if os.path.basename(os.path.normpath(self.repo_root)) == ".git":
            self.repo_root = str(Path(self.repo_root).parent.absolute())
        self.repo_path = os.path.sep.join(list(filter(lambda x: x != '', self.repo_root.split(os.path.sep)))[-2:])

        self.head_name = self.repo.head.name.split("/")[-1]
        self.last_commit_id = str(self.repo.head.target)[:7]
        self.last_commit = self.repo.revparse_single(str(self.repo.head.target))
        self.last_commit_message = self.last_commit.message.rstrip()

        self.load_index_html(__file__)

    def init_app(self):
        self.init_vars()

        self.fetch_status_info()
        self.fetch_log_info()
        self.fetch_submodule_info()
        self.fetch_branch_info()

    def init_vars(self):
        (text_color, nav_item_color, info_color, date_color, id_color, author_color) = get_emacs_func_result(
            "get-emacs-face-foregrounds",
            ["default",
             "font-lock-function-name-face",
             "font-lock-keyword-face",
             "font-lock-builtin-face",
             "font-lock-comment-face",
             "font-lock-string-face"])

        self.buffer_widget.eval_js('''init(\"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\")'''.format(
            self.theme_background_color, QColor(self.theme_background_color).darker(110).name(),
            text_color, nav_item_color, info_color,
            date_color, id_color, author_color,
            self.repo_path, self.head_name, self.last_commit_id, self.last_commit_message))

    def fetch_status_info(self):
        thread = FetchStatusThread(self.repo)
        thread.fetch_result.connect(self.update_status_info)
        self.fetch_status_threads.append(thread)
        thread.start()

    @PostGui()
    def update_status_info(self, stage_status, unstage_status):
        self.buffer_widget.eval_js('''updateStatusInfo({}, {})'''.format(json.dumps(stage_status), json.dumps(unstage_status)))

    def fetch_log_info(self):
        thread = FetchLogThread(self.repo)
        thread.fetch_result.connect(self.update_log_info)
        self.fetch_log_threads.append(thread)
        thread.start()

    @PostGui()
    def update_log_info(self, log):
        self.buffer_widget.eval_js('''updateLogInfo({})'''.format(json.dumps(log)))

    def fetch_submodule_info(self):
        thread = FetchSubmoduleThread(self.repo)
        thread.fetch_result.connect(self.update_submodule_info)
        self.fetch_submodule_threads.append(thread)
        thread.start()

    @PostGui()
    def update_submodule_info(self, submodule):
        self.buffer_widget.eval_js('''updateSubmoduleInfo({})'''.format(json.dumps(submodule)))

    def fetch_branch_info(self):
        thread = FetchBranchThread(self.repo)
        thread.fetch_result.connect(self.update_branch_info)
        self.fetch_branch_threads.append(thread)
        thread.start()

    @PostGui()
    def update_branch_info(self, branch):
        self.buffer_widget.eval_js('''updateBranchInfo({})'''.format(json.dumps(branch)))

    def switch_to_dashboard(self):
        self.buffer_widget.eval_js('''changePage(\"Dashboard\");''')

    def switch_to_log(self):
        self.buffer_widget.eval_js('''changePage(\"Log\");''')

    def switch_to_submodule(self):
        self.buffer_widget.eval_js('''changePage(\"Submodule\");''')

    def switch_to_branch(self):
        self.buffer_widget.eval_js('''changePage(\"Branch\");''')

    def switch_to_patch(self):
        self.buffer_widget.eval_js('''changePage(\"Patch\");''')

class FetchLogThread(QThread):

    fetch_result = QtCore.pyqtSignal(list)

    def __init__(self, repo):
        QThread.__init__(self)

        self.repo = repo

    def run(self):
        git_log = []

        for commit in self.repo.walk(self.repo.head.target, GIT_SORT_TOPOLOGICAL):
            git_log.append({
                "id": str(commit.id),
                "time": datetime.utcfromtimestamp(int(commit.commit_time)).strftime('%Y-%m-%d %H:%M:%S'),
                "author": commit.author.name,
                "message": commit.message.rstrip()
            })

        self.fetch_result.emit(git_log)

class FetchSubmoduleThread(QThread):

    fetch_result = QtCore.pyqtSignal(list)

    def __init__(self, repo):
        QThread.__init__(self)

        self.repo = repo

    def run(self):
        self.fetch_result.emit(self.repo.listall_submodules())

class FetchBranchThread(QThread):

    fetch_result = QtCore.pyqtSignal(list)

    def __init__(self, repo):
        QThread.__init__(self)

        self.repo = repo

    def run(self):
        self.fetch_result.emit(self.repo.listall_branches())

class FetchStatusThread(QThread):

    fetch_result = QtCore.pyqtSignal(list, list)

    def __init__(self, repo):
        QThread.__init__(self)

        self.repo = repo

    def run(self):
        status = list(filter(lambda info: info[1] != GIT_STATUS_IGNORED, list(self.repo.status().items())))
        
        (stage_status, unstage_status) = self.parse_status(status)
        
        self.fetch_result.emit(stage_status, unstage_status)
        
    def parse_status(self, status):
        stage_status = []
        unstage_status = []
        
        for info in status:
            if info[1] in GIT_STATUS_DICT:
                self.append_file_to_status_list(info, info[1], stage_status, unstage_status)
            else:
                first_dict = GIT_STATUS_DICT
                second_dict = GIT_STATUS_DICT
                
                for first_key in first_dict:
                    for second_key in second_dict:
                        if info[1] == first_key | second_key:
                            self.append_file_to_status_list(info, first_key, stage_status, unstage_status)
                            self.append_file_to_status_list(info, second_key, stage_status, unstage_status)
                            
        return (stage_status, unstage_status)                    
                            
    def append_file_to_status_list(self, info, type_key, stage_status, unstage_status):
        status = {
            "file": info[0],
            "type": GIT_STATUS_DICT[type_key]
        }
        
        if type_key in [GIT_STATUS_INDEX_MODIFIED, GIT_STATUS_INDEX_DELETED, GIT_STATUS_INDEX_RENAMED, GIT_STATUS_INDEX_TYPECHANGE]:
            if status not in stage_status:
                stage_status.append(status)
        else:
            if status not in unstage_status:
                unstage_status.append(status)
        
