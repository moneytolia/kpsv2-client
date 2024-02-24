import requests

from kpsv2_client.kps_helper import KpsException, _kps_helper
from datetime import datetime

class KpsService:
    def __init__(self, action: str = None, kps_url: str = None, sts_url: str = None):
        self._username = None
        self._password = None
        self._action = (
            action
            or "http://kps.nvi.gov.tr/2023/02/01/BilesikKutukSorgulaKimlikNoServis/Sorgula"
        )
        self._kps_url = (
            kps_url or "https://kpsv2test.nvi.gov.tr/Services/RoutingService.svc"
        )
        self._sts_url = (
            sts_url
            or "https://kimlikdogrulama.nvi.gov.tr/Services/Issuer.svc/IWSTrust13"
        )
        self._headers = {"Content-Type": "application/soap+xml; charset=utf-8"}

    @property
    def _security_context(self):
        return {
            "action": self._action,
            "kps_url": self._kps_url,
            "sts_url": self._sts_url,
            "password": self._password,
            "username": self._username,
        }

    def set_auth(self, username: str, password: str):
        self._username = username
        self._password = password

    def _check_auth(self):
        if not self._username or not self._password:
            raise KpsException("username and password must be set")

    def _send_request(
        self,
        created,
        expires,
        msg_uuid,
        security,
        birth_date,
        identity_number,
    ):
        data = _kps_helper.kps_xml_schema.format(
            self._security_context["action"],
            msg_uuid,
            self._security_context["kps_url"],
            created,
            expires,
            security["issuer_name"],
            security["serial_number"],
            security["cipher_datas"][0].text,
            security["cipher_datas"][1].text,
            security["digest_value"],
            security["signature"],
            security["key_identifier_path"],
            birth_date.month,
            birth_date.day,
            birth_date.year,
            identity_number,
        )

        response = requests.post(
            self._security_context["kps_url"], data=data, headers=self._headers
        )
        response = _kps_helper.xml_to_json(response.content)

        return response

    def bilesik_kutuk_sorgula(self, birth_date: str, identity_number: str):
        self._check_auth()

        msg_uuid = _kps_helper.create_uuid()
        created, expires = _kps_helper.create_timestamp()

        date_format = '%d.%m.%Y'
        birth_date = datetime.strptime(birth_date, date_format) if isinstance(birth_date, str) else birth_date

        sts_response = _kps_helper.create_sts_request(
            self._security_context, self._headers, created, expires, msg_uuid
        )
        security = _kps_helper.create_security_data(sts_response, created, expires)

        return self._send_request(
            created,
            expires,
            msg_uuid,
            security,
            birth_date,
            identity_number,
        )
