# Releasing a new version of the template

A short, repeatable checklist for cutting a new tagged release. The whole
thing takes about five minutes once you've done it a couple of times.

This template follows [Semantic Versioning](https://semver.org/) —
`MAJOR.MINOR.PATCH`.

| Bump | When |
|---|---|
| **PATCH** (e.g. `0.3.0` → `0.3.1`) | Bug fixes, doc clarifications, validator polish. |
| **MINOR** (e.g. `0.3.0` → `0.4.0`) | New opt-in features, new workflows / skills, new docs. Existing copies keep working. |
| **MAJOR** (e.g. `0.x` → `1.0.0`) | Breaking changes to `AGENTS.md`, the Memory Bank layout, or the validator's public flags. |

The version in [`VERSION`](../VERSION) always equals the latest git tag.

---

## The five-step checklist

### 1. Land your changes on `main`

Make sure everything you want in the release is committed and pushed to
`main`. The release is just a snapshot of `main` at a point in time —
nothing magical.

### 2. Update `VERSION`

Open [`VERSION`](../VERSION) and change the single line to the new number:

```text
0.4.0
```

No `v` prefix in the file. The `v` prefix is only used on the git tag.

### 3. Update `CHANGELOG.md`

Open [`../CHANGELOG.md`](../CHANGELOG.md):

1. Promote the `## Unreleased` section to a real version heading:

   ```markdown
   ## v0.4.0 — 2026-MM-DD — Short title

   ### Added
   - ...

   ### Changed
   - ...

   ### Fixed
   - ...
   ```

2. Add an empty `## Unreleased` section back at the top so future work has a
   place to land:

   ```markdown
   ## Unreleased

   _Nothing yet._
   ```

3. Use the `Added / Changed / Fixed / Removed / Security` sub-headings from
   [Keep a Changelog](https://keepachangelog.com/) where they apply. Omit
   any sub-heading that has no entries.

### 4. Validate, commit, tag, push

From the repo root:

```bash
# Verify the template still passes its own checks
python scripts/check-template.py

# Commit the release bookkeeping (VERSION + CHANGELOG)
git add VERSION CHANGELOG.md
git commit -m "chore(release): v0.4.0"

# Tag the commit
git tag -a v0.4.0 -m "v0.4.0"

# Push the commit and the tag together
git push origin main
git push origin v0.4.0
```

Use the `v` prefix on the git tag (`v0.4.0`, not `0.4.0`). GitHub's release
UI expects it and the README badges read it.

### 5. Publish the GitHub Release

This is the part that makes the new version visible on the repo's landing
page banner and sends a notification to anyone watching the repo.

1. Open `https://github.com/<owner>/<repo>/releases/new`.
2. **Choose a tag** → pick the `v0.4.0` tag you just pushed.
3. **Release title** → `v0.4.0 — Short title` (match the changelog heading).
4. **Description** → paste the relevant `CHANGELOG.md` section. Keep it
   short and scannable; users decide here whether to upgrade.
5. Tick **Set as the latest release**.
6. **Publish release**.

Done. The repo's right-hand sidebar now shows the new version, and the
"Latest release" badge in the README updates within a few minutes.

---

## Tips that save pain later

- **Push the tag separately.** `git push origin main` does not push tags.
  Forgetting `git push origin <tag>` is the most common failure mode.
- **Never reuse or move a tag.** If you tagged the wrong commit, make a new
  patch release instead. Rewriting a published tag breaks anyone who pulled
  the old one.
- **Keep `VERSION` and the tag in sync.** If you bump the tag, bump the
  file. The validator does not enforce this yet, but humans will notice.
- **One release = one logical change.** Don't bundle "new feature + bug
  fix + refactor" into one tag if you can avoid it. Smaller releases are
  easier to roll back and easier to write changelogs for.
- **Pre-releases are fine.** For experimental work, tag `v0.5.0-rc.1` and
  tick "Set as a pre-release" in the GitHub UI. Pre-releases don't update
  the "latest" badge.

---

## If you make a mistake

| Mistake | Fix |
|---|---|
| Forgot to push the tag | `git push origin v0.4.0` |
| Typo in changelog or release notes | Edit on GitHub (release notes) or land a follow-up commit + push (CHANGELOG). No re-tag needed. |
| Tagged the wrong commit | Don't move the tag. Tag a new patch (`v0.4.1`) on the right commit and note the regression in its changelog. |
| Published a release prematurely | Edit the release on GitHub and tick "Set as a pre-release," or delete the release (but leave the tag) and re-publish later. |
