# Images History Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove retired `/images/` blobs from Git history and verify a measurable reduction in the GitHub repository without changing the approved site output.

**Architecture:** Perform the rewrite in a disposable mirror clone, protected by a full bundle backup and immutable before/after content manifests. Use `git filter-repo` with an exact path rule, validate the rewritten branch in a clean checkout, then request separate authorization for the force push.

**Tech Stack:** Git, git-filter-repo, SHA-256 manifests, static-site reference audit, Chromium smoke tests, GitHub Pages.

## Global Constraints

- This plan is blocked until the functional reconciliation preview and Task 11 of the companion plan are explicitly approved.
- Never rewrite history in the user's working repository or active worktree.
- Never force-push without a separate explicit approval immediately before the push.
- Preserve a verified Git bundle and the original remote refs.
- Remove only the exact historical path `images/`; do not broadly delete files by extension.
- The approved site output and active `/img/images/` hashes must be identical before and after rewriting.
- Warn that all other clones must be recreated or realigned after the force push.

---

### Task 1: Capture the pre-rewrite baseline and recovery artifacts

**Files:**
- Create: `docs/acervo/history-cleanup-report.md`
- Create outside repository: `/tmp/crisanti-history-cleanup-<timestamp>/`

- [ ] **Step 1: Confirm the functional gate and a clean committed source branch**
- [ ] **Step 2: Record remote refs, object counts, pack size, branch SHA, and active asset hashes**
- [ ] **Step 3: Create and verify a full Git bundle in the temporary safety directory**
- [ ] **Step 4: Create a mirror clone in the same temporary directory**
- [ ] **Step 5: Record exact recovery commands in the report and commit it before rewriting anything**

### Task 2: Dry-run the exact history filter in a disposable clone

**Files:**
- Modify in disposable mirror only: Git object database and refs
- Modify: `docs/acervo/history-cleanup-report.md`

- [ ] **Step 1: Verify `git filter-repo` availability and version**
- [ ] **Step 2: Clone the mirror again as a throwaway rehearsal target**
- [ ] **Step 3: Run the exact filter rule `--path images --invert-paths` in the rehearsal clone**
- [ ] **Step 4: Confirm no historical `images/` paths remain and `/img/images/` remains intact**
- [ ] **Step 5: Measure reclaimed object and pack size and record the rehearsal result**

Expected: `git log --all -- images` returns no commits in the rehearsal repository, while the active branch contains all approved `img/images/**` files.

### Task 3: Validate the rewritten site from a clean checkout

**Files:**
- Create outside repository: clean checkout beneath the temporary safety directory
- Modify: `docs/acervo/history-cleanup-report.md`

- [ ] **Step 1: Check out the rewritten branch from the rehearsal mirror into a fresh directory**
- [ ] **Step 2: Run `tools/acervo/audit_references.py` and the full unit suite**
- [ ] **Step 3: Run the PT/ES browser smoke suite**
- [ ] **Step 4: Compare every active asset hash with the pre-rewrite manifest**
- [ ] **Step 5: Record pass/fail evidence and the exact before/after sizes**

Any mismatch blocks the rewrite; restore from the bundle or discard the disposable clone rather than patching around it.

### Task 4: Prepare the coordinated rewrite handoff

**Files:**
- Modify: `docs/acervo/history-cleanup-report.md`

- [ ] **Step 1: Fetch the remote and verify it has not advanced since the baseline**
- [ ] **Step 2: Enumerate every ref that would change and every protected branch constraint**
- [ ] **Step 3: Document clone recovery/re-alignment instructions for collaborators**
- [ ] **Step 4: Present the measured savings, validation evidence, affected refs, and rollback bundle to the user**
- [ ] **Step 5: Stop and request explicit authorization for the destructive force push**

### Task 5: Execute and verify the authorized force push

**Files:**
- Modify remote Git refs only after explicit authorization
- Finalize: `docs/acervo/history-cleanup-report.md`

- [ ] **Step 1: Reconfirm remote refs have not changed**
- [ ] **Step 2: Apply the already rehearsed filter to the protected mirror clone**
- [ ] **Step 3: Repeat hash, reference, unit, and browser checks**
- [ ] **Step 4: Force-push only the enumerated refs using the safest supported lease/ref checks**
- [ ] **Step 5: Fetch from GitHub, verify remote SHAs and repository size, then publish collaborator recovery instructions**

If the remote changes between approval and push, abort and return to Task 4. Never override unrelated remote work.
