from service import kps_service
from datetime import datetime


identity_number = "13090809606"
birth_date = "01.07.1891"


if __name__ == '__main__':
    birth_date = datetime.strptime(birth_date, '%d.%m.%Y')
    resp = kps_service.send_request(identity_number=identity_number, birth_date=birth_date)
