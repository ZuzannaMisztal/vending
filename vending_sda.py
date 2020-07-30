from decimal import Decimal
import unittest
import typing
from vending import Machine, Product, Coins, MachineOverloadedException, ProductUnavailableException


class TestVendingMachine(unittest.TestCase):
    def test_loading_products(self):
        machine = Machine(slots=3, slot_depth=10)
        products = {
            "coca-cola": Product(name="coca-cola", quantity=7, price=Decimal(2.1)),
            "mars": Product(name="mars", quantity=5, price=Decimal(1.9)),
            "orbit": Product(name="orbit", quantity=6, price=Decimal(2.3)),
        }
        machine.load_products(products)
        available_products = machine.get_available_products().keys()
        self.assertIn("coca-cola", available_products)
        self.assertIn("mars", available_products)
        self.assertIn("orbit", available_products)
        self.assertNotIn("lays", available_products)

    def test_too_many_product_kinds(self):
        machine = Machine(slots=2, slot_depth=10)
        products = {
            "coca-cola": Product(name="coca-cola", quantity=7, price=Decimal(2.1)),
            "mars": Product(name="mars", quantity=5, price=Decimal(1.9)),
            "orbit": Product(name="orbit", quantity=6, price=Decimal(2.3)),
        }
        with self.assertRaises(MachineOverloadedException):
            machine.load_products(products)

    def test_product_amount_exceeds_slot_depth(self):
        machine = Machine(slots=1, slot_depth=1)
        products = {
            "coca-cola": Product(name="coca-cola", quantity=7, price=Decimal(2.1)),
        }
        with self.assertRaises(MachineOverloadedException):
            machine.load_products(products)

    def test_two_products_cant_share_one_slot(self):
        machine = Machine(slots=3, slot_depth=10)
        products = {
            "coca-cola": Product(name="coca-cola", quantity=15, price=Decimal(2.1)),
            "mars": Product(name="mars", quantity=15, price=Decimal(1.9)),
        }
        with self.assertRaises(MachineOverloadedException):
            machine.load_products(products)

    def test_one_products_can_take_many_slots(self):
        machine = Machine(slots=2, slot_depth=10)
        products = {
            "coca-cola": Product(name="coca-cola", quantity=20, price=Decimal(2.1)),
        }
        machine.load_products(products)
        available_products = machine.get_available_products().keys()
        self.assertIn("coca-cola", available_products)
        self.assertNotIn("mars", available_products)

    def test_loading_coins(self):
        machine = Machine(slots=2, slot_depth=10)
        money = Coins({Decimal(0.2): 5, Decimal(1): 1})
        machine.load_coins(money)
        self.assertEqual(machine.get_balance(), Decimal(2))

    def test_can_buy_available_product_with_exact_change(self):
        machine = Machine(slots=3, slot_depth=10)
        products = {
            "coca-cola": Product(name="coca-cola", quantity=7, price=Decimal(2.1)),
            "mars": Product(name="mars", quantity=5, price=Decimal(1.9)),
            "orbit": Product(name="orbit", quantity=6, price=Decimal(2.3)),
        }
        money = Coins({Decimal(2): 1, Decimal(0.1): 1})
        machine.load_products(products)
        slot_code, _ = machine.get_available_products()["coca-cola"]
        product, change = machine.choose_product(slot_code, money)
        self.assertIsNotNone(product)
        self.assertIsNone(change)
        self.assertEqual(product.name, "coca-cola")

    def test_can_buy_available_product_and_change(self):
        machine = Machine(slots=3, slot_depth=10)
        products = {
            "coca-cola": Product(name="coca-cola", quantity=7, price=Decimal(2.1)),
            "mars": Product(name="mars", quantity=5, price=Decimal(1.9)),
            "orbit": Product(name="orbit", quantity=6, price=Decimal(2.3)),
        }
        money = Coins({Decimal(2): 2, Decimal(0.1): 2})
        machine.load_products(products)
        slot_code, _ = machine.get_available_products()["coca-cola"]
        product, change = machine.choose_product(slot_code, money)
        self.assertIsNotNone(product)
        self.assertIsNotNone(change)
        self.assertEqual(product.name, "coca-cola")
        self.assertEqual(change, Coins({Decimal(2): 1, Decimal(0.1): 1}))

    def test_can_buy_available_product_and_different_change(self):
        machine = Machine(slots=3, slot_depth=10)
        products = {
            "coca-cola": Product(name="coca-cola", quantity=7, price=Decimal(2.1)),
            "mars": Product(name="mars", quantity=5, price=Decimal(1.9)),
            "orbit": Product(name="orbit", quantity=6, price=Decimal(2.3)),
        }
        money = Coins({Decimal(2): 1, Decimal(0.5): 1})
        machine.load_products(products)
        machine.load_coins(Coins({Decimal(0.2): 2}))
        slot_code, _ = machine.get_available_products()["coca-cola"]
        product, change = machine.choose_product(slot_code, money)
        self.assertIsNotNone(product)
        self.assertIsNotNone(change)
        self.assertEqual(product.name, "coca-cola")
        self.assertEqual(change, Coins({Decimal(0.2): 2}))

    def test_cant_get_product_for_too_little_money(self):
        machine = Machine(slots=3, slot_depth=10)
        products = {
            "coca-cola": Product(name="coca-cola", quantity=7, price=Decimal(2.1)),
            "mars": Product(name="mars", quantity=5, price=Decimal(1.9)),
            "orbit": Product(name="orbit", quantity=6, price=Decimal(2.3)),
        }
        too_little_money_to_buy_coke = Coins({Decimal(0.2): 2})
        machine.load_products(products)
        slot_code, _ = machine.get_available_products()["coca-cola"]
        product, change = machine.choose_product(slot_code, too_little_money_to_buy_coke)
        self.assertIsNone(product)
        self.assertIsNotNone(change)
        self.assertEqual(change, too_little_money_to_buy_coke)

    def test_cant_buy_unavailable_product(self):
        machine = Machine(slots=3, slot_depth=10)
        products = {
            "coca-cola": Product(name="coca-cola", quantity=1, price=Decimal(2.1)),
            "mars": Product(name="mars", quantity=5, price=Decimal(1.9)),
            "orbit": Product(name="orbit", quantity=6, price=Decimal(2.3)),
        }
        machine.load_products(products)
        machine.load_coins(Coins({Decimal(0.2): 2}))
        money = Coins({Decimal(2): 2, Decimal(0.1): 2})
        slot_code, _ = machine.get_available_products()["coca-cola"]
        machine.choose_product(slot_code, money)
        product, change = machine.choose_product(slot_code, money)
        self.assertIsNone(product)
        self.assertEqual(money, change)
        self.assertEqual(machine.get_balance(), Decimal(0.4))

    def test_buy_a_product_if_cant_give_a_change(self):
        machine = Machine(slots=3, slot_depth=10)
        products = {
            "coca-cola": Product(name="coca-cola", quantity=1, price=Decimal(2.1)),
            "mars": Product(name="mars", quantity=5, price=Decimal(1.9)),
            "orbit": Product(name="orbit", quantity=6, price=Decimal(2.3)),
        }
        machine.load_products(products)
        money = Coins({Decimal(5): 1})
        slot_code, _ = machine.get_available_products()["coca-cola"]
        product, change = machine.choose_product(slot_code, money)
        self.assertIsNone(product)
        self.assertEqual(money, change)
        self.assertEqual(machine.get_balance(), Decimal(0))

    def test_machine_keeps_track_of_available_products(self):
        pass


if __name__ == '__main__':
    unittest.main()
