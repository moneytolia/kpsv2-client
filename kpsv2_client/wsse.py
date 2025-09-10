from datetime import datetime, timedelta, timezone
from lxml import etree
from .xmlutil import NS

WS_TRUST_13 = "http://docs.oasis-open.org/ws-sx/ws-trust/200512"

def _ts_now():
    return datetime.now(timezone.utc)

def build_timestamp(minutes=5):
    ts = etree.Element(etree.QName(NS["wsu"], "Timestamp"), nsmap=NS)
    created = etree.SubElement(ts, etree.QName(NS["wsu"], "Created"))
    expires = etree.SubElement(ts, etree.QName(NS["wsu"], "Expires"))
    now = _ts_now()
    created.text = now.isoformat()
    expires.text = (now + timedelta(minutes=minutes)).isoformat()
    return ts

def build_security_header_for_issued_token(internal_ref_id: str):
    """
    WS-Policy: <sp:RequireInternalReference/> gereği SecurityTokenReference -> Reference URI="#{wsu:Id}" kullanıyoruz.
    """
    sec = etree.Element(etree.QName(NS["wsse"], "Security"), nsmap=NS)
    sec.append(build_timestamp())
    str_el = etree.SubElement(sec, etree.QName(NS["wsse"], "SecurityTokenReference"))
    ref = etree.SubElement(str_el, etree.QName(NS["wsse"], "Reference"))
    ref.set("URI", f"#{internal_ref_id}")
    return sec

def build_rst_issue_envelope(applies_to: str, username: str, password: str, institution_code: str, sts_action_issue: str):
    """
    Minimal WS-Trust 1.3 RST (Issue) zarfı.
    KeyType = SymmetricKey (WSDL RequestSecurityTokenTemplate ile uyumlu)
    """
    env = etree.Element(etree.QName(NS["s"], "Envelope"), nsmap=NS)
    hdr = etree.SubElement(env, etree.QName(NS["s"], "Header"))
    # WS-Addressing
    wsa_action = etree.SubElement(hdr, etree.QName(NS["wsa"], "Action"))
    wsa_action.text = f"{WS_TRUST_13}/RST/Issue"
    wsa_to = etree.SubElement(hdr, etree.QName(NS["wsa"], "To"))
    wsa_to.text = sts_action_issue
    # Timestamp
    hdr.append(build_timestamp())

    # Body / RST
    body = etree.SubElement(env, etree.QName(NS["s"], "Body"))
    rst = etree.SubElement(body, etree.QName(WS_TRUST_13, "RequestSecurityToken"))

    keytype = etree.SubElement(rst, etree.QName(WS_TRUST_13, "KeyType"))
    keytype.text = f"{WS_TRUST_13}/SymmetricKey"

    applies = etree.SubElement(rst, etree.QName(WS_TRUST_13, "AppliesTo"))
    # MEX/Policy namespace farkları için basit EPR:
    epr = etree.SubElement(applies, "{http://schemas.xmlsoap.org/ws/2004/09/policy}EndpointReference")
    addr = etree.SubElement(epr, "{http://www.w3.org/2005/08/addressing}Address")
    addr.text = applies_to

    # Basit UsernameToken (kurum kodu genelde domain\username gibi prefixlenir)
    sec = etree.SubElement(hdr, etree.QName(NS["wsse"], "Security"))
    ut = etree.SubElement(sec, etree.QName(NS["wsse"], "UsernameToken"))
    u = etree.SubElement(ut, etree.QName(NS["wsse"], "Username"))
    p = etree.SubElement(ut, etree.QName(NS["wsse"], "Password"))
    u.text = f"{institution_code}\\{username}" if institution_code else username
    p.text = password

    return env

def parse_rstr_for_issued_token(xml_text: str):
    """
    RSTR içinden:
      - RequestedSecurityToken (wsu:Id/internal reference)
      - Lifetime/Expires
    döndürür.
    """
    root = etree.fromstring(xml_text.encode("utf-8"))
    rstn = root.xpath("//*[local-name()='RequestedSecurityToken']/*[@wsu:Id]", namespaces=NS)
    if not rstn:
        raise RuntimeError("Security token not found in RSTR.")
    token_el = rstn[0]
    internal_id = token_el.attrib.get(f"{{{NS['wsu']}}}Id")
    exp_el = root.xpath("//*[local-name()='Lifetime']/*[local-name()='Expires']", namespaces=NS)
    expires_at = exp_el[0].text if exp_el else None
    return {"internal_id": internal_id, "raw": etree.tostring(token_el, encoding="unicode")}, expires_at
