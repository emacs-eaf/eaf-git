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
from pygit2 import Repository, GIT_SORT_TIME, GIT_SORT_TOPOLOGICAL
from datetime import datetime
import os
import json

class AppBuffer(BrowserBuffer):
    def __init__(self, buffer_id, url, arguments):
        BrowserBuffer.__init__(self, buffer_id, url, arguments, False)
        
        self.fetch_log_threads = []
        self.fetch_submodule_threads = []
        
        self.current_dir = get_emacs_var("default-directory")
        self.repo_path = os.path.sep.join(list(filter(lambda x: x != '', self.current_dir.split(os.path.sep)))[-2:])
        self.repo = Repository(self.current_dir)
        self.head_name = self.repo.head.name.split("/")[-1]
        self.last_commit_id = str(self.repo.head.target)[:7]
        self.last_commit = self.repo.revparse_single(str(self.repo.head.target))
        self.last_commit_message = self.last_commit.message.rstrip()

        self.load_index_html(__file__)
        
    def init_app(self):
        self.init_vars()
        
        self.fetch_log_info()
        self.fetch_submodule_info()
        
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

