import uuid
from lxml import etree

NS = {
    "s": "http://www.w3.org/2003/05/soap-envelope",
    "wsa": "http://www.w3.org/2005/08/addressing",
    "wsse": "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd",
    "wsu": "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd",
}

def new_message_id() -> str:
    return f"urn:uuid:{uuid.uuid4()}"

def to_bytes(elem) -> bytes:
    return etree.tostring(elem, xml_declaration=True, encoding="utf-8")

def envelope_with_headers(action: str, to: str, security_header) -> etree._Element:
    env = etree.Element(etree.QName(NS["s"], "Envelope"), nsmap=NS)
    header = etree.SubElement(env, etree.QName(NS["s"], "Header"))

    wsa_action = etree.SubElement(header, etree.QName(NS["wsa"], "Action"))
    wsa_action.text = action
    wsa_to = etree.SubElement(header, etree.QName(NS["wsa"], "To"))
    wsa_to.text = to
    wsa_mid = etree.SubElement(header, etree.QName(NS["wsa"], "MessageID"))
    wsa_mid.text = new_message_id()

    header.append(security_header)
    etree.SubElement(env, etree.QName(NS["s"], "Body"))
    return env
