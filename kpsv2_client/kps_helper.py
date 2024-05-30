import base64
import datetime
import hashlib
import hmac
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom

import requests

_sts_data = """
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing" xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
  <s:Header>
    <a:Action s:mustUnderstand="1">http://docs.oasis-open.org/ws-sx/ws-trust/200512/RST/Issue</a:Action>
    <a:MessageID>urn:uuid:{}</a:MessageID>
    <a:ReplyTo>
      <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
    </a:ReplyTo>
    <a:To s:mustUnderstand="1">{}</a:To>
    <o:Security s:mustUnderstand="1" xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
      <u:Timestamp u:Id="_1">
        <u:Created>{}</u:Created>
        <u:Expires>{}</u:Expires>
      </u:Timestamp>
      <o:UsernameToken u:Id="_2">
        <o:Username>{}</o:Username>
        <o:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{}</o:Password>
      </o:UsernameToken>
    </o:Security>
  </s:Header>
  <s:Body>
    <trust:RequestSecurityToken xmlns:trust="http://docs.oasis-open.org/ws-sx/ws-trust/200512">
      <wsp:AppliesTo xmlns:wsp="http://schemas.xmlsoap.org/ws/2004/09/policy">
        <a:EndpointReference>
          <a:Address>{}</a:Address>
        </a:EndpointReference>
      </wsp:AppliesTo>
      <trust:RequestType>http://docs.oasis-open.org/ws-sx/ws-trust/200512/Issue</trust:RequestType>
    </trust:RequestSecurityToken>
  </s:Body>
</s:Envelope>
"""

_kps_data = """<?xml version="1.0"?><s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing" xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"><s:Header><a:Action s:mustUnderstand="1">{}</a:Action><a:MessageID>urn:uuid:{}</a:MessageID><a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo><a:To s:mustUnderstand="1">{}</a:To><o:Security xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" s:mustUnderstand="1"><u:Timestamp u:Id="_0"><u:Created>{}</u:Created><u:Expires>{}</u:Expires></u:Timestamp><xenc:EncryptedData xmlns:xenc="http://www.w3.org/2001/04/xmlenc#" Type="http://www.w3.org/2001/04/xmlenc#Element"><xenc:EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#aes256-cbc"/><KeyInfo xmlns="http://www.w3.org/2000/09/xmldsig#"><e:EncryptedKey xmlns:e="http://www.w3.org/2001/04/xmlenc#"><e:EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p"><DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/></e:EncryptionMethod><KeyInfo><o:SecurityTokenReference><X509Data><X509IssuerSerial><X509IssuerName>{}</X509IssuerName><X509SerialNumber>{}</X509SerialNumber></X509IssuerSerial></X509Data></o:SecurityTokenReference></KeyInfo><e:CipherData><e:CipherValue>{}</e:CipherValue></e:CipherData></e:EncryptedKey></KeyInfo><xenc:CipherData><xenc:CipherValue>{}</xenc:CipherValue></xenc:CipherData></xenc:EncryptedData><Signature xmlns="http://www.w3.org/2000/09/xmldsig#"><SignedInfo><CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/><SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#hmac-sha1"/><Reference URI="#_0"><Transforms><Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/></Transforms><DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/><DigestValue>{}</DigestValue></Reference></SignedInfo><SignatureValue>{}</SignatureValue><KeyInfo><o:SecurityTokenReference xmlns:k="http://docs.oasis-open.org/wss/oasis-wss-wssecurity-secext-1.1.xsd" k:TokenType="http://docs.oasis-open.org/wss/oasis-wss-saml-token-profile-1.1#SAMLV1.1"><o:KeyIdentifier ValueType="http://docs.oasis-open.org/wss/oasis-wss-saml-token-profile-1.0#SAMLAssertionID">{}</o:KeyIdentifier></o:SecurityTokenReference></KeyInfo></Signature></o:Security></s:Header>{}</s:Envelope>"""
bilesik_kutuk_sorgula_schema = """<env:Body xmlns:env="http://www.w3.org/2003/05/soap-envelope" xmlns:ns1="http://kps.nvi.gov.tr/2024/04/01"><ns1:Sorgula><ns1:kriterListesi><ns1:BilesikKutukSorgulaKimlikNoSorguKriteri><ns1:DogumAy>{}</ns1:DogumAy><ns1:DogumGun>{}</ns1:DogumGun><ns1:DogumYil>{}</ns1:DogumYil><ns1:KimlikNo>{}</ns1:KimlikNo></ns1:BilesikKutukSorgulaKimlikNoSorguKriteri></ns1:kriterListesi></ns1:Sorgula></env:Body>"""


class _KpsHelper:
    def __init__(self):
        self.sts_xml_schema = _sts_data
        self.kps_xml_schema = _kps_data
        self.bilesik_kutuk_sorgula_xml_schema = bilesik_kutuk_sorgula_schema

    def xml_to_json(self, response_xml=None, response_element=None):
        response_dict = {}
        if response_xml:
            root = minidom.parseString(response_xml).getElementsByTagName(
                "SorguSonucu"
            )[0]
        else:
            root = response_element

        for e in root.childNodes:
            if e.hasChildNodes():
                response_dict[e.nodeName] = self.xml_to_json(response_element=e)
            elif e.nodeType == e.TEXT_NODE:
                return e.data

        return response_dict

    def get_issuer_name(self, xml_doc):
        namespace = {"sig": "http://www.w3.org/2000/09/xmldsig#"}
        return xml_doc.find(".//sig:X509IssuerName", namespaces=namespace).text

    def get_serial_number(self, root):
        namespace = {"sig": "http://www.w3.org/2000/09/xmldsig#"}
        return root.find(".//sig:X509SerialNumber", namespaces=namespace).text

    def get_cipher_values(self, root):
        namespace = {"enc": "http://www.w3.org/2001/04/xmlenc#"}
        return root.findall(".//enc:CipherValue", namespaces=namespace)

    def get_binary_secret(self, root):
        namespace = {"trust": "http://docs.oasis-open.org/ws-sx/ws-trust/200512"}
        return base64.b64decode(
            root.find(".//trust:BinarySecret", namespaces=namespace).text
        )

    def get_key_identifier_path(self, root):
        namespace = {
            "secext": "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
        }
        return root.find(".//secext:KeyIdentifier", namespaces=namespace).text

    def get_digest_value(self, created, expires):
        timestamp = f'<u:Timestamp xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" u:Id="_0"><u:Created>{created}</u:Created><u:Expires>{expires}</u:Expires></u:Timestamp>'
        return base64.b64encode(
            hashlib.sha1(timestamp.encode("utf-8")).digest()
        ).decode("utf-8")

    def get_signature(self, binary_secret, digest_value):
        c14n = f'<SignedInfo xmlns="http://www.w3.org/2000/09/xmldsig#"><CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></CanonicalizationMethod><SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#hmac-sha1"></SignatureMethod><Reference URI="#_0"><Transforms><Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></Transform></Transforms><DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></DigestMethod><DigestValue>{digest_value}</DigestValue></Reference></SignedInfo>'
        return base64.b64encode(
            hmac.new(binary_secret, c14n.encode("utf-8"), hashlib.sha1).digest()
        ).decode("utf-8")

    def create_timestamp(self):
        created = (datetime.datetime.utcnow() + datetime.timedelta()).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        expires = (datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        return created, expires

    def create_uuid(self):
        return uuid.uuid4()

    def create_sts_request(self, security_context, headers, created, expires, msg_uuid):
        try:
            data = self.sts_xml_schema.format(
                msg_uuid,
                security_context["sts_url"],
                created,
                expires,
                security_context["username"],
                security_context["password"],
                security_context["kps_url"],
            )
            response = requests.post(
                security_context["sts_url"], data=data, headers=headers
            )
            resp = response.content.decode("utf-8")
        except Exception as e:
            raise KpsException(e)

        return resp

    def create_security_data(self, sts_token, created, expires):
        xml_doc = ET.fromstring(sts_token)
        binary_secret = self.get_binary_secret(xml_doc)
        digest_value = self.get_digest_value(created, expires)

        return {
            "issuer_name": self.get_issuer_name(xml_doc),
            "serial_number": self.get_serial_number(xml_doc),
            "cipher_datas": self.get_cipher_values(xml_doc),
            "digest_value": digest_value,
            "signature": self.get_signature(binary_secret, digest_value),
            "key_identifier_path": self.get_key_identifier_path(xml_doc),
        }

    def bilesik_kutuk_sorgula(self, birth_date, identity_number: str):
        return self.bilesik_kutuk_sorgula_xml_schema.format(
            birth_date.month,
            birth_date.day,
            birth_date.year,
            identity_number,
        )

class KpsException(Exception):
    pass


_kps_helper = _KpsHelper()
