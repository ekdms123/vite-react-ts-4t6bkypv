#!/usr/bin/env python3
"""Run the JIGAEWOL ZIP's per-turn chat hook for this project (user > ZIP > model).

The ZIP in jigaewol/ is verified and activated by its own START_CHAT.py the first time a
session needs it; every prompt and every answer then pass through tools/jigaewol_chat_hook.py.
An activation failure is reported to the model, never skipped silently.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[1])
event_text = sys.stdin.read()
event = json.loads(event_text or "{}")
name = str(event.get("hook_event_name") or "")


def report(message: str) -> None:
    if name == "UserPromptSubmit":
        print(json.dumps({"hookSpecificOutput": {"hookEventName": name, "additionalContext": message}}, ensure_ascii=False))
    elif name == "Stop" and not event.get("stop_hook_active"):
        print(json.dumps({"decision": "block", "reason": message}, ensure_ascii=False))


archives = sorted(project.glob("jigaewol/*.zip"))
if not archives:
    report("[JIGAEWOL] jigaewol/ 폴더에 ZIP이 없어요. 사용자에게 알리세요.")
    sys.exit(0)
archive = archives[-1]
digest = hashlib.sha256(archive.read_bytes()).hexdigest()[:12]
root = Path(tempfile.gettempdir()) / f"jigaewol_runtime_{digest}"
state = project / ".jigaewol_state"
hook = root / "tools" / "jigaewol_chat_hook.py"

if not hook.is_file():
    starter = Path(tempfile.gettempdir()) / f"jigaewol_start_{digest}.py"
    starter.write_bytes(zipfile.ZipFile(archive).read("START_CHAT.py"))
    started = subprocess.run([sys.executable, "-B", str(starter), "--zip", str(archive), "--root", str(root), "--state", str(state)],
                             capture_output=True, text=True)
    if started.returncode or not hook.is_file():
        report("[JIGAEWOL] ZIP 검증·활성화 실패: " + (started.stderr or started.stdout).strip()[-500:] + "\n검사가 돌지 않았다는 사실을 사용자에게 그대로 알리세요.")
        sys.exit(0)

done = subprocess.run([sys.executable, "-B", str(hook), "--state", str(state)], input=event_text, capture_output=True, text=True)
if done.returncode:
    report("[JIGAEWOL] 훅 실행 실패: " + done.stderr.strip()[-500:] + "\n사용자에게 그대로 알리세요.")
    sys.exit(0)
sys.stdout.write(done.stdout)
