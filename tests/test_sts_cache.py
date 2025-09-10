import types
from kpsv2_client.sts_client import StsClient
import datetime as dt

def test_cache_logic():
    class Cfg(types.SimpleNamespace): pass
    cfg = Cfg(username="u", password="p", institution_code="KRM-X",
              sts_endpoint="https://example/issuer", request_timeout=5)
    st = StsClient(cfg)
    st._cache = {"token": {"internal_id": "id1", "raw": "<t/>"},
                 "expires_at": dt.datetime.utcnow() + dt.timedelta(days=1)}
    t = st.request_security_token("https://applies")
    assert t["token"]["internal_id"] == "id1"
