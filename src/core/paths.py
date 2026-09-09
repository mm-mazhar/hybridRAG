from pathlib import Path


def project_root() -> Path:
    """Return the repository root (parent of `src/`)."""
    return Path(__file__).resolve().parents[2]


def resolve_under_root(path: str | Path) -> Path:
    """Resolve a path relative to the project root when it is not absolute."""
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return project_root() / candidate
