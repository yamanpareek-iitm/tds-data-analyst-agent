import asyncio, base64, io
from typing import Dict, Any, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def png_base64(fig, max_bytes=100_000, start_dpi=110):
    for dpi in [start_dpi, 100, 90, 80, 70, 60, 50]:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.1,
                    metadata={"Software": "matplotlib"})
        data = buf.getvalue()
        if len(data) <= max_bytes:
            plt.close(fig)
            return base64.b64encode(data).decode("ascii")
    plt.close(fig)
    return base64.b64encode(data).decode("ascii")

def assert_image_under_limit(b64_str: str, max_bytes: int):
    raw = base64.b64decode(b64_str, validate=True)
    if len(raw) > max_bytes:
        raise RuntimeError(f"Image exceeds {max_bytes} bytes")

async def run_code_steps(plan: List[Dict[str, Any]], context: Dict[str, Any], timeout_sec: int = 120) -> Any:
    env_globals = {
        "__builtins__": __builtins__,
        "context": context,
        "png_base64": png_base64,
        "assert_image_under_limit": assert_image_under_limit,
    }
    env_locals: Dict[str, Any] = {}
    RESULT = None

    async def _exec_all():
        nonlocal RESULT
        for step in plan:
            if step.get("type") != "python":
                continue
            code = step.get("code", "")
            exec(code, env_globals, env_locals)
        RESULT = env_locals.get("RESULT", None)

    await asyncio.wait_for(_exec_all(), timeout=timeout_sec)
    if RESULT is None:
        raise RuntimeError("No RESULT produced by plan")
    return RESULT
