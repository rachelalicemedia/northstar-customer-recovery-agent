import json
from datetime import datetime
from pathlib import Path


LOG_FILE = Path(__file__).parent / "logs" / "agent_runs.json"


def log_event(
    event_type: str,
    details: dict
) -> None:
    """Record an event in the agent audit log."""

    logs = json.loads(
        LOG_FILE.read_text(encoding="utf-8")
    )

    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "details": details
    }

    logs.append(event)

    LOG_FILE.write_text(
        json.dumps(logs, indent=4),
        encoding="utf-8"
    )