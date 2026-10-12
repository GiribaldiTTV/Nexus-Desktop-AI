"""Validate bounded dev-only source-owner markers."""
from __future__ import annotations
import io, re, tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INV = Path("Docs/branch_plans/feature_repo_wide_source_owner_marker_adoption_inventory.md")
PFX = "NEXUS-SOURCE-OWNER:"
LEGACY = "NDAI-" + "SRCOWN"
ROW = re.compile(r"^\| `(?P<path>[^`]+)` \| `(?P<owner>[^`]+)` \| `(?P<ledger>[^`]+)` \| `(?P<surface>[^`]+)` \| `(?P<status>[^`]+)` \|")
ROOTS = (Path("desktop"), Path("dev"), Path("nexus_visual"), Path("Docs"))
EXTS = {".py", ".ps1", ".js", ".css", ".html", ".md"}
PROD = (Path("desktop/desktop_renderer.py"), Path("nexus_visual/orin_core.html"), Path("nexus_visual/orin_core_desktop.html"), Path("nexus_visual/orin_core.css"), Path("nexus_visual/orin_core_desktop.css"), Path("nexus_visual/orin_core.js"), Path("nexus_visual/monitoring_hud.html"), Path("nexus_visual/monitoring_hud.css"), Path("nexus_visual/monitoring_hud.js"))
FORBID = (PFX, LEGACY, "SRCOWN-" + "MARK-", "source-owner label", "source owner marker", "review badge", "ledger tooltip")
KV = re.compile(r"([a-z]+)=([^;\s`<>]+)")
LEDGER = re.compile(r"\b[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+-\d{3}\b")

# NEXUS-SOURCE-OWNER: schema=source-owner-v1; owner=VALIDATOR-HELPER; ledger=SRCOWN-FIRSTPASS-VALIDATOR-010; surface=source-owner-marker-validator; status=canonical

def read(p: Path) -> str:
    return (ROOT / p).read_text(encoding="utf-8")

def files():
    for r in ROOTS:
        base = ROOT / r
        if base.exists():
            for p in base.rglob("*"):
                if p.is_file() and p.suffix.lower() in EXTS and not {"logs", "__pycache__", ".git"}.intersection(p.relative_to(ROOT).parts):
                    yield p.relative_to(ROOT)

def is_comment(p: Path, line: str) -> bool:
    s = line.lstrip("\ufeff").lstrip(); ext = p.suffix.lower()
    return (ext in {".md", ".html"} and s.startswith("<!--")) or (ext in {".py", ".ps1"} and s.startswith("#")) or (ext == ".js" and (s.startswith("//") or s.startswith("/*"))) or (ext == ".css" and s.startswith("/*"))

def strip_comments(p: Path) -> str:
    text = read(p)
    if p.suffix.lower() == ".py":
        return "".join(t.string for t in tokenize.generate_tokens(io.StringIO(text).readline) if t.type != tokenize.COMMENT)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)

def validate_historical_adoption() -> list[str]:
    fails: list[str] = []
    inv = read(INV) if (ROOT / INV).exists() else ""
    if not inv: fails.append(f"{INV}: inventory artifact is missing")
    for phrase in ("first-pass adoption surfaces", "deferred surfaces", "production ui exclusion", "inventory-only", "compact-ai", "fam-007"):
        if phrase not in inv.casefold(): fails.append(f"{INV}: missing inventory phrase {phrase!r}")
    expected = []
    for line in inv.splitlines():
        m = ROW.match(line)
        if m:
            expected.append((Path(m.group("path")), m.group("owner"), m.group("ledger"), m.group("surface"), m.group("status")))
    docs = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "Docs").rglob("*.md"))
    ledgers = set(LEDGER.findall(docs))
    found: dict[tuple[Path, str], tuple[int, dict[str, str]]] = {}
    for p in files():
        for n, line in enumerate(read(p).splitlines(), 1):
            if PFX in line:
                if p.suffix.lower() == ".md" and not is_comment(p, line): continue
                if not is_comment(p, line): continue
                vals = dict(KV.findall(line)); mid = vals.get("id", "")
                for key in ("schema", "owner", "ledger", "surface", "status"):
                    if key not in vals: fails.append(f"{p}:{n}: marker missing {key}")
                if vals.get("schema") != "source-owner-v1": fails.append(f"{p}:{n}: unsupported schema {vals.get('schema')!r}")
                if vals.get("status") not in {"canonical", "shared", "external"}: fails.append(f"{p}:{n}: unsupported status {vals.get('status')!r}")
                if vals.get("owner") not in {"FAM006-HUD", "FAM007-AI", "GOV-SOURCE-TRUTH", "RELEASE-READINESS", "VALIDATOR-HELPER", "SHARED-DESKTOP-CORE", "SHARED-DOCS", "COMPACT-AI-PROTECTED", "HISTORICAL-EVIDENCE"}: fails.append(f"{p}:{n}: unsupported owner {vals.get('owner')!r}")
                key = (p, vals.get("surface", ""))
                if key in found: fails.append(f"{p}:{n}: duplicate marker surface {vals.get('surface')!r}")
                found[key] = (n, vals)
            if LEGACY in line and not (p.suffix.lower() == ".md" and not is_comment(p, line)):
                fails.append(f"{p}:{n}: obsolete source-owner marker token remains")
    if not expected: fails.append(f"{INV}: missing first-pass adoption table")
    for path, owner, ledger, surface, status in expected:
        item = found.get((path, surface))
        if not item: fails.append(f"{path}: missing marker for {surface}"); continue
        n, vals = item
        for key, want in (("owner", owner), ("ledger", ledger), ("status", status)):
            if vals.get(key) != want: fails.append(f"{path}:{n}: {surface} {key} is {vals.get(key)!r}, expected {want!r}")
        if vals.get("ledger") not in ledgers: fails.append(f"{path}:{n}: unknown ledger {vals.get('ledger')}")
    for path, n, vals in [ (p, n, vals) for (p, _), (n, vals) in found.items() ]:
        if (path, vals.get("surface", "")) not in {(p, s) for p, _, _, s, _ in expected}: fails.append(f"{path}:{n}: unapproved first-pass marker {vals.get('surface')!r}")
    for p in PROD:
        stripped = strip_comments(p)
        for token in set(FORBID) | {ledger for _, _, ledger, _, _ in expected} | {surface for _, _, _, surface, _ in expected}:
            if token.casefold() in stripped.casefold(): fails.append(f"{p}: production UI exclusion failed for {token!r}")
    branch_record = read(Path("Docs/branch_records/feature_repo_wide_source_owner_marker_adoption.md"))
    for token in (
        "Compact-AI-Status-Card",
        "2f2354db",
        "ac16ca37",
        "protected",
        "salvage",
        "fold-down",
        "SRCOWN-COMPACT-AI-PRESERVE-014",
    ):
        if token not in branch_record: fails.append(f"Compact-AI preservation/fold-down source truth missing {token!r}")
    return fails

def validate() -> list[str]:
    """Current marker syntax and product exclusion; old inventory is not live authority."""
    fails = []
    for path in files():
        seen = set()
        for number, line in enumerate(read(path).splitlines(), 1):
            if PFX not in line or not is_comment(path, line):
                continue
            values = dict(KV.findall(line))
            if values.get('schema') != 'source-owner-v1' or not all(values.get(k) for k in ('owner', 'ledger', 'surface', 'status')):
                fails.append(f'{path}:{number}: malformed source owner metadata')
            if values.get('status') not in {'canonical', 'shared', 'external'}:
                fails.append(f'{path}:{number}: unsupported source owner status')
            if values.get('owner') not in {'FAM006-HUD', 'FAM007-AI', 'GOV-SOURCE-TRUTH', 'RELEASE-READINESS', 'VALIDATOR-HELPER', 'SHARED-DESKTOP-CORE', 'SHARED-DOCS', 'COMPACT-AI-PROTECTED', 'HISTORICAL-EVIDENCE'}:
                fails.append(f'{path}:{number}: unsupported source owner role')
            if not LEDGER.fullmatch(values.get('ledger', '')):
                fails.append(f'{path}:{number}: malformed historical ledger reference')
            if values.get('surface') in seen:
                fails.append(f'{path}:{number}: duplicate source owner surface')
            seen.add(values.get('surface'))
    for path in PROD:
        if not (ROOT / path).is_file():
            fails.append(f'{path}: production surface missing')
            continue
        text = strip_comments(path).casefold()
        for token in FORBID:
            if token.casefold() in text:
                fails.append(f'{path}: source owner metadata leaked into production')
    return fails

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--historical-adoption', action='store_true', help='Validate dated first-pass inventory as historical evidence.')
    args = parser.parse_args()
    failures = validate_historical_adoption() if args.historical_adoption else validate()
    print('BLOCK' if failures else 'PASS', ': source owner metadata validation')
    for failure in failures:
        print('- ' + failure)
    raise SystemExit(bool(failures))
