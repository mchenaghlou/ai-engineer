# Git Cheatsheet (Practical Engineering Reference)

This document focuses on operational Git: moving between states, recovering history, and managing branches. It avoids theory unless needed to explain behavior.

---

# 1. Mental Model (Core Git Object Graph)

Git is a directed acyclic graph (DAG) of commits.

Each commit:
- Points to a parent commit (or multiple parents in merges)
- Contains a snapshot of the repository state

Basic structure:

```
A --- B --- C (main)
        \
         D --- E (feature)
```

Branches are just pointers:

```
main:    C
feature: E
```

HEAD = "where you currently are"

```
HEAD -> main -> C
```

---

# 2. Status Flow (Working Directory → Staging → Commit)

```
Working Directory  -->  Staging Area  -->  Repository
       (edit)              (add)            (commit)
```

Commands:

```bash
git status
git add <file>
git add .
git commit -m "message"
```

---

# 3. Branching

## Create / Switch branches

```bash
git branch feature-x
git switch feature-x
```

or combined:

```bash
git switch -c feature-x
```

Legacy:

```bash
git checkout -b feature-x
```

## List branches

```bash
git branch
git branch -a
```

## Delete branch

```bash
git branch -d feature-x     # safe delete
git branch -D feature-x     # force delete
```

---

# 4. Commit History Navigation

## View history

```bash
git log
git log --oneline --graph --all
```

Visual:

```
* E (HEAD -> feature)
* D
* C (main)
* B
* A
```

---

## Move HEAD (detached state)

```bash
git checkout <commit_hash>
```

Detached HEAD means:

- You are not on a branch
- Commits are "floating" unless saved

---

# 5. Reset vs Revert (Critical)

## git reset (rewrites history)

### Soft reset (keep changes staged)
```bash
git reset --soft HEAD~1
```

### Mixed reset (default)
```bash
git reset HEAD~1
```

### Hard reset (discard everything)
```bash
git reset --hard HEAD~1
```

Diagram:

```
Before:
A --- B --- C (HEAD)

git reset B

After:
A --- B (HEAD)
      C (lost unless reflog)
```

---

## git revert (safe history undo)

Creates a new commit that reverses changes.

```bash
git revert <commit>
```

```
A --- B --- C --- D (revert C)
```

Use in shared branches.

---

# 6. Stash (Temporary State Saving)

```bash
git stash
git stash list
git stash pop
git stash apply
```

Use case:
- switching branch with uncommitted work

---

# 7. Merge

## Fast-forward merge

```
main: A --- B
feature:      C --- D

merge ->

main: A --- B --- C --- D
```

Command:

```bash
git merge feature
```

---

## 3-way merge

```
      C --- D (feature)
     /
A --- B --- E (main)
```

Merge creates commit E with two parents.

---

# 8. Rebase (Linear history)

Rebase rewrites commits onto new base.

```
Before:
A --- B --- C (main)
      \
       D --- E (feature)

git rebase main

After:
A --- B --- C --- D' --- E'
```

Command:

```bash
git rebase main
```

---

# 9. Remote Operations (Push / Pull / Fetch)

## Fetch (download only)

```bash
git fetch
```

- Updates remote tracking branches
- Does NOT modify working branch

---

## Pull (fetch + merge)

```bash
git pull
```

Equivalent:

```bash
git fetch
git merge origin/main
```

---

## Push

```bash
git push origin main
git push origin feature-x
```

First push:

```bash
git push -u origin feature-x
```

---

# 10. Remote Branch Model

```
Local:        main
Remote:       origin/main
Tracking:     main -> origin/main
```

Update flow:

```
git fetch  -> updates origin/main
git pull   -> merges into main
git push   -> updates remote
```

---

# 11. Restoring Files

## Restore file to last commit

```bash
git restore <file>
```

## Restore from staging

```bash
git restore --staged <file>
```

## Old equivalent:

```bash
git checkout -- <file>
```

---

# 12. Moving Commits (Cherry-pick)

Apply a specific commit:

```bash
git cherry-pick <commit>
```

```
A --- B --- C (main)
       \
        D (feature)

cherry-pick D -> main gets D
```

---

# 13. Reflog (Safety Net)

Git keeps hidden history of HEAD movements.

```bash
git reflog
```

Recover lost commits:

```bash
git reset --hard <reflog_hash>
```

---

# 14. Conflict Resolution

When merge fails:

```
<<<<<< HEAD
current branch
======
incoming branch
>>>>>> feature
```

Fix manually:

```bash
git add .
git commit
```

---

# 15. Common Workflows

## Feature branch workflow

```bash
git switch main
git pull
git switch -c feature-x

# work
git add .
git commit

git push -u origin feature-x
```

Merge back:

```bash
git switch main
git merge feature-x
git push
```

---

## Update feature branch

```bash
git fetch
git rebase origin/main
```

---

# 16. Quick Command Map

```
STATE INSPECTION
git status
git log --graph --oneline

BRANCHING
git switch -c
git branch -d

HISTORY
git log
git reflog

UNDO
git reset
git revert
git restore

SYNC
git fetch
git pull
git push

TEMP
git stash

INTEGRATION
git merge
git rebase
git cherry-pick
```

---

# 17. Key Mental Rules

1. Commit = immutable snapshot
2. Branch = pointer
3. HEAD = current pointer
4. Reset rewrites history (dangerous on shared branches)
5. Revert is safe undo (always shared-safe)
6. Rebase rewrites history (clean but risky if misused)
