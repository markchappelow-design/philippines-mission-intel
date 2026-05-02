from datetime import datetime, timezone
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
GENERATOR = PROJECT_DIR / "generate_report.py"


def main() -> int:
    now = datetime.now(timezone.utc)

    # Execute only in a narrow 0001Z window
    if now.hour == 0 and 1 <= now.minute <= 5:
        return subprocess.call([sys.executable, str(GENERATOR)], cwd=str(PROJECT_DIR))

    print("Not in 0001Z execution window. Exiting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())