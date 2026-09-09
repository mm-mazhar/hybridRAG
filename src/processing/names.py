def clean_table_name(name: str) -> str:
    """Turn a filename or host into a LanceDB-safe table id."""
    cleaned = "".join(char if char.isalnum() else "_" for char in name)
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    return cleaned.lower()


def domain_label(host: str, common_tlds: list[str]) -> str:
    """Strip www and a known TLD so table names stay short."""
    domain = host[4:] if host.startswith("www.") else host
    for tld in sorted(common_tlds, key=len, reverse=True):
        if domain.endswith(tld):
            return domain[: -len(tld)]
    return domain
