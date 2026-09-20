# Screenshot checklist - Git & GitHub assignment

Save each image in this folder with the filename shown.
Capture with **Win + PrtScn** (auto-saves to Pictures\Screenshots), then
move and rename it here. Win+Shift+S only copies to the clipboard - if you
use it, paste into Paint and save, or the file is never created.

Run all terminal commands from:
    cd C:\Users\yagna\Devops_Assignments

---

## Task 1 - Repository setup & first branch  (4 shots)

- [ ] **01-ssh-keygen-or-key.png**
      GitHub -> Settings -> SSH and GPG keys, showing "Yagna Laptop".

- [ ] **02-ssh-auth.png**
      ssh -T git@github.com
      -> "Hi YagnaRaval28! You've successfully authenticated"

- [ ] **03-branch-created.png**
      git branch -a

- [ ] **04-task1-merge.png**
      git log --oneline --graph -8

## Task 2 - Update JSON & resolve conflicts  (3 shots)

- [ ] **05-conflict.png**
      git log --oneline --all | Select-String "Tutedude_new"
      Shows the conflict was created and resolved. The original CONFLICT
      message has scrolled past; the commit history is the evidence.

- [ ] **06-resolved-json.png**
      Browser: http://127.0.0.1:5000/api
      Shows 5 courses with "(Updated)" titles - the _new branch version
      that was accepted during conflict resolution.

- [ ] **07-push.png**
      git log --oneline -3
      git status

## Task 3 - Parallel feature development  (5 shots)

- [ ] **08-two-branches.png**
      git branch -v

- [ ] **09-todo-page.png**
      Browser: http://127.0.0.1:5000/todo
      The To-Do form (master_1 work).

- [ ] **10-docker-mongo.png**
      docker ps

- [ ] **11-submit-result.png**
      Fill the /todo form, submit it. You get a JSON response with
      "To-Do item stored successfully" and an id.

- [ ] **12-todoitems.png**
      Browser: http://127.0.0.1:5000/todoitems
      The stored items read back from MongoDB.

- [ ] **13-merge-graph.png**
      git log --oneline --graph -12
      Shows master_1 and master_2 merging into main.

## Task 4 - Sequential commits, reset & rebase  (4 shots)

- [ ] **14-three-commits.png**
      git reflog master_1 | Select-Object -First 5
      The three separate commits: Item ID, Item UUID, Item Hash.
      Use the reflog, not git log: the later rebase dropped those commits
      as already-upstream, so git log no longer lists them. The reflog is
      the record that each field was committed separately.

- [ ] **15-reset-soft.png**
      git reflog main | Select-Object -First 6
      Shows the reset --soft entry in the history.

- [ ] **16-rebase.png**
      git reflog master_1 | Select-Object -First 6
      Shows "rebase (finish)" and the three commits replayed
      individually - proof they were not squashed.

- [ ] **17-form-all-fields.png**
      Browser: http://127.0.0.1:5000/todo
      The form now showing all five fields: Item Name, Item Description,
      Item ID, Item UUID, Item Hash.

## Final  (1 shot)

- [ ] **18-github-branches.png**
      https://github.com/YagnaRaval28/devops_tutedude/branches
      All five branches: main, Tutedude, Tutedude_new, master_1, master_2.

---

Total: 18 screenshots.
