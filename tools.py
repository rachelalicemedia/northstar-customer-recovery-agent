from pathlib import Path


POLICY_FILE = Path(__file__).parent / "data" / "policies.md"


def get_policy() -> str:
    """Retrieve Northstar Supply Co. customer service policies."""

    return POLICY_FILE.read_text(encoding="utf-8")