
# KPSv2 Client

Bu proje, Türkiye Cumhuriyeti Kimlik Paylaşımı Sistemi'nin (KPS) v2 sürümüne erişmek için bir istemci sağlar. Bu istemci, KPS API'sine HTTP istekleri gönderir ve yanıtları alır.


## Gereksinimler

- [KPS V2 Test Hesabı](https://www.nvi.gov.tr/kps)
- Python 3
- [Venv](https://docs.python.org/3/library/venv.html)


## Örnek Kullanım

```python
from kpsv2_client import KpsService

kps_service = KpsService()
kps_service.set_auth("username", "password")
resp = kps_service.bilesik_kutuk_sorgula(identity_number="01234567890", birth_date="01.07.1891")
```

## Katkıda Bulunma
Lütfen katkıda bulunmak için pull request açın. Her türlü katkıya açığız.


## Lisans
Bu proje MIT lisansı altında lisanslanmıştır. Daha fazla bilgi için LICENSE dosyasına bakın.


## İletişim
Eğer bir sorunuz veya geri bildiriminiz varsa, lütfen [issues](https://github.com/moneytolia/kpsv2-client/issues) sayfasında bir konu açın.
