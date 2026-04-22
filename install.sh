#!/usr/bin/env bash
# cml-skills — install Claude Code skills for a user.
#
# Symlinks each top-level skill directory in this repo into ~/.claude/skills/
# so that Claude Code picks them up automatically.
#
# Usage:
#   ./install.sh              # symlink every skill
#   ./install.sh <name> ...   # symlink only named skills
#   ./install.sh --list       # list available skills
#   ./install.sh --copy       # copy instead of symlink (falls out of sync)
#   ./install.sh --dry-run    # show what would happen, don't do it

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skills_dir="${HOME}/.claude/skills"

mode="symlink"
dry=""
list_only=""
requested=()

for arg in "$@"; do
  case "$arg" in
    --copy)     mode="copy" ;;
    --dry-run)  dry="echo [dry-run]" ;;
    --list)     list_only=1 ;;
    -h|--help)
      sed -n '2,14p' "${BASH_SOURCE[0]}"
      exit 0
      ;;
    *)          requested+=("$arg") ;;
  esac
done

discover_skills() {
  for d in "$repo_root"/*/; do
    name="$(basename "$d")"
    # Skip non-skill directories.
    [[ "$name" == ".git" || "$name" == ".github" ]] && continue
    [[ -f "$d/SKILL.md" ]] || continue
    echo "$name"
  done
}

all_skills=()
while IFS= read -r s; do all_skills+=("$s"); done < <(discover_skills)

if [[ -n "$list_only" ]]; then
  printf 'Available skills in %s:\n' "$repo_root"
  for s in "${all_skills[@]}"; do printf '  %s\n' "$s"; done
  exit 0
fi

# Determine which skills to install.
if [[ ${#requested[@]} -eq 0 ]]; then
  to_install=("${all_skills[@]}")
else
  to_install=()
  for want in "${requested[@]}"; do
    found=0
    for have in "${all_skills[@]}"; do
      [[ "$want" == "$have" ]] && { to_install+=("$have"); found=1; break; }
    done
    if [[ "$found" -eq 0 ]]; then
      echo "error: unknown skill '$want' (use --list to see available)" >&2
      exit 1
    fi
  done
fi

$dry mkdir -p "$skills_dir"

for s in "${to_install[@]}"; do
  src="$repo_root/$s"
  dest="$skills_dir/$s"

  if [[ -e "$dest" || -L "$dest" ]]; then
    $dry rm -rf "$dest"
  fi

  if [[ "$mode" == "copy" ]]; then
    $dry cp -r "$src" "$dest"
    printf 'copied  %s -> %s\n' "$src" "$dest"
  else
    $dry ln -s "$src" "$dest"
    printf 'linked  %s -> %s\n' "$dest" "$src"
  fi
done

echo
echo "Done. Verify with:"
echo "  ls -la ~/.claude/skills/"
