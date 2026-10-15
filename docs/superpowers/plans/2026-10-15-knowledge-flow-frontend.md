# Knowledge Flow Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Save the approved minimal frontend, apply it to the upload homepage, and merge the reviewed change into the original `main` branch.

**Architecture:** Keep the existing native frontend and backend routes. Extract the approved page styling and background motion into local CSS/JavaScript; retain upload, reordering, removal and task creation behavior. Save the standalone offline preview separately.

**Tech Stack:** HTML, CSS, native JavaScript, FastAPI static routes, pytest, Node.js regression checks.

**Spec:** User-approved `frontend-preview.html`: quiet gray-green UI, mathematical formulas and code rising from bottom to top, background intensity 30%, manual play/pause even when reduced motion is enabled.

**Record:** This file records the implementation plan; final validation and delivery are recorded in the verification note and GitHub PR.

## Global Constraints

- Original and merge target branch: `main`; feature branch: `codex/refine-frontend-with-knowledge-flow`.
- No new AI integration, backend workflows, external frontend dependencies or build step.
- Preserve real homepage upload controls and existing task API routes.
- Keep `frontend-preview.html` usable offline without a backend.
- Honor reduced motion by default, with an enabled explicit play button.

## Review Focus

- Reduced motion: a visitor can explicitly start and pause the background.
- File ordering: moving and removing files keeps logical page order and counts accurate.
- Pending uploads: list actions cannot unlock submission or create duplicate tasks; failures allow retry.
- Filenames containing HTML: display as text.
- Narrow layouts: controls wrap and long filenames remain readable.
- Existing endpoints: homepage assets load and backend regression suite remains green.

### Task 1: Save approved homepage and preview

**Files:** `frontend-preview.html`; `lecture-syllabus-generator/frontend/index.html`; `frontend/css/home.css`; `frontend/js/knowledge-flow.js`; `frontend/js/upload.js`; `README.md`.

- [x] Apply the approved composition and motion controls to the existing homepage.
- [x] Preserve file selection, sorting, removal and task creation with safe filename rendering.
- [x] Verify motion preference behavior, upload interactions and asset delivery using isolated regression checks.
- [x] Run the backend test suite and review the diff before committing.

### Task 2: Publish and merge

- [ ] Commit and push the feature branch.
- [ ] Create a PR targeting `main`, describing the reason, result and validation.
- [ ] Attach the PR to this chat, merge the reviewed head and add the requested explanatory comment.
- [ ] Update local `main` to the merge result and verify branch synchronization.
