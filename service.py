import requests

from kps_helper import kps_helper

class KpsService:
    def __init__(self):
        self.security_context = {
            "action": "http://kps.nvi.gov.tr/2023/02/01/BilesikKutukSorgulaKimlikNoServis/Sorgula",
            "kps_url": "https://kpsv2test.nvi.gov.tr/Services/RoutingService.svc",
            "sts_url": "https://kimlikdogrulama.nvi.gov.tr/Services/Issuer.svc/IWSTrust13",
            "password": "******",
            "username": "******"
        }
        self.headers = {"Content-Type": "application/soap+xml; charset=utf-8"}

    def get_bilesik_kutuk_sorgula(
        self,
        created,
        expires,
        msg_uuid,
        security,
        birth_date,
        identity_number,
    ):
        data = kps_helper.kps_xml_schema.format(
            self.security_context["action"],
            msg_uuid,
            self.security_context["kps_url"],
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

        response = requests.post(self.security_context["kps_url"], data=data, headers=self.headers)
        response = kps_helper.xml_to_json(response.content)

        return response

    def send_request(self, birth_date, identity_number):
        msg_uuid = kps_helper.create_uuid()
        created, expires = kps_helper.create_timestamp()

        token = kps_helper.create_sts_request(self.security_context, self.headers, created, expires, msg_uuid)
        security = kps_helper.create_security_data(token, created, expires)

        return self.get_bilesik_kutuk_sorgula(
            created,
            expires,
            msg_uuid,
            security,
            birth_date,
            identity_number,
        )


kps_service = KpsService()
