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
        (eaf-git-save-window-configuration)
        (delete-other-windows)
        (eaf-open repo-root "git"))
    (message "%s is not a git repository." default-directory)))

(defcustom eaf-git-keybinding
  '(("<f12>" . "open_devtools")
    ("C-s"   . "search"))
  "The keybinding of EAF git client."
  :type 'cons)

(defcustom eaf-git-js-keybinding
  '(("Global"
     (
      ("T"  ("js_toggle_layout" "Toggle Layout"))
      ("L"  ("py_status_pull" "Pull"))
      ("h" ("js_page_select_prev" "Left page"))
      ("l" ("js_page_select_next" "Right page"))
      ("q" ("py_exit" "Exit"))
      ))
    ("Dashboard"
     (
      ("u"  ("py_status_push" "Push"))
      ("U"  ("py_status_push_branch" "Push branch"))
      ("f"  ("js_status_view_file" "View file"))
      ("s"  ("js_status_stage_file" "Stage file"))
      ("S"  ("js_status_manage_hunk" "Stage/Unstage hunk"))
      ("d"  ("js_status_delete_file" "Delete"))
      ("D"  ("js_status_delete_hunk" "Delete hunk"))
      ("y"  ("py_status_commit_and_push" "Commit and push"))
      ("C"  ("py_status_commit_all" "Commit all"))
      ("c"  ("py_status_commit_stage" "Commit stage"))
      ("x"  ("py_status_stash_push" "Stash push"))
      ("z"  ("py_status_checkout_all" "Revoke changes"))
      ("m"  ("py_status_copy_change_files_to_mirror_repo" "Copy to mirror"))
      ("a"  ("py_status_fetch_pr" "Fetch PR"))
      ("j"  ("js_status_select_next" "Next"))
      ("k"  ("js_status_select_prev" "Prev"))
      ("n"  ("js_hunks_select_next" "Next Hunk"))
      ("p"  ("js_hunks_select_prev" "Prev Hunk"))
      (","  ("js_status_preview_scroll_up_line" "Code up line"))
      ("."  ("js_status_preview_scroll_down_line" "Code down line"))
      ("<"  ("js_status_preview_scroll_up" "Code up"))
      (">"  ("js_status_preview_scroll_down" "Code down"))
      ))
    ("Log"
     (
      ("Enter"  ("js_log_view_diff" "Diff"))
      ("i"      ("py_log_show_compare_branch" "Show compare"))
      ("I"      ("py_log_hide_compare_branch" "Hide compare"))
      ("m"      ("js_log_mark_file" "Mark"))
      ("u"      ("js_log_unmark_file" "Unmark"))
      ("U"      ("js_log_unmark_all" "Unmark all"))
      ("c"      ("js_log_cherry_pick" "Copyto branch"))
      ("x"      ("js_log_copy_commit_url" "Copy commit url"))
      ("X"      ("js_log_copy_commit_id" "Copy commit id"))
      ("b"      ("py_log_rebase_branch" "Rebase and merge from other branch"))
      ("r"      ("js_log_revert_commit" "Revert current"))
      ("R"      ("js_log_revert_to" "Revert all commits above"))
      ("z"      ("js_log_reset_last" "Reset last"))
      ("Z"      ("js_log_reset_to" "Reset all commits above"))
      ("j"      ("js_log_select_next" "Next"))
      ("k"      ("js_log_select_prev" "Prev"))
      ("J"      ("js_log_select_last" "Last"))
      ("K"      ("js_log_select_first" "First"))
      ("p"      ("js_log_select_pg_up" "Previous Page"))
      ("n"      ("js_log_select_pg_dn" "Next Page"))
      ))
    ("Branch"
     (
      ("Enter" ("js_branch_switch" "Switch"))
      ("n"     ("py_branch_new" "New"))
      ("m"     ("js_branch_rename" "Rename"))
      ("d"     ("js_branch_delete" "Delete"))
      ("f"     ("py_branch_fetch" "Fetch"))
      ("F"     ("py_branch_fetch_all" "Fetch all"))
      ("c"     ("py_branch_create_from_remote" "Create from remote"))
      ("x"     ("py_remote_copy_url" "Copy remote url"))
      ("j"     ("js_branch_select_next" "Next"))
      ("k"     ("js_branch_select_prev" "Prev"))
      ("J"     ("js_branch_select_last" "Last"))
      ("K"     ("js_branch_select_first" "First"))
      ))
    ("Stash"
     (
      ("y"      ("js_stash_apply" "Apply"))
      ("p"      ("js_stash_pop" "Pop"))
      ("d"      ("js_stash_drop" "Drop"))
      ("Enter"  ("js_stash_view_diff" "View diff"))
      ("j"      ("js_stash_select_next" "Next"))
      ("k"      ("js_stash_select_prev" "Prev"))
      ("J"      ("js_stash_select_last" "Last"))
      ("K"      ("js_stash_select_first" "First"))
      ))
    ("Submodule"
     (
      ("Enter"  ("js_submodule_view" "View"))
      ("a"      ("py_submodule_add" "Add"))
      ("d"      ("js_submodule_remove" "Remove"))
      ("u"      ("js_submodule_update" "Update"))
      ("r"      ("js_submodule_rollback" "Rollback"))
      ("j"      ("js_submodule_select_next" "Next"))
      ("k"      ("js_submodule_select_prev" "Prev"))
      ("J"      ("js_submodule_select_last" "Last"))
      ("K"      ("js_submodule_select_first" "First"))
      ("p"      ("js_submodule_select_pg_up" "Previous Page"))
      ("n"      ("js_submodule_select_pg_dn" "Next Page"))
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

(defcustom eaf-git-light-highlight-style "stata-light"
  "The default light syntax highlight style."
  :type 'string)

(defcustom eaf-git-dark-highlight-style "monokai"
  "The default dark syntax highlight style."
  :type 'string)

(defcustom eaf-git-layout "H"
  "The default dark syntax highlight style."
  :type '(choice (const :tag "Horizontal" "H")
                 (const :tag "Vertical" "V")))

(add-to-list 'eaf-app-binding-alist '("git" . eaf-git-keybinding))

(setq eaf-git-module-path (concat (file-name-directory load-file-name) "buffer.py"))
(add-to-list 'eaf-app-module-path-alist '("git" . eaf-git-module-path))

(defvar eaf-git-window-configuration nil)

(defun eaf-git-save-window-configuration ()
  (setq eaf-git-window-configuration (current-window-configuration)))

(defun eaf-git-exit (repo-path)
  (kill-buffer)
  (eaf-git-restore-window-configuration)
  (message "Exit git repository %s" repo-path))

(defun eaf-git-restore-window-configuration ()
  (when eaf-git-window-configuration
    (set-window-configuration eaf-git-window-configuration)
    (setq eaf-git-window-configuration nil)))

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

(defun eaf-git-push ()
  (interactive)
  (message "Git push...")
  (save-window-excursion
    (async-shell-command "git push")))

(defun eaf-git-pull ()
  (interactive)
  (message "Git pull...")
  (save-window-excursion
    (async-shell-command "git pull --rebase")))

(defun eaf-git-clone (url)
  (interactive "sGit clone: ")
  (message "Git %s clone..." url)
  (save-window-excursion
    (async-shell-command (format "git clone %s" url))))

(defun eaf-git-show-history ()
  (interactive)
  (let ((point-thing (eaf-git-pointer-thing)))
    (vc-region-history (car point-thing) (cadr point-thing))))

(setq eaf-git-permalink-path (concat (file-name-directory load-file-name) "generate_file_permalink.py"))

(defun eaf-git-get-permalink ()
  (interactive)
  (let ((permalink (shell-command-to-string (format "python %s %s %s" eaf-git-permalink-path (buffer-file-name) (format-mode-line "%l")))))
    (kill-new permalink)
    (message "Copy permalink '%s'" permalink)))

(defun eaf-git-pointer-thing ()
  (cond ((use-region-p)
         (list (region-beginning) (region-end)))
        ((eaf-git-in-string-p)
         (list
          (1+ (car (eaf-git-string-start+end-points)))
          (cdr (eaf-git-string-start+end-points))))
        (t
         (list
          (beginning-of-thing 'symbol)
          (end-of-thing 'symbol)))))

(defun eaf-git-string-start+end-points (&optional state)
  "Return a cons of the points of open and close quotes of the string.
The string is determined from the parse state STATE, or the parse state
  from the beginning of the defun to the point.
This assumes that `eaf-git-in-string-p' has already returned true, i.e.
  that the point is already within a string."
  (save-excursion
    (let ((start (nth 8 (or state (eaf-git-current-parse-state)))))
      (goto-char start)
      (forward-sexp 1)
      (cons start (1- (point))))))

(defun eaf-git-in-string-p (&optional state)
  (or (nth 3 (or state (eaf-git-current-parse-state)))
      (and
       (eq (get-text-property (point) 'face) 'font-lock-string-face)
       (eq (get-text-property (- (point) 1) 'face) 'font-lock-string-face))
      (and
       (eq (get-text-property (point) 'face) 'font-lock-doc-face)
       (eq (get-text-property (- (point) 1) 'face) 'font-lock-doc-face))
      ))

(defun eaf-git-current-parse-state ()
  "Return parse state of point from beginning of defun."
  (let ((point (point)))
    (beginning-of-defun)
    (parse-partial-sexp (point) point)))

(defun eaf-git-checkout-files (checkout-files)
  (save-excursion
    (dolist (filepath checkout-files)
      (let ((buffer (get-file-buffer filepath)))
        (when buffer
          (with-current-buffer buffer
            (revert-buffer :ignore-auto :noconfirm)))))))

(provide 'eaf-git)

;;; eaf-git.el ends here
