# Watson Agent patcher module
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

_A_PREFIX = re.compile(r"^---\s+a\/", re.M)
_B_PREFIX = re.compile(r"^\+\+\+\s+b\/", re.M)
_FILE_HDR = re.compile(r"^(\-\-\-|\+\+\+)\s+[ab]\/", re.M)
_HEADER_RE = re.compile(r'^(---)\s+(.*?)\r?\n(\+\+\+)\s+(.*?)\r?$', re.M)
_HUNK_RE = re.compile(r'^\@\@[\s\-\+0-9,]+\@\@', re.M)
_HUNK_FULL_RE = re.compile(r'^\@\@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? \@\@', re.M)


def _strip_ab_prefixes(text: str) -> str:
    text = _A_PREFIX.sub("--- ", text)
    text = _B_PREFIX.sub("+++ ", text)
    return _FILE_HDR.sub(lambda m: m.group(0)[:4], text)


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _strip_git_metadata(text: str) -> str:
    """Remove git-specific metadata lines that may cause git apply to fail."""
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        # Skip diff --git, index, new/deleted file mode, similarity, etc.
        if line.startswith(('diff --git', 'index ', 'new file mode', 'deleted file mode', 
                           'similarity index', 'rename from', 'rename to', 'copy from', 'copy to')):
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)


def _write_temp_diff(patch_text: str) -> str:
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".diff", mode="w", encoding="utf-8", newline="\n")
    f.write(patch_text)
    f.close()
    return f.name


def _validate_unified_diff(txt: str) -> tuple[bool, str]:
    """Validates unified diff structure and consistency."""
    header = _HEADER_RE.search(txt)
    if not header:
        return False, "missing unified diff headers (--- / +++)"
    if not _HUNK_RE.search(txt):
        return False, "missing @@ hunk markers"
    
    # Check hunk markers are well-formed
    for match in _HUNK_FULL_RE.finditer(txt):
        old_start, old_count, new_start, new_count = match.groups()
        if not old_start or not new_start:
            return False, f"malformed hunk marker: {match.group(0)}"
    
    old_name = header.group(2).strip()
    new_name = header.group(4).strip()
    
    def _clean(name: str) -> str:
        return re.sub(r'^(a/|b/)', '', name)
    
    old_clean = _clean(old_name)
    new_clean = _clean(new_name)
    
    if old_name != "/dev/null" and new_name != "/dev/null" and old_clean != new_clean:
        return False, f"inconsistent filenames: {old_name} vs {new_name}"
    
    return True, "ok"


def _git_apply_check(repo: str, diff_path: str) -> tuple[bool, str]:
    """Dry-run check if patch can be applied."""
    cmd = ["git", "-C", repo, "apply", "--check", diff_path]
    p = subprocess.run(cmd, capture_output=True, text=True)
    ok = p.returncode == 0
    out = f"$ {' '.join(cmd)}\n{p.stdout}{p.stderr}"
    return ok, out


def _apply_unified_diff_in_memory(repo_path: str, diff_text: str) -> tuple[bool, str]:
    """
    CONSERVATIVE fallback: parses hunks and applies line-by-line without git.
    Supports MODIFIED/ADDED simple cases only (no renames, no binary).
    Returns (ok, log).
    """
    log = []
    try:
        parts = _HEADER_RE.split(diff_text)
        if len(parts) < 5:
            return False, "fallback: no header blocks"
        
        # Process each file block
        i = 1
        while i < len(parts):
            if i + 3 >= len(parts):
                break
            old_path = parts[i + 1].strip()
            new_path = parts[i + 3].strip()
            body = parts[i + 4] if i + 4 < len(parts) else ""
            
            def clean(p):
                return re.sub(r'^(a/|b/)', '', p)
            
            old_clean = clean(old_path)
            new_clean = clean(new_path)
            
            file_created = (old_path == "/dev/null")
            file_deleted = (new_path == "/dev/null")
            target_path = new_clean if not file_deleted else old_clean
            abs_path = Path(repo_path) / target_path
            
            if file_created:
                # Create new file from added lines
                content_lines = []
                for line in body.splitlines(keepends=False):
                    if line.startswith('+') and not line.startswith('+++'):
                        content_lines.append(line[1:])
                abs_path.parent.mkdir(parents=True, exist_ok=True)
                abs_path.write_text("\n".join(content_lines), encoding="utf-8")
                log.append(f"created {target_path} ({len(content_lines)} lines)")
                i += 5
                continue
            
            if file_deleted:
                if abs_path.exists():
                    abs_path.unlink()
                    log.append(f"deleted {target_path}")
                i += 5
                continue
            
            if not abs_path.exists():
                log.append(f"skip {target_path}: not found")
                i += 5
                continue
            
            # Read original file
            original = abs_path.read_text(encoding="utf-8").splitlines(keepends=False)
            result = original[:]
            cursor = 0
            
            # Parse and apply hunks
            for line in body.splitlines(keepends=False):
                if line.startswith('@@'):
                    continue
                elif line.startswith(' '):
                    # Context line - sync cursor
                    ctx = line[1:]
                    while cursor < len(result) and result[cursor] != ctx:
                        cursor += 1
                    if cursor < len(result):
                        cursor += 1
                elif line.startswith('-') and not line.startswith('---'):
                    # Delete line
                    to_del = line[1:]
                    found = None
                    for j in range(max(0, cursor - 3), min(len(result), cursor + 3)):
                        if result[j] == to_del:
                            found = j
                            break
                    if found is not None:
                        del result[found]
                        cursor = found
                elif line.startswith('+') and not line.startswith('+++'):
                    # Add line
                    to_add = line[1:]
                    result.insert(cursor, to_add)
                    cursor += 1
            
            # Write back
            abs_path.write_text("\n".join(result), encoding="utf-8")
            log.append(f"patched {target_path} (fallback, {len(result)} lines)")
            i += 5
        
        return True, "\n".join(log)
    except Exception as e:
        return False, f"fallback error: {e}"


def _try_git_apply(repo: str, diff_path: str, extra: list[str]) -> tuple[bool, str]:
    cmd = ["git", "-C", repo, "apply", "--whitespace=nowarn", "--reject"] + extra + [diff_path]
    p = subprocess.run(cmd, capture_output=True, text=True)
    ok = p.returncode == 0
    out = f"$ {' '.join(cmd)}\n{p.stdout}{p.stderr}"
    return ok, out


def apply_patch(repo_root: str, unified_diff: str) -> tuple[bool, str]:
    """
    Smart unified diff apply with validation:
      0) Validate diff structure and consistency
      1) git apply --check (dry-run)
      2) git apply (reject/nowarn)
      3) git apply with ignore whitespace
      4) strip a/ b/ prefixes and retry steps 1-3
      5) fallback: -p0, --unidiff-zero
    Returns (ok, log). Also writes patch.last.diff in repo for debugging.
    """
    repo = os.path.abspath(repo_root)
    os.makedirs(repo, exist_ok=True)

    # Save last diff for debugging
    try:
        with open(os.path.join(repo, "patch.last.diff"), "w", encoding="utf-8", newline="\n") as f:
            f.write(unified_diff)
    except Exception:
        pass

    base = _normalize_newlines(unified_diff)
    base = _strip_git_metadata(base)  # Remove diff --git, index, etc.
    logs: list[str] = []
    
    # PRE-VALIDATION
    valid, reason = _validate_unified_diff(base)
    logs.append(f"[validate] {reason}")
    if not valid:
        # Try stripping prefixes and re-validate
        stripped = _strip_ab_prefixes(base)
        valid2, reason2 = _validate_unified_diff(stripped)
        logs.append(f"[validate after strip] {reason2}")
        if not valid2:
            return False, "\n".join(logs)
        base = stripped
    
    tmp1 = _write_temp_diff(base)
    
    # DRY-RUN CHECK
    check_ok, check_out = _git_apply_check(repo, tmp1)
    logs.append(f"[git apply --check]\n{check_out}")
    
    # Strategy 1: standard apply
    ok, out = _try_git_apply(repo, tmp1, [])
    logs.append(out)
    if ok:
        os.unlink(tmp1)
        return True, "\n".join(logs)

    # Strategy 2: ignore whitespace
    ok2, out2 = _try_git_apply(repo, tmp1, ["--ignore-space-change", "--ignore-whitespace"])
    logs.append(out2)
    if ok2:
        os.unlink(tmp1)
        return True, "\n".join(logs)

    # Strategy 3: strip prefixes and retry
    stripped = _strip_ab_prefixes(base)
    tmp2 = _write_temp_diff(stripped)
    ok3, out3 = _try_git_apply(repo, tmp2, [])
    logs.append(out3)
    if ok3:
        os.unlink(tmp1); os.unlink(tmp2)
        return True, "\n".join(logs)

    # Strategy 4: strip + ignore whitespace
    ok4, out4 = _try_git_apply(repo, tmp2, ["--ignore-space-change", "--ignore-whitespace"])
    logs.append(out4)
    if ok4:
        os.unlink(tmp1); os.unlink(tmp2)
        return True, "\n".join(logs)
    
    # Strategy 5: fallback -p0
    ok5, out5 = _try_git_apply(repo, tmp2, ["-p0"])
    logs.append(out5)
    if ok5:
        os.unlink(tmp1); os.unlink(tmp2)
        return True, "\n".join(logs)
    
    # Strategy 6: fallback --unidiff-zero
    ok6, out6 = _try_git_apply(repo, tmp2, ["--unidiff-zero"])
    logs.append(out6)
    
    try:
        os.unlink(tmp1); os.unlink(tmp2)
    except Exception:
        pass
    
    if ok6:
        os.unlink(tmp1); os.unlink(tmp2)
        return True, "\n".join(logs)
    
    # Strategy 7: FALLBACK without git (in-memory patch)
    ok_fb, fb_log = _apply_unified_diff_in_memory(repo, base)
    logs.append(f"[fallback in-memory]\n{fb_log}")
    
    try:
        os.unlink(tmp1); os.unlink(tmp2)
    except Exception:
        pass
    
    return ok_fb, "\n".join(logs)


