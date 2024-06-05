import pytest

from kpsv2_client.config import settings
from tests.mocks import kps_error, kps_success, sts_mock


@pytest.fixture(scope="function")
def sts_response(requests_mock, request):
    requests_mock.post(settings.get("sts_url"), content=sts_mock())


@pytest.fixture(scope="function")
def kps_response(requests_mock, request):
    if request.param:
        requests_mock.post(settings.get("kps_url"), content=kps_success())
    else:
        requests_mock.post(settings.get("kps_url"), content=kps_error())
