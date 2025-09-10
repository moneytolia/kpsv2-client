from dataclasses import dataclass
from typing import Optional

# KisiAdresNoSorgulaServis tipleri (WSDL'e göre sadeleştirilmiş DTO)

@dataclass
class KisiAdresNoSorguKriteri:
    KimlikNo: int
    SeriNo: Optional[str] = None

@dataclass
class Parametre:
    Aciklama: Optional[str]
    Kod: Optional[int]

@dataclass
class KisiAdresNoSorgula:
    AdresNo: Optional[int]
    HataBilgisi: Optional[Parametre]

@dataclass
class KisiAdresNoSorgulaSonucu:
    HataBilgisi: Optional[Parametre]
    SorguSonucu: Optional[KisiAdresNoSorgula]
