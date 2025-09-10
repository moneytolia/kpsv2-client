import datetime as dt
import requests
from .wsse import build_rst_issue_envelope, parse_rstr_for_issued_token
from .xmlutil import to_bytes

class StsClient:
    def __init__(self, cfg):
        self.cfg = cfg
        self._cache = None  # {"token": {...}, "expires_at": datetime}

    def request_security_token(self, applies_to: str):
        # Basit cache
        if self._cache and self._cache["expires_at"] > dt.datetime.utcnow():
            return self._cache

        env = build_rst_issue_envelope(
            applies_to=applies_to,
            username=self.cfg.username,
            password=self.cfg.password,
            institution_code=self.cfg.institution_code,
            sts_action_issue=self.cfg.sts_endpoint,
        )
        headers = {
            "Content-Type": 'application/soap+xml; charset="utf-8"; action="http://docs.oasis-open.org/ws-sx/ws-trust/200512/RST/Issue"'
        }
        resp = requests.post(
            self.cfg.sts_endpoint,
            data=to_bytes(env),
            headers=headers,
            timeout=self.cfg.request_timeout,
        )
        resp.raise_for_status()
        token_info, expires_iso = parse_rstr_for_issued_token(resp.text)

        # Expires parse
        expires_at = dt.datetime.max
        if expires_iso:
            try:
                expires_at = dt.datetime.fromisoformat(expires_iso.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                pass

        self._cache = {"token": token_info, "expires_at": expires_at}
        return self._cache
