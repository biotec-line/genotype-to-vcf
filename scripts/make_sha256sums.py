"""SHA256SUMS-Generator fuer Release-Artifacts in dist/.

Aufruf: python scripts/make_sha256sums.py [dist-dir]
Standard-Verzeichnis: dist/ relativ zum Projektroot.
Erzeugt: dist/SHA256SUMS (BSD-Format: "<hash>  <dateiname>")
"""

import hashlib
import sys
from pathlib import Path


RELEASE_PATTERNS = ["*.exe", "*.zip", "*.tar.gz", "*.whl"]


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_sums(directory: Path, patterns: list[str] | None = None) -> list[str]:
    """Gibt Liste von '<hash>  <dateiname>'-Zeilen zurueck (sortiert)."""
    if patterns is None:
        patterns = RELEASE_PATTERNS
    files = sorted(
        p for pattern in patterns for p in directory.glob(pattern) if p.is_file()
    )
    return [f"{compute_sha256(f)}  {f.name}" for f in files]


def write_sha256sums(directory: Path, patterns: list[str] | None = None) -> Path:
    """Schreibt SHA256SUMS in directory/ und gibt den Pfad zurueck."""
    lines = generate_sums(directory, patterns)
    out = directory / "SHA256SUMS"
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    dist_dir = Path(args[0]) if args else Path(__file__).parent.parent / "dist"
    if not dist_dir.is_dir():
        print(f"Fehler: {dist_dir} existiert nicht oder ist kein Verzeichnis.", file=sys.stderr)
        return 1
    out = write_sha256sums(dist_dir)
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    if not lines:
        print("Keine Release-Artifacts gefunden (*.exe, *.zip, *.tar.gz, *.whl).")
        return 0
    for line in lines:
        print(line)
    print(f"\nGeschrieben: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
