from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
import typing

ProductName = str
Slot_code = str
Assortment = typing.Dict[ProductName, 'Product']
Coins = Counter[Decimal, int]
Menu = typing.Dict[ProductName, typing.Tuple[Slot_code, Decimal]]


class MachineOverloadedException(Exception):
    pass


class ProductUnavailableException(Exception):
    pass


@dataclass
class Product:
    name: str
    quantity: int
    price: Decimal


class Machine:
    def __init__(self, slots: int, slot_depth: int) -> None:
        pass

    def load_products(self, assortment: Assortment) -> None:
        pass

    def load_coins(self, coins: Coins) -> None:
        pass

    def get_available_products(self) -> Menu:
        pass

    def choose_product(self, product_code: str, money: Coins) -> typing.Tuple[typing.Optional[Product], typing.Optional[Coins]]:
        pass

    def get_balance(self) -> Decimal:
        pass

    def cash_out(self) -> Coins:
        pass
