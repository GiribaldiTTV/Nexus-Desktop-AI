import configparser
import datetime
import json
import os
import platform
import re
import shutil
import urllib.parse
import zipfile


DEFAULT_GITHUB_ISSUES_NEW_URL = "https://github.com/GiribaldiTTV/Jarvis/issues/new"
SUPPORT_BUNDLE_FOLDER = "support_bundles"
MANIFEST_FILENAME = "manifest.json"
VERSION_CLOSEOUT_PATTERN = re.compile(r"^v(\d+)\.(\d+)\.(\d+)_closeout\.md$")


class SupportBundleError(RuntimeError):
    pass


def normalize_path(path):
    return os.path.normcase(os.path.normpath(os.path.abspath(path)))


def derive_run_identity(runtime_log_path):
    stem = os.path.splitext(os.path.basename(runtime_log_path))[0]
    if stem.startswith("Runtime_"):
        return stem[len("Runtime_"):]
    return stem or "unknown_run"


def make_safe_name(value):
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return safe or "bundle"


def detect_jarvis_version(root_dir):
    docs_dir = os.path.join(root_dir, "docs")
    best = None

    try:
        for entry in os.scandir(docs_dir):
            if not entry.is_file():
                continue
            match = VERSION_CLOSEOUT_PATTERN.match(entry.name)
            if not match:
                continue
            version_tuple = tuple(int(part) for part in match.groups())
            if best is None or version_tuple > best:
                best = version_tuple
    except OSError:
        return "unknown"

    if best is None:
        return "unknown"

    return f"v{best[0]}.{best[1]}.{best[2]}"


def read_runtime_log_reference(crash_log_path):
    try:
        with open(crash_log_path, "r", encoding="utf-8", errors="ignore") as handle:
            for _ in range(80):
                line = handle.readline()
                if not line:
                    break
                if line.startswith("Runtime Log:"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        return None
    return None


def find_matching_crash_log(runtime_log_path, crash_dir):
    if not os.path.isdir(crash_dir):
        return None

    runtime_norm = normalize_path(runtime_log_path)
    candidates = []

    try:
        for entry in os.scandir(crash_dir):
            if not entry.is_file() or not entry.name.lower().endswith(".txt"):
                continue
            candidates.append((entry.stat().st_mtime, entry.path))
    except OSError:
        return None

    for _, crash_log_path in sorted(candidates, reverse=True):
        referenced_runtime = read_runtime_log_reference(crash_log_path)
        if not referenced_runtime:
            continue
        if normalize_path(referenced_runtime) == runtime_norm:
            return crash_log_path

    return None


def parse_github_repo_url(remote_url):
    cleaned = (remote_url or "").strip()
    if not cleaned:
        return None

    path = None
    if cleaned.startswith("git@github.com:"):
        path = cleaned[len("git@github.com:"):]
    elif cleaned.startswith("https://github.com/"):
        path = cleaned[len("https://github.com/"):]
    elif cleaned.startswith("http://github.com/"):
        path = cleaned[len("http://github.com/"):]
    elif cleaned.startswith("ssh://git@github.com/"):
        path = cleaned[len("ssh://git@github.com/"):]

    if path is None:
        return None

    if path.endswith(".git"):
        path = path[:-4]

    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        return None

    return f"https://github.com/{parts[0]}/{parts[1]}"


def detect_github_issues_new_url(root_dir):
    config_path = os.path.join(root_dir, ".git", "config")

    try:
        parser = configparser.ConfigParser()
        parser.read(config_path, encoding="utf-8")
        for section_name in ('remote "origin"', 'remote "upstream"'):
            if parser.has_option(section_name, "url"):
                repo_url = parse_github_repo_url(parser.get(section_name, "url"))
                if repo_url:
                    return f"{repo_url}/issues/new"
    except Exception:
        pass

    return DEFAULT_GITHUB_ISSUES_NEW_URL


def build_environment_summary():
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
    }


def ensure_support_bundle_dir(runtime_log_path):
    support_dir = os.path.join(os.path.dirname(runtime_log_path), SUPPORT_BUNDLE_FOLDER)
    os.makedirs(support_dir, exist_ok=True)
    return support_dir


def choose_bundle_basename(support_dir, run_identity):
    base = f"JarvisSupport_{make_safe_name(run_identity)}"
    candidate = base
    suffix = 2

    while (
        os.path.exists(os.path.join(support_dir, candidate))
        or os.path.exists(os.path.join(support_dir, f"{candidate}.zip"))
    ):
        candidate = f"{base}_{suffix}"
        suffix += 1

    return candidate


def create_support_bundle(root_dir, runtime_log_path, crash_dir):
    if not runtime_log_path:
        raise SupportBundleError("No runtime log was provided by diagnostics.")

    runtime_log_path = os.path.abspath(runtime_log_path)
    if not os.path.isfile(runtime_log_path):
        raise SupportBundleError("The runtime log for this report could not be found.")

    run_identity = derive_run_identity(runtime_log_path)
    support_dir = ensure_support_bundle_dir(runtime_log_path)
    bundle_basename = choose_bundle_basename(support_dir, run_identity)
    staging_dir = os.path.join(support_dir, bundle_basename)
    bundle_path = os.path.join(support_dir, f"{bundle_basename}.zip")

    os.makedirs(staging_dir, exist_ok=False)

    runtime_log_name = os.path.basename(runtime_log_path)
    crash_log_path = find_matching_crash_log(runtime_log_path, crash_dir)
    crash_log_name = os.path.basename(crash_log_path) if crash_log_path else None

    bundled_files = [
        {"name": runtime_log_name, "kind": "runtime_log"},
    ]
    if crash_log_name:
        bundled_files.append({"name": crash_log_name, "kind": "crash_log"})
    bundled_files.append({"name": MANIFEST_FILENAME, "kind": "manifest"})

    manifest = {
        "jarvis_version": detect_jarvis_version(root_dir),
        "run_identity": run_identity,
        "bundle_created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "environment_summary": build_environment_summary(),
        "bundled_files": bundled_files,
        "manual_review_required": True,
        "manual_issue_submission_required": True,
    }

    try:
        shutil.copy2(runtime_log_path, os.path.join(staging_dir, runtime_log_name))
        if crash_log_path and os.path.isfile(crash_log_path):
            shutil.copy2(crash_log_path, os.path.join(staging_dir, crash_log_name))

        manifest_path = os.path.join(staging_dir, MANIFEST_FILENAME)
        with open(manifest_path, "w", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2, sort_keys=True)

        with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for entry_name in sorted(os.listdir(staging_dir)):
                entry_path = os.path.join(staging_dir, entry_name)
                archive.write(entry_path, arcname=f"{bundle_basename}/{entry_name}")
    except Exception as exc:
        raise SupportBundleError(f"Support bundle creation failed: {exc}") from exc
    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)

    return {
        "bundle_path": bundle_path,
        "bundle_name": os.path.basename(bundle_path),
        "runtime_log_name": runtime_log_name,
        "crash_log_name": crash_log_name,
        "run_identity": run_identity,
        "jarvis_version": manifest["jarvis_version"],
        "manifest": manifest,
    }


def build_issue_prefill_url(root_dir, bundle_info):
    issues_new_url = detect_github_issues_new_url(root_dir)
    crash_log_label = bundle_info["crash_log_name"] or "not included"

    body_lines = [
        "## Summary",
        "",
        "Please describe what happened.",
        "",
        "## Support Bundle",
        "",
        "- Review the local support bundle before sharing.",
        f"- Attach the bundle manually before submitting: `{bundle_info['bundle_name']}`",
        "",
        "## Included Artifacts",
        "",
        f"- Runtime log: `{bundle_info['runtime_log_name']}`",
        f"- Crash log: `{crash_log_label}`",
        f"- Manifest: `{MANIFEST_FILENAME}`",
        "",
        "## Run Context",
        "",
        f"- Jarvis version: `{bundle_info['jarvis_version']}`",
        f"- Run identity: `{bundle_info['run_identity']}`",
    ]

    query = urllib.parse.urlencode(
        {
            "title": f"Support bundle report: {bundle_info['run_identity']}",
            "body": "\n".join(body_lines),
        }
    )
    return f"{issues_new_url}?{query}"
