;;; eaf-git.el --- Git client

;; Filename: eaf-git.el
;; Description: Git client
;; Author: Andy Stewart <lazycat.manatee@gmail.com>
;; Maintainer: Andy Stewart <lazycat.manatee@gmail.com>
;; Copyright (C) 2021, Andy Stewart, all rights reserved.
;; Created: 2021-08-01 10:30:42
;; Version: 0.1
;; Last-Updated: 2021-08-01 10:30:42
;;           By: Andy Stewart
;; URL: http://www.emacswiki.org/emacs/download/eaf-git.el
;; Keywords:
;; Compatibility: GNU Emacs 28.0.50
;;
;; Features that might be required by this library:
;;
;;
;;

;;; This file is NOT part of GNU Emacs

;;; License
;;
;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation; either version 3, or (at your option)
;; any later version.

;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with this program; see the file COPYING.  If not, write to
;; the Free Software Foundation, Inc., 51 Franklin Street, Fifth
;; Floor, Boston, MA 02110-1301, USA.

;;; Commentary:
;;
;; Git client
;;

;;; Installation:
;;
;; Put eaf-git.el to your load-path.
;; The load-path is usually ~/elisp/.
;; It's set in your ~/.emacs like this:
;; (add-to-list 'load-path (expand-file-name "~/elisp"))
;;
;; And the following to your ~/.emacs startup file.
;;
;; (require 'eaf-git)
;;
;; No need more.

;;; Customize:
;;
;;
;;
;; All of the above can customize by:
;;      M-x customize-group RET eaf-git RET
;;

;;; Change log:
;;
;; 2021/08/01
;;      * First released.
;;

;;; Acknowledgements:
;;
;;
;;

;;; TODO
;;
;;
;;

;;; Require


;;; Code:

;;;###autoload
(defun eaf-open-git ()
  "Open EAF Git client."
  (interactive)
  (if (and (executable-find "git")
           (string-equal (car (split-string (shell-command-to-string "git rev-parse --is-inside-work-tree"))) "true"))
      (let ((repo-root (car (split-string (shell-command-to-string "git rev-parse --show-toplevel")))))
        (eaf-open repo-root "git"))
    (message "%s is not a git repository." default-directory)))

(defcustom eaf-git-keybinding
  '(("<f12>" . "open_devtools"))
  "The keybinding of EAF git client."
  :type 'cons)

(defcustom eaf-git-js-keybinding
  '(("Dashboard" (
                  ("u"  ("statusPull" "Pull"))
                  ("U"  ("statusPush" "Push"))
                  ("j"  ("statusSelectNext" "Next"))
                  ("k"  ("statusSelectPrev" "Prev"))
                  ("s"  ("statusStageFile" "Stage"))
                  ("d"  ("statusDeleteFile" "Delete"))
                  ("y"  ("statusCommitAndPush" "Commit and push"))
                  ("C"  ("statusCommitAll" "Commit all"))
                  ("c"  ("statusCommitStage" "Commit stage"))
                  ("z"  ("statusCheckoutAll" "Revoke changes"))
                  ("m"  ("statusCopyChangeFilesToMirrorRepo" "Copy to mirror repo"))
                  ))
    ("Log" (
            ("j"      ("logSelectNext" "Next"))
            ("k"      ("logSelectPrev" "Prev"))
            ("Enter"  ("logViewDiff" "View diff"))
            ("s"      ("logSearchForward" "Search forward"))
            ("r"      ("logSearchBackward" "Search backward"))
            ("J"      ("logSelectLast" "Last"))
            ("K"      ("logSelectFirst" "First"))
            ))
    ("Branch" (
               ("j"     ("branchSelectNext" "Next"))
               ("k"     ("branchSelectPrev" "Prev"))
               ("Enter" ("branchSwitch" "Switch"))
               ("J"     ("branchSelectLast" "Last"))
               ("K"     ("branchSelectFirst" "First"))
               )))
  "The keybinding of EAF git client."
  :type 'cons)

(add-to-list 'eaf-app-binding-alist '("git" . eaf-git-keybinding))

(setq eaf-git-module-path (concat (file-name-directory load-file-name) "buffer.py"))
(add-to-list 'eaf-app-module-path-alist '("git" . eaf-git-module-path))

(defun eaf-git-show-commit-diff (diff-string)
  (let ((log-buffer (current-buffer))
        (diff-buffer (make-temp-file "eaf-git-commit-diff")))
    ;; Split window.
    (when (< (length (cl-remove-if #'window-dedicated-p (window-list))) 2) ;we need remove dedicated window, such as sort-tab window
      (split-window-below))

    ;; Select top window.
    (ignore-errors
      (dotimes (i 50)
        (windmove-up)))

    ;; Insert diff content.
    (find-file diff-buffer)
    (erase-buffer)
    (insert diff-string)
    (diff-mode)
    (goto-char (point-min))
    (read-only-mode 1)

    ;; Select EAF log window.
    (select-window (get-buffer-window log-buffer))
    ))

(provide 'eaf-git)

;;; eaf-git.el ends here
