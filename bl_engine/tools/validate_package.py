from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from stateful_author.release import validate_package


def main() -> int:
    target = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT
    result = validate_package(target)
    print(f"errors: {len(result['errors'])}")
    for item in result['errors']:
        print(f"ERROR {item}")
    print(f"warnings: {len(result['warnings'])}")
    for item in result['warnings']:
        print(f"WARNING {item}")
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
