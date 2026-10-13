import os
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_PYTHON_DISABLED"] = "true"
os.environ["FASTAPI_TELEMETRY_DISABLE"] = "1"