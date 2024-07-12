from pydantic import BaseModel
from typing import Optional


# http request classes
class CoinmarketCap_Access(BaseModel):
    coinmarketcap_key: str


class Covalent_Access(BaseModel):
    chainid: str
    eth_address: str
    covalent_key: str


class Loan_Item(BaseModel):
    loan_request: int


class Covalent_Item(
        Covalent_Access, CoinmarketCap_Access, Loan_Item):
    pass


class KYC_Item(BaseModel):
    chosen_validator: str
    coinmarketcap_key: str

    eth_address: Optional[str]
    covalent_key: Optional[str]
