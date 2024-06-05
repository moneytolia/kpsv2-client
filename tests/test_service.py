from datetime import datetime

import pytest

from kpsv2_client.service import KpsException, KpsService


def test_set_auth():
    kps_service = KpsService()
    kps_service.set_auth("username", "password")

    kps_service._check_auth()
    assert kps_service._username == "username"
    assert kps_service._password == "password"


def test_no_auth():
    kps_service = KpsService()

    try:
        kps_service._check_auth()
    except KpsException as e:
        assert str(e) == "username and password must be set"


@pytest.mark.parametrize(
    "sts_response,kps_response,birth_date,assert_empty",
    [
        (True, True, datetime.now(), False),
        (True, True, datetime.now(), False),
        (True, False, datetime.now(), True),
    ],
    indirect=["sts_response", "kps_response"],
)
def test_bilesik_kutuk_sorgula(sts_response, kps_response, birth_date, assert_empty):
    kps_service = KpsService()
    kps_service.set_auth("username", "password")

    result = kps_service.bilesik_kutuk_sorgula(birth_date, "11111111110")

    assert (
        bool(
            result.get("BilesikKutukBilgileri", {})
            .get("TCVatandasiKisiKutukleri", {})
            .get("KisiBilgisi", {})
            .get("TemelBilgisi", {})
            .get("Ad")
        )
        != assert_empty
    ), result
