# Moving to a fresh, single-contributor GitHub repo

Goal: disconnect this local project from its current GitHub repo and history,
and push the current code as a brand-new repo with you as the only
contributor.

**I have not run any of these steps.** Deleting local git history and pushing
to a new remote are hard to reverse, so this is written for you to run
yourself (or ask me to run specific steps once you've reviewed them).

## What's true about your setup right now (checked 2026-07-12)

- Current remote: `origin -> https://github.com/HarshiniUF/DSSAT-Chatbot.git`
- Current branch: `main`, 2 commits, single author already (`HarshiniUF`) --
  so the *history* isn't the problem, but you still want a clean break/new repo.
- Local git identity is already set correctly: `user.name=HarshiniUF`,
  `user.email=harshini.sangem@ufl.edu`. New commits will be attributed to you.
- `.gitignore` already excludes the things that must never be pushed:
  `.env` (your API keys), `venv/`/`.venv/` (both venvs), `__pycache__/`,
  and `INTEGRATION/` (which contains very large soil data files, some
  100-370MB -- GitHub hard-blocks files over 100MB, so this exclusion matters).
- The project (excluding venvs) is ~2.2GB. Most of that is soil/weather data
  already gitignored; the actual code is much smaller.
- `gh` (GitHub CLI) is **not installed** on this machine, so the "create a new
  repo" step below uses the GitHub website. If you install `gh` and run
  `gh auth login` first, there's a one-command alternative noted at that step.

## Step 1 -- Back up first (recommended, cheap insurance)

Deleting `.git` is permanent for this working copy. Before doing that, make a
throwaway copy of the whole project folder, or at minimum copy just the
`.git` directory somewhere safe, in case you ever want the old history back:

```bash
cp -r /home/harshini/Downloads/dssat_project/dssat_project /home/harshini/Downloads/dssat_project_backup_$(date +%Y%m%d)
```

## Step 2 -- Double-check nothing sensitive would get committed

```bash
cd /home/harshini/Downloads/dssat_project/dssat_project
git status --short | grep -i "\.env$"      # should print nothing
git check-ignore -v .env                    # should confirm it's ignored
du -sh --exclude=venv --exclude=.venv .     # sanity-check total size
```

If `.env` ever shows up as trackable, stop and fix `.gitignore` before
continuing -- that file has your real API keys in it.

## Step 3 -- Remove the old GitHub connection locally

This deletes all local git history and the link to the old remote. Your
actual project files on disk are untouched -- only the `.git` folder goes.

```bash
cd /home/harshini/Downloads/dssat_project/dssat_project
rm -rf .git
```

## Step 4 -- Start a fresh local repo

```bash
git init
git branch -m main
```

## Step 5 -- Stage and make one clean initial commit

```bash
git add .
git status   # review what's about to be committed -- confirm no .env, no venv/, nothing unexpected
git commit -m "Initial commit"
```

If `git status` shows anything you don't want committed, `git rm --cached
<file>` it and add it to `.gitignore` before committing.

## Step 6 -- Create a brand-new empty repo on GitHub

**Via the website:**
1. Go to https://github.com/new
2. Pick a name (can reuse `DSSAT-Chatbot` or pick a new one -- it's a
   different repo either way since there's no shared history)
3. Choose Public or Private
4. **Do not** check "Add a README", "Add .gitignore", or "Add a license" --
   leave it completely empty so it has no commits of its own to conflict with
   yours
5. Click "Create repository" and copy the repo URL it shows you
   (`https://github.com/HarshiniUF/<new-repo-name>.git`)

**Via GitHub CLI instead** (only if you install `gh` and run `gh auth login`
first):
```bash
gh repo create <new-repo-name> --private --source=. --remote=origin
```
(This one command replaces steps 6 and 7 below if you use it.)

## Step 7 -- Point this local repo at the new remote and push

```bash
git remote add origin https://github.com/HarshiniUF/<new-repo-name>.git
git push -u origin main
```

## Step 8 -- Verify

- Open the new repo on GitHub and confirm the files are all there.
- Check the repo's "Contributors"/commit history (Insights tab, or just
  `git log` locally) -- it should show only you, with a single "Initial
  commit".

## Step 9 -- Decide what happens to the old repo (separate decision)

This repo bridge doesn't touch `HarshiniUF/DSSAT-Chatbot` (the old one) at
all -- disconnecting locally doesn't delete or change it on GitHub. If you
want it gone too, that's a distinct, irreversible action you'd take
separately on GitHub itself (repo Settings -> Danger Zone -> Delete this
repository), not something to bundle into this process. Decide that on its
own once the new repo is confirmed working.
