from __future__ import annotations

import json
import sys
import time


def json_log(message: str, **kwargs):
    payload = {"message": message, **kwargs, "ts": int(time.time() * 1000)}
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


class Timer:
    def __init__(self, name: str):
        self.name = name
        self.t0 = time.time()

    def end(self) -> int:
        return int((time.time() - self.t0) * 1000)


