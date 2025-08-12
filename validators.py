import base64
from typing import Any, Dict

class ValidationError(Exception):
    pass

def validate_final_output_schema(result: Any, output_spec: Dict[str, Any]):
    # Enforce array vs object
    if output_spec.get("type") == "json_array":
        if not isinstance(result, list):
            raise ValidationError("Expected JSON array output.")
        # Prefer primitive types in array (esp. for evaluators expecting strings)
        if not all(isinstance(x, (str, int, float, bool)) for x in result):
            raise ValidationError("JSON array items must be primitive types (prefer strings).")
    else:
        if not isinstance(result, dict):
            raise ValidationError("Expected JSON object output.")

    # Enforce keys if specified
    keys = output_spec.get("keys")
    if keys and isinstance(result, dict):
        missing = [k for k in keys if k not in result]
        if missing:
            raise ValidationError(f"Missing keys: {missing}")

    # Validate PNG sizes for likely base64 fields (look for PNG magic iVBOR)
    max_bytes = output_spec.get("image_constraints", {}).get("max_png_bytes", 100_000)

    def check_b64_png(val: str):
        try:
            raw = base64.b64decode(val, validate=True)
        except Exception:
            return
        if len(raw) > max_bytes:
            raise ValidationError(f"PNG exceeds {max_bytes} bytes")

    if isinstance(result, dict):
        for v in result.values():
            if isinstance(v, str) and len(v) > 100 and "iVBOR" in v[:20]:
                check_b64_png(v)
    elif isinstance(result, list):
        for v in result:
            if isinstance(v, str) and len(v) > 100 and "iVBOR" in v[:20]:
                check_b64_png(v)
