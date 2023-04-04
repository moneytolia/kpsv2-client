
# KPSv2 Client

Bu proje, Türkiye Cumhuriyeti Kimlik Paylaşımı Sistemi'nin (KPS) v2 sürümüne erişmek için bir istemci sağlar. Bu istemci, KPS API'sine HTTP istekleri gönderir ve yanıtları alır.






## Gereksinimler

- [KPS V2 Test Hesabı](https://www.nvi.gov.tr/kps)
- Python 3
- [Venv](https://docs.python.org/3/library/venv.html) 
  
## Yükleme 
Bu projenin kopyasını yerel bilgisayarınıza indirin:

```python 
  git clone https://github.com/moneytolia/kpsv2-client.git
  virtualenv -p python3.6 venv
  pip install -r requirements.txt || pip3 install requests==2.28.1
  python3 test_kps_service.py
```
    
