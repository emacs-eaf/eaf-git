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
  '(("Global"
     (
      ("h" ("pageSelectPrev" "<-"))
      ("l" ("pageSelectNext" "->"))
      ))
    ("Dashboard"
     (
      ("u"  ("statusPull" "Pull"))
      ("U"  ("statusPush" "Push"))
      ("j"  ("statusSelectNext" "Hide: Next"))
      ("k"  ("statusSelectPrev" "Hide: Prev"))
      ("s"  ("statusStageFile" "Stage"))
      ("d"  ("statusDeleteFile" "Delete"))
      ("y"  ("statusCommitAndPush" "Commit and push"))
      ("C"  ("statusCommitAll" "Commit all"))
      ("c"  ("statusCommitStage" "Commit stage"))
      ("x"  ("statusStashPush" "Stash push"))
      ("z"  ("statusCheckoutAll" "Revoke changes"))
      ("m"  ("statusCopyChangeFilesToMirrorRepo" "Copy to mirror"))
      ))
    ("Log"
     (
      ("j"      ("logSelectNext" "Hide: Next"))
      ("k"      ("logSelectPrev" "Hide: Prev"))
      ("Enter"  ("logViewDiff" "Diff"))
      ("m"      ("logMarkFile" "Mark"))
      ("u"      ("logUnmarkFile" "Unmark"))
      ("U"      ("logUnmarkAll" "Unmark all"))
      ("c"      ("logCherryPick" "Copy to branch"))
      ("i"      ("logShowCompareBranch" "Show compare"))
      ("I"      ("logHideCompareBranch" "Hide compare"))
      ("s"      ("logSearchForward" "Search forward"))
      ("r"      ("logSearchBackward" "Search backward"))
      ("J"      ("logSelectLast" "Hide: Last"))
      ("K"      ("logSelectFirst" "Hide: First"))
      ("R"      ("logRevertCommit" "Revert"))
      ))
    ("Branch"
     (
      ("j"     ("branchSelectNext" "Hide: Next"))
      ("k"     ("branchSelectPrev" "Hide: Prev"))
      ("Enter" ("branchSwitch" "Switch"))
      ("n"     ("branchNew" "New"))
      ("d"     ("branchDelete" "Delete"))
      ("J"     ("branchSelectLast" "Hide: Last"))
      ("K"     ("branchSelectFirst" "Hide: First"))
      ))
    ("Stash"
     (
      ("j"      ("stashSelectNext" "Hide: Next"))
      ("k"      ("stashSelectPrev" "Hide: Prev"))
      ("y"      ("stashApply" "Apply"))
      ("p"      ("stashPop" "Pop"))
      ("d"      ("stashDrop" "Drop"))
      ("Enter"  ("stashViewDiff" "View diff"))
      ("s"      ("stashSearchForward" "Search forward"))
      ("r"      ("stashSearchBackward" "Search backward"))
      ("J"      ("stashSelectLast" "Hide: Last"))
      ("K"      ("stashSelectFirst" "Hide: First"))
      )))
  "The keybinding of EAF git client."
  :type 'cons)

(defcustom eaf-git-delta-executable "delta"
  "The delta executable on your system to be used by eaf-git."
  :type 'string)

(defcustom eaf-git-delta-default-light-theme "GitHub"
  "The default color theme when Emacs has a light background."
  :type 'string)

(defcustom eaf-git-delta-default-dark-theme "Monokai Extended"
  "The default color theme when Emacs has a dark background."
  :type 'string)

(defcustom eaf-git-delta-args
  `("--max-line-distance" "0.6"
    "--true-color"
    "always"
    "--color-only")
  "Delta command line arguments as a list of strings.

If the color theme is not specified using --theme, then it will
be chosen automatically according to whether the current Emacs
frame has a light or dark background. See `eaf-git-delta-default-light-theme' and
`eaf-git-delta-default-dark-theme'.

--color-only is required in order to use delta with magit; it
will be added if not present."
  :type '(repeat string))

(defcustom eaf-git-delta-hide-plus-minus-markers t
  "Whether to hide the +/- markers at the beginning of diff lines."
  :type '(choice (const :tag "Hide" t)
                 (const :tag "Show" nil)))

(add-to-list 'eaf-app-binding-alist '("git" . eaf-git-keybinding))

(setq eaf-git-module-path (concat (file-name-directory load-file-name) "buffer.py"))
(add-to-list 'eaf-app-module-path-alist '("git" . eaf-git-module-path))

(defun eaf-git-list-intersect-p (list1 list2)
  "Return non-nil if any elements of LIST1 appear in LIST2.
Comparison is done with `equal'."
  (while (and list1 (not (member (car list1) list2)))
    (pop list1))
  list1)

(defun eaf-git-delta--make-delta-args ()
  "Make final list of delta command-line arguments."
  (let ((args eaf-git-delta-args))
    (unless (eaf-git-list-intersect-p '("--syntax-theme" "--light" "--dark") args)
      (setq args (nconc
                  (list "--syntax-theme"
                        (if (eq (frame-parameter nil 'background-mode) 'dark)
                            eaf-git-delta-default-dark-theme
                          eaf-git-delta-default-light-theme))
                  args)))
    (unless (member "--color-only" args)
      (setq args (cons "--color-only" args)))
    args))

(defun eaf-git-delta-hide-plus-minus-markers ()
  "Apply text properties to hide the +/- markers at the beginning of lines."
  (save-excursion

    (goto-char (point-min))
    ;; Within hunks, hide - or + at the start of a line.
    (let ((in-hunk nil))
      (while (re-search-forward "^\\(diff\\|@@\\|+\\|-\\)" nil t)
        (cond
         ((string-equal (match-string 0) "diff")
          (setq in-hunk nil))
         ((string-equal (match-string 0) "@@")
          (setq in-hunk t))
         (in-hunk
          (add-text-properties (match-beginning 0) (match-end 0)
                               '(invisible t))))))))
(defun eaf-git-call-delta-and-convert-ansi-escape-sequences ()
  "Call delta on buffer contents and convert ANSI escape sequences to overlays.

The input buffer contents are expected to be raw git output."
  (apply #'call-process-region
         (point-min) (point-max)
         eaf-git-delta-executable t t nil (eaf-git-delta--make-delta-args))
  (let ((buffer-read-only nil))
    (xterm-color-colorize-buffer 'use-overlays)
    (if eaf-git-delta-hide-plus-minus-markers
        (eaf-git-delta-hide-plus-minus-markers))))

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

    (if (and
         (ignore-errors (require 'xterm-color))
         (executable-find eaf-git-delta-executable))
        (eaf-git-call-delta-and-convert-ansi-escape-sequences))

    (read-only-mode 1)

    ;; Select EAF log window.
    (select-window (get-buffer-window log-buffer))
    ))

(provide 'eaf-git)

;;; eaf-git.el ends here
