import requests
from lxml import etree
from .xmlutil import envelope_with_headers, to_bytes, NS
from .wsse import build_security_header_for_issued_token

class SoapClient:
    def __init__(self, cfg):
        self.cfg = cfg

    def call(self, action: str, token: dict, body: dict):
        # WS-Security (IssuedToken internal reference)
        sec = build_security_header_for_issued_token(token["token"]["internal_id"])

        # Envelope + WS-Addressing headers
        env = envelope_with_headers(action=action, to=self.cfg.routing_endpoint, security_header=sec)

        # Literal body
        body_el = env.find(f".//{{{NS['s']}}}Body")
        tns = "http://kps.nvi.gov.tr/2011/01/01"
        sorgula = etree.SubElement(body_el, f"{{{tns}}}Sorgula")
        kriter = etree.SubElement(sorgula, f"{{{tns}}}kriter")

        for k, v in (body.get("Sorgula") or {}).get("kriter", {}).items():
            if v is None:
                continue
            el = etree.SubElement(kriter, f"{{{tns}}}{k}")
            el.text = str(v)

        headers = {
            "Content-Type": f'application/soap+xml; charset="utf-8"; action="{action}"'
        }
        resp = requests.post(
            self.cfg.routing_endpoint,
            data=to_bytes(env),
            headers=headers,
            timeout=self.cfg.request_timeout
        )
        resp.raise_for_status()
        return resp.text
