import unittest
from math import ceil
from vending_machine import *


class VendingMachineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.snack_space_requirement = {"Chocolate bar": 1, "Strawberry Bar": 3, "Orange juice": 4, "Apple Juice": 4}
        self.machine = VendingMachine(self.snack_space_requirement)
        self.number_of_rows = sum([v for _, v in self.snack_space_requirement.items()])

    def test_empty_machine(self):
        self.assertEqual(self.machine.empty_rows, self.number_of_rows)
        self.assertEqual(self.machine.quantity, 0)

    def test_delivery(self):
        delivery = {"Chocolate bar": 10, "Strawberry Bar": 5, "Orange juice": 20, "Apple Juice": 15}
        self.machine.deliver(delivery)
        rows_taken = sum([ceil(quantity / self.machine.row_depth) for _, quantity in delivery.items()])
        self.assertEqual(self.machine.empty_rows,  self.number_of_rows - rows_taken)
        self.assertEqual(self.machine.quantity, 50)
        new_delivery = {"Strawberry Bar": 25, "Orange juice": 20, "Apple Juice": 25}
        self.machine.deliver(new_delivery)
        self.assertEqual(self.machine.quantity, 120)
