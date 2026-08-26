# Git for you (minimum hassle)

**Your rule:** You work on **main** only. Agents handle git. You almost never type git.

## Why it felt awful

Grok sometimes uses a **second folder** (worktree) so it does not wreck your main project. That created extra branches and “not on any branch” messages. That is tooling friction — not something you failed at.

## Your monorepo (the only place that matters)

```
D:\Users\uzeda\Mt. Sinai LLC\monorepo
```

- Branch: **main** only  
- Phase 4–5 local work, Psalm titles, and static Word study are **already on main** (published 2026-08-26).  
- Public 365DBR stays **static files on GoDaddy** (no live database). See `docs/365DBR/Hosting-and-Runtime.md`.

## What you do (optional)

| When | What you say to the agent |
|------|---------------------------|
| End of a good session | “Save my work” / “check it in” |
| Want backup on GitHub | “Push to GitHub” |
| Something looks wrong | “Is main safe?” |

That is the whole workflow. No branch names. No merge tutorials.

## What the agent must do for you

1. Stay on **main** (or put finished work on main before ending).  
2. Commit when you ask (or when work is clearly done and you want safety).  
3. **Never** ask you to learn rebase, cherry-pick, or worktrees.  
4. **Never** force-push or rewrite published history without an explicit “yes”.  
5. Prefer one sentence status: “Saved on main” or “Saved on main and pushed to GitHub.”

## What git is actually buying you (without the ritual)

- Undo a bad day without guessing which files to restore  
- Backup if a drive dies (after push)  
- Monorepo: one place for 365DBR + other apps  

If it costs more than that, the process is wrong — fix the process, not you.

## Emergency (only if agent is gone)

From your monorepo folder, in PowerShell:

```powershell
# See if anything is unsaved
git status

# Save everything on main (only if you know you want that)
git add -A
git commit -m "Save work"

# Backup to GitHub (only when you want remote safety)
git push
```

If those fail, stop and ask an agent — do not dig deeper.

---

**Bottom line:** You own the Bible work and product decisions. Agents own git plumbing.
