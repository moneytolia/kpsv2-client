from .endpoints import ACTIONS
from .sts_client import StsClient
from .soap_client import SoapClient

class KpsService:
    """
    Geriye uyumluluk için sınıf adı korunmuştur.
    yeni kullanım Config ile:
        from kpsv2_client.endpoints import Config
        cfg = Config(institution_code="KRM-XXXX", username="user", password="pass")
        kps = KpsService(cfg)
        xml = kps.kisi_adres_no_sorgula(10000000146)
    """

    def __init__(self, cfg=None):
        self.cfg = cfg
        self._username = None
        self._password = None
        if cfg:
            self.sts = StsClient(cfg)
            self.soap = SoapClient(cfg)
        else:
            self.sts = None
            self.soap = None

    # Eski örneklere geriye uyumluluk (kullanmayın)
    def set_auth(self, username: str, password: str):
        self._username = username
        self._password = password

    def kisi_adres_no_sorgula(self, kimlik_no: int, seri_no: str | None = None):
        if not self.cfg:
            raise RuntimeError("Config gereklidir. Lütfen Config ile KpsService örneği oluşturun.")
        token = self.sts.request_security_token(applies_to=self.cfg.routing_endpoint)
        body = {"Sorgula": {"kriter": {"KimlikNo": kimlik_no, "SeriNo": seri_no}}}
        xml = self.soap.call(action=ACTIONS.KISI_ADRES_NO_SORGULA, token=token, body=body)
        return xml  # İstersen burada parse edip models ile nesne döndürebiliriz.
