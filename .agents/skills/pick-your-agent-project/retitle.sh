#!/usr/bin/env bash
#
# retitle.sh — deterministic helper for the pick-your-agent-project skill.
#
# Problem: after the brainstorm skill writes project_brief.md, participants
# are supposed to rename their existing scaffolded agent project to match the
# brief. When that step is skipped (or done by hand and gets it wrong), the
# next prompt often makes the coding agent scaffold a SECOND project instead
# of continuing to build on the first one — which is the #1 source of
# confusion reported from the first run of this lab.
#
# This script does the mechanical, error-prone parts so a weaker model
# doesn't have to (and can't get them wrong): find the project, work out the
# new name from the brief, rename the project folder, and replace the old
# name everywhere it's baked into the project's own files (manifest,
# pyproject, generated telemetry/service-name constants). It does NOT touch
# app code logic, tools, or the agent's persona — that's the one part left
# for the coding agent to do afterward (see SKILL.md).
#
# Usage:
#   bash .agents/skills/pick-your-agent-project/retitle.sh
#
# Run from the workspace root (where project_brief.md lives) or from inside
# the scaffolded project itself — the script looks in both places.
#
# Exits 0 (no-op, with a message) if there's no project_brief.md, no
# scaffolded project, or the project is already named correctly. Never
# fails the caller's flow.
#
set -euo pipefail

info() { printf '\033[1;34m›\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!\033[0m %s\n' "$*" >&2; }

# ---------------------------------------------------------------------------
# 1. Locate project_brief.md — cwd, or one level up (the brief usually lives
#    at the workspace root while the scaffolded project is a subfolder).
# ---------------------------------------------------------------------------
find_brief() {
  if [ -f "project_brief.md" ]; then printf '%s\n' "$(pwd)/project_brief.md"; return 0; fi
  if [ -f "../project_brief.md" ]; then printf '%s\n' "$(cd .. && pwd)/project_brief.md"; return 0; fi
  return 1
}

BRIEF="$(find_brief || true)"
if [ -z "$BRIEF" ]; then
  warn "No project_brief.md found in this directory or its parent — nothing to rename."
  exit 0
fi

# ---------------------------------------------------------------------------
# 2. Locate the scaffolded project — cwd if it has the manifest, else a
#    direct child directory that does.
# ---------------------------------------------------------------------------
find_project_dir() {
  if [ -f "agents-cli-manifest.yaml" ]; then printf '%s\n' "$(pwd)"; return 0; fi
  local d
  for d in */; do
    if [ -f "${d}agents-cli-manifest.yaml" ]; then printf '%s\n' "$(cd "$d" && pwd)"; return 0; fi
  done
  return 1
}

PROJECT_DIR="$(find_project_dir || true)"
if [ -z "$PROJECT_DIR" ]; then
  warn "No scaffolded agents-cli project found (no agents-cli-manifest.yaml here or in a subfolder) — nothing to rename."
  exit 0
fi

# ---------------------------------------------------------------------------
# 3. Derive the new name from the brief's "# My agent: <name>" line.
#    Slugify to the agents-cli project-name rules: lowercase, letters,
#    numbers, hyphens only, <=26 chars.
# ---------------------------------------------------------------------------
RAW_NAME="$(grep -m1 -iE '^#[[:space:]]*My agent:' "$BRIEF" 2>/dev/null | sed -E 's/^#[[:space:]]*[Mm]y [Aa]gent:[[:space:]]*//' | tr -d '\r' || true)"
if [ -z "$RAW_NAME" ]; then
  warn "Could not find a '# My agent: <name>' line in $BRIEF — nothing to rename."
  exit 0
fi

# Brief names are often "Name (descriptive subtitle)" — the subtitle repeats
# the one-liner and, left in, tends to blow past the 26-char limit and get
# truncated mid-word. Prefer just the part before a trailing "(...)".
NAME_NO_SUFFIX="$(printf '%s' "$RAW_NAME" | sed -E 's/[[:space:]]*\([^)]*\)[[:space:]]*$//')"
[ -n "$NAME_NO_SUFFIX" ] && RAW_NAME="$NAME_NO_SUFFIX"

SLUG="$(printf '%s' "$RAW_NAME" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"
SLUG="${SLUG:0:26}"
SLUG="$(printf '%s' "$SLUG" | sed -E 's/-+$//')"   # trim a hyphen left dangling by truncation
[ -n "$SLUG" ] || SLUG="my-agent"

# ---------------------------------------------------------------------------
# 4. Read the project's current name straight from pyproject.toml.
# ---------------------------------------------------------------------------
PYPROJECT="$PROJECT_DIR/pyproject.toml"
if [ ! -f "$PYPROJECT" ]; then
  warn "No pyproject.toml in $PROJECT_DIR — nothing to rename."
  exit 0
fi

OLD_NAME="$(grep -m1 -E '^name[[:space:]]*=' "$PYPROJECT" | sed -E 's/^name[[:space:]]*=[[:space:]]*"([^"]*)".*/\1/')"
if [ -z "$OLD_NAME" ]; then
  warn "Could not read [project].name from $PYPROJECT — nothing to rename."
  exit 0
fi

if [ "$OLD_NAME" = "$SLUG" ]; then
  ok "Project is already named '$SLUG' — nothing to do."
  echo "NEXT: continue in $PROJECT_DIR — update the root agent's instruction in its agent file to match project_brief.md, then continue the lab."
  exit 0
fi

info "Renaming project '$OLD_NAME' -> '$SLUG'"

# ---------------------------------------------------------------------------
# 5. Replace the old name inside the project's own files. Word-bounded
#    (via perl \b) so we only ever match the whole name, never a substring
#    of an unrelated identifier — this is what makes it safe to run even
#    when the name is a short, common-looking word.
#
#    Guard: skip the content replace entirely for names that are too short,
#    or that are common generic words likely to appear elsewhere in the
#    codebase for unrelated reasons (import names, directory names, etc).
#    In that case we still rename the folder and update just the manifest +
#    pyproject, which is always safe.
# ---------------------------------------------------------------------------
case "$OLD_NAME" in
  app|agent|api|src|main|test|tests|frontend|backend|server|client|agents|core|demo|sample)
    NARROW=1 ;;
  *)
    if [ "${#OLD_NAME}" -lt 4 ]; then NARROW=1; else NARROW=0; fi
    ;;
esac

cd "$PROJECT_DIR"

if [ "$NARROW" = "1" ]; then
  warn "Project name '$OLD_NAME' is short/common — only updating the name field in agents-cli-manifest.yaml and pyproject.toml (never agent_directory or other fields that may share the same word)."
  # Anchored to the "name" field specifically so a common word like "app" in
  # agent_directory (a separate field, often equal to the old project name)
  # is never touched.
  perl -pi -e "s/^name:(\\s*)\"?\\Q${OLD_NAME}\\E\"?(\\s*)\$/name:\$1${SLUG}\$2/" agents-cli-manifest.yaml
  perl -pi -e "s/^name(\\s*=\\s*)\"\\Q${OLD_NAME}\\E\"/name\$1\"${SLUG}\"/" pyproject.toml
else
  # Walk the project's own text files, skipping venvs/caches/locks/binaries.
  while IFS= read -r -d '' f; do
    if grep -qF "$OLD_NAME" "$f" 2>/dev/null; then
      perl -pi -e "s/\\b\\Q${OLD_NAME}\\E\\b/${SLUG}/g" "$f"
    fi
  done < <(find . \
      \( -path './.venv' -o -path './.git' -o -path './.adk' -o -path './.google-agents-cli' \
         -o -path './.ruff_cache' -o -name '__pycache__' -o -name 'node_modules' \) -prune -o \
      -type f \( -name '*.py' -o -name '*.toml' -o -name '*.yaml' -o -name '*.yml' \
                 -o -name '*.md' -o -name '*.json' -o -name '*.cfg' -o -name '*.ini' \
                 -o -name '*.tf' -o -name '*.tfvars' \) \
      ! -name 'uv.lock' ! -name 'package-lock.json' -print0)
fi

ok "Updated project name references in $PROJECT_DIR"

# ---------------------------------------------------------------------------
# 6. Rename the project folder itself (do this last, after in-place edits,
#    so every edit above used stable relative paths).
# ---------------------------------------------------------------------------
PROJECT_ABS="$(pwd)"
PROJECT_PARENT="$(dirname "$PROJECT_ABS")"
PROJECT_BASE="$(basename "$PROJECT_ABS")"

if [ "$PROJECT_BASE" != "$SLUG" ]; then
  if [ -e "$PROJECT_PARENT/$SLUG" ]; then
    warn "A directory named '$SLUG' already exists next to the project — leaving the folder as '$PROJECT_BASE'."
  else
    cd "$PROJECT_PARENT"
    mv "$PROJECT_BASE" "$SLUG"
    PROJECT_ABS="$PROJECT_PARENT/$SLUG"
    ok "Renamed project folder to $PROJECT_ABS"
  fi
fi

cd "$PROJECT_ABS"

# ---------------------------------------------------------------------------
# 7. Verify with agents-cli, if it's on PATH. Never fatal.
# ---------------------------------------------------------------------------
if command -v agents-cli >/dev/null 2>&1; then
  if agents-cli info >/tmp/retitle_agents_cli_info.$$ 2>&1; then
    ok "agents-cli info confirms the project loads from $PROJECT_ABS"
  else
    warn "agents-cli info reported an issue after the rename — see /tmp/retitle_agents_cli_info.$$"
  fi
else
  warn "agents-cli not on PATH — skipping the agents-cli info verification step."
fi

echo
ok "Done. Project is now '$SLUG' at $PROJECT_ABS"
echo "NEXT: cd $PROJECT_ABS, then update the root agent's instruction (its persona/system prompt) in the agent file under $PROJECT_ABS to match project_brief.md. Do not add tools, memory, storage, or deploy yet — that happens in the lab steps that follow."
