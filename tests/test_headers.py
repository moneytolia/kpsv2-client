from kpsv2_client.endpoints import ACTIONS
from kpsv2_client.kps_service import KpsService

def test_action_constant():
    assert ACTIONS.KISI_ADRES_NO_SORGULA.endswith("/KisiAdresNoSorgulaServis/Sorgula")

def test_service_init_without_config():
    svc = KpsService()
    try:
        svc.kisi_adres_no_sorgula(10000000146)
        assert False, "Config olmadan hata beklenirdi"
    except RuntimeError:
        assert True
