from datetime import datetime

import requests

from kpsv2_client.kps_helper import KpsException, _kps_helper
from kpsv2_client.config import settings


class KpsService:
    def __init__(self, action: str = None, kps_url: str = None, sts_url: str = None):
        self._username = None
        self._password = None
        self._action = action or settings["bilesik_kutuk_sorgula"]
        self._kps_url = kps_url or settings["kps_url"]
        self._sts_url = sts_url or settings["sts_url"]
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

    def _send_request(self, created, expires, msg_uuid, security, xml_schema, action=None):
        effective_action = action or self._security_context["action"]
        data = _kps_helper.kps_xml_schema.format(
            effective_action,
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
            xml_schema,
        )

        response = requests.post(self._security_context["kps_url"], data=data, headers=self._headers)
        response = _kps_helper.xml_to_json(response.content)
        return response

    def bilesik_kutuk_sorgula(self, birth_date: datetime, identity_number: str):
        self._check_auth()
        msg_uuid = _kps_helper.create_uuid()
        created, expires = _kps_helper.create_timestamp()

        date_format = "%d.%m.%Y"
        birth_date = datetime.strptime(birth_date, date_format) if isinstance(birth_date, str) else birth_date

        sts_response = _kps_helper.create_sts_request(self._security_context, self._headers, created, expires, msg_uuid)
        security = _kps_helper.create_security_data(sts_response, created, expires)

        schema = _kps_helper.bilesik_kutuk_sorgula(birth_date, identity_number)
        return self._send_request(created, expires, msg_uuid, security, schema)

    def kisi_adres_no_sorgula(self, kimlik_no: str = None, seri_no: str = None):
        """KisiAdresNoSorgulaServis/Sorgula — at least one of the params must be given."""
        if not kimlik_no and not seri_no:
            raise KpsException("kimlik_no veya seri_no parametrelerinden en az biri verilmelidir.")
        self._check_auth()

        msg_uuid = _kps_helper.create_uuid()
        created, expires = _kps_helper.create_timestamp()

        sts_response = _kps_helper.create_sts_request(self._security_context, self._headers, created, expires, msg_uuid)
        security = _kps_helper.create_security_data(sts_response, created, expires)

        schema = _kps_helper.kisi_adres_no_sorgula(kimlik_no=kimlik_no, seri_no=seri_no)
        return self._send_request(created, expires, msg_uuid, security, schema, action=settings["kisi_adres_no_sorgula"])
