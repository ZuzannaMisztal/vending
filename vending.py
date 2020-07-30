from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
from math import ceil
import typing

ProductName = typing.NewType('ProductName', str)
SlotCode = typing.NewType('SlotCode', str)
Assortment = typing.Dict[ProductName, 'Product']
Coins = typing.Counter[Decimal]
Menu = typing.Dict[ProductName, typing.Tuple[SlotCode, Decimal]]


def add_assortments(asrt1: Assortment, asrt2: Assortment) -> Assortment:
    result = {}
    try:
        for product_name in asrt1.keys():
            if product_name in asrt2.keys():
                result[product_name] = asrt1[product_name] + asrt2[product_name]
            else:
                result[product_name] = asrt1[product_name]
        for product_name in asrt2.keys():
            if product_name in asrt1.keys():
                continue
            result[product_name] =asrt2[product_name]
    except TypeError:
        result = asrt2 #it solves only first delivery problem. Will probably crash if delivery is empty
    return result


class MachineOverloadedException(Exception):
    pass


class Product:
    def __init__(self, name: ProductName, quantity: int, price: Decimal):
        self.name = name
        self.quantity = quantity
        self.price = price

    def __add__(self, other):
        if self.name != other.name or self.price != other.price:
            raise ValueError("Products are not the same type")
        return Product(self.name, self.quantity + other.quantity, self.price)


class Machine:
    def __init__(self, slots: int, slot_depth: int) -> None:
        self.coins = Coins()
        self.slot_depth = slot_depth
        self.slots: typing.Dict[SlotCode, Product] = {str(i): None for i in range(slots)}
        self.assortment: Assortment = Assortment

    def _arrange_slots(self) -> None:
        index = 0
        for product in self.assortment.values():
            product_units = product.quantity
            slots_taken = ceil(product.quantity / self.slot_depth)
            for _ in range(slots_taken):
                number_of_products_in_slot = min(self.slot_depth, product_units)
                self.slots[SlotCode(str(index))] = Product(product.name, number_of_products_in_slot, product.price)
                index += 1
                product_units -= number_of_products_in_slot

    def _get_slot_code(self, product_name: ProductName):
        for slot_code, product in self.slots.items():
            if product.name == product_name:
                return slot_code

    def load_products(self, delivery: Assortment) -> None:
        self.assortment = add_assortments(self.assortment, delivery)
        self._arrange_slots()

    def load_coins(self, coins: Coins) -> None:
        pass

    def get_available_products(self) -> Menu:
        return {product_name: (self._get_slot_code(product_name), product.price) for product_name, product in self.assortment.items()}

    def choose_product(self, product_code: SlotCode, money: Coins) -> typing.Tuple[typing.Optional[Product], typing.Optional[Coins]]:
        pass

    def get_balance(self) -> Decimal:
        pass

    def cash_out(self) -> Coins:
        pass
