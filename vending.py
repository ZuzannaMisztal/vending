from collections import Counter
from decimal import Decimal
from math import ceil
import typing

ProductName = typing.NewType('ProductName', str)
SlotCode = typing.NewType('SlotCode', str)
Assortment = typing.Dict[ProductName, 'Product']
Coins = typing.Counter[Decimal]
Menu = typing.Dict[ProductName, typing.Tuple[SlotCode, Decimal]]


def sum_of_coins(coins: Coins) -> Decimal:
    return sum([nominal * quantity for nominal, quantity in coins.items()])


def add_assortments(assortment1: typing.Optional[Assortment], assortment2: Assortment) -> Assortment:
    if assortment1 is None:
        return assortment2
    result = {}
    for product_name in assortment1.keys():
        if product_name in assortment2.keys():
            result[product_name] = assortment1[product_name] + assortment2[product_name]
        else:
            result[product_name] = assortment1[product_name]
    for product_name in assortment2.keys():
        if product_name in assortment1.keys():
            continue
        result[product_name] = assortment2[product_name]
    return result


def collect_change(coins_available: Coins, value_to_collect: Decimal, change: Coins) -> typing.Optional[Coins]:
    if value_to_collect == 0:
        return change
    if value_to_collect < 0:
        return None
    for coin in coins_available:
        new_coins_available = coins_available.copy()
        new_coins_available[coin] -= 1
        new_coins_available += Counter()
        new_change = change.copy()
        new_change.update({coin: 1})
        new_value_to_collect = value_to_collect - coin
        ret = collect_change(new_coins_available, new_value_to_collect, new_change)
        if ret:
            return ret
    return None


class MachineOverloadedException(Exception):
    pass


class NotEnoughMoneyInMachineException(Exception):
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
        self.coins: Coins = Coins()
        self.slot_depth = slot_depth
        self.number_of_slots = slots
        self.slots: typing.Dict[SlotCode, Product] = {str(i): None for i in range(slots)}
        self.assortment = None

    def _arrange_slots(self) -> None:
        index = 0
        for product in self.assortment.values():
            product_units = product.quantity
            slots_taken = ceil(product.quantity / self.slot_depth)
            for _ in range(slots_taken):
                number_of_products_in_slot = min(self.slot_depth, product_units)
                self.slots[SlotCode(str(index))] = Product(product.name, number_of_products_in_slot, product.price)
                product_units -= number_of_products_in_slot
                index += 1
                if index > self.number_of_slots:
                    raise MachineOverloadedException

    def _get_slot_code(self, product_name: ProductName):
        for slot_code, product in self.slots.items():
            if product.name == product_name:
                return slot_code

    def load_products(self, delivery: Assortment) -> None:
        self.assortment = add_assortments(self.assortment, delivery)
        self._arrange_slots()

    def load_coins(self, coins: Coins) -> None:
        self.coins.update(coins)

    def get_available_products(self) -> Menu:
        items = {product_name: (self._get_slot_code(product_name), product.price) for product_name, product in self.assortment.items()}
        return items

    def choose_product(self, product_code: SlotCode, money: Coins) -> typing.Tuple[typing.Optional[Product], typing.Optional[Coins]]:
        if product_code not in self.slots:
            return None, money
        product = self.slots[product_code]
        if product is None or product.quantity == 0 or sum_of_coins(money) < product.price:
            return None, money
        self.load_coins(money)
        try:
            change: Coins = self._get_change(money, product.price)
            self._give_coins(change)
            product.quantity -= 1
            self.assortment[product.name].quantity -= 1
            return Product(product.name, 1, product.price), change
        except NotEnoughMoneyInMachineException:
            self._give_coins(money)
            return None, money

    def get_balance(self) -> Decimal:
        return sum_of_coins(self.coins)

    def cash_out(self) -> Coins:
        pass

    def _get_change(self, money: Coins, price: Decimal) -> typing.Optional[Coins]:
        if sum_of_coins(money) == price:
            return None
        change = collect_change(self.coins, sum_of_coins(money) - price, Counter())
        if not change:
            raise NotEnoughMoneyInMachineException
        return change

    def _give_coins(self, change: Coins) -> None:
        if change is None:
            return None
        for nominal, quantity in change.items():
            if self.coins[nominal] < quantity:
                raise NotEnoughMoneyInMachineException
            self.coins[nominal] -= quantity
