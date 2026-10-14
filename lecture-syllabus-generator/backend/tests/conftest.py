import os
import tempfile
from pathlib import Path

import pytest

os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_PYTHON_DISABLED"] = "true"
os.environ["FASTAPI_TELEMETRY_DISABLE"] = "1"

# Set these BEFORE application imports, including test-module collection.
# Never use a developer's .env database, storage or live model credentials.
_test_directory = tempfile.TemporaryDirectory(prefix="lecture-syllabus-tests-")
TEST_ROOT = Path(_test_directory.name)
TEST_DATABASE = TEST_ROOT / "data" / "test.db"
TEST_DATABASE.parent.mkdir()
os.environ["APP_DATABASE_URL"] = "sqlite:///" + TEST_DATABASE.as_posix()
os.environ["APP_DATA_DIR"] = str(TEST_DATABASE.parent)
os.environ["APP_STORAGE_DIR"] = str(TEST_ROOT / "storage")
os.environ["APP_MODEL_PROVIDER"] = "mock"
os.environ["APP_MODEL_API_KEY"] = ""


@pytest.fixture(autouse=True)
def isolated_database():
    from app.db import Base, engine, init_db

    # This guard must run before any destructive test cleanup.
    assert Path(engine.url.database).resolve() == TEST_DATABASE.resolve()
    Base.metadata.drop_all(bind=engine)
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(isolated_database):
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def pytest_unconfigure(config):
    # Close SQLite handles before TemporaryDirectory removes test-owned files.
    import sys
    if "app.db" in sys.modules:
        sys.modules["app.db"].engine.dispose()
    _test_directory.cleanup()
