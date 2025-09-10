import os

class ACTIONS:
    KISI_ADRES_NO_SORGULA = "http://kps.nvi.gov.tr/2011/01/01/KisiAdresNoSorgulaServis/Sorgula"

class Config:
    def __init__(
        self,
        institution_code: str,
        username: str,
        password: str,
        sts_endpoint: str | None = None,
        routing_endpoint: str | None = None,
        request_timeout: int = 30,
    ):
        self.institution_code = institution_code
        self.username = username
        self.password = password
        self.sts_endpoint = sts_endpoint or os.getenv(
            "KPS_STS_ENDPOINT",
            "https://kimlikdogrulama.nvi.gov.tr/Services/Issuer.svc/IWSTrust13"
        )
        self.routing_endpoint = routing_endpoint or os.getenv(
            "KPS_ROUTING_ENDPOINT",
            "https://kpsv2.nvi.gov.tr/Services/RoutingService.svc"
        )
        self.request_timeout = int(os.getenv("KPS_TIMEOUT", request_timeout))
