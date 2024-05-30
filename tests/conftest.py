import pytest
from starlette.testclient import TestClient

from rsserpent_rev import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Share one test client across the whole module with `pytest.fixture`."""
    return TestClient(app)
