import pytest
from starlette.testclient import TestClient


@pytest.mark.parametrize(
    ['url'],
    [
        ['/liveness'],
        ['/readiness']
    ]
)
async def test_common_url(client: TestClient, url: str):
    response = client.get(url)
    assert response.status_code == 200
