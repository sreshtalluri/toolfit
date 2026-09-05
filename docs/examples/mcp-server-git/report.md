## Confusion Matrix

| Intended \ Called | git_add | git_branch | git_checkout | git_commit | git_create_branch | git_diff | git_diff_staged | git_diff_unstaged | git_log | git_reset | git_show | git_status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| git_add | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| git_branch | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| git_checkout | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| git_commit | 5 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| git_create_branch | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| git_diff | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| git_diff_staged | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 |
| git_diff_unstaged | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 |
| git_log | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| git_reset | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 |
| git_show | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| git_status | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 9 |

## Trial Diversity
- git_add: 10/10 distinct
- git_branch: 10/10 distinct
- git_checkout: 10/10 distinct
- git_commit: 10/10 distinct
- git_create_branch: 10/10 distinct
- git_diff: 10/10 distinct
- git_diff_staged: 10/10 distinct
- git_diff_unstaged: 10/10 distinct
- git_log: 10/10 distinct
- git_reset: 10/10 distinct
- git_show: 10/10 distinct
- git_status: 10/10 distinct

## Pass Rates
- git_add: 10/10 (100%), 95% CI [72%, 100%]
- git_branch: 10/10 (100%), 95% CI [72%, 100%]
- git_checkout: 10/10 (100%), 95% CI [72%, 100%]
- git_commit: 4/10 (40%), 95% CI [17%, 69%]
- git_create_branch: 10/10 (100%), 95% CI [72%, 100%]
- git_diff: 10/10 (100%), 95% CI [72%, 100%]
- git_diff_staged: 10/10 (100%), 95% CI [72%, 100%]
- git_diff_unstaged: 10/10 (100%), 95% CI [72%, 100%]
- git_log: 9/10 (90%), 95% CI [60%, 98%]
- git_reset: 10/10 (100%), 95% CI [72%, 100%]
- git_show: 10/10 (100%), 95% CI [72%, 100%]
- git_status: 9/10 (90%), 95% CI [60%, 98%]

## Solvability Warnings
- git_commit (seed 1): Committing requires staging changes first (git_add) before git_commit can be used, so a single tool isn't clearly sufficient.
- git_commit (seed 7): Committing requires files to be staged first (via git_add), and since git_status/git_diff_unstaged aren't guaranteed to show unstaged changes are already staged, it's unclear whether git_commit alone will succeed without first calling git_add.
- git_commit (seed 8): Committing typically requires staging changes first (git_add) before git_commit, so it's unclear whether the assistant should call git_add or git_commit as the single next tool.
- git_commit (seed 10): Committing typically requires staging changes first (git_add) before git_commit, so it's unclear whether the assistant should call git_add or git_commit alone.
- git_add (seed 9): The request asks to both stage files and commit, which requires two distinct tool calls (git_add and git_commit), so no single tool fulfills the entire request.

## Metadata
- Model under test: claude-sonnet-5
- Generator model: claude-sonnet-5
- Seeds per tool: 10

## Proposed Fixes

### git_status — REJECTED
- Before: 'Shows the working tree status'
- After:  "Displays a summary of the repository's current state at repo_path, listing tracked/untracked and staged/unstaged file changes without showing diff content, branch lists, or commit history."
- Pass rate: 9/10 → 10/10, p-value 0.5000
- Reason: rejected: improvement not significant after correction

### git_commit — REJECTED
- Before: 'Records changes to the repository'
- After:  'Records a new commit in the Git repository at repo_path by permanently saving the currently staged changes (as added via git_add) along with the provided commit message, distinguishing it from git_add (which only stages changes) and git_status/git_diff variants (which only inspect changes without committing them).'
- Pass rate: 4/10 → 2/10, p-value 1.0000
- Reason: rejected: made things worse

### git_log — REJECTED
- Before: 'Shows the commit logs'
- After:  'Retrieves the commit history for the repository at the given required `repo_path`, optionally limited to the most recent `max_count` commits and/or filtered to commits made between the optional `start_timestamp` and `end_timestamp`, unlike `git_show` (which displays the full contents of a single specified commit) or `git_diff`/`git_diff_staged`/`git_diff_unstaged` (which show line-level changes rather than a list of commits).'
- Pass rate: 9/10 → 9/10, p-value 1.0000
- Reason: rejected: no change
