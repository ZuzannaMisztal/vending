import typing


class NotEnoughSpaceException(Exception):
    pass


class SnackSpace:
    def __init__(self, name, starting_index, number_of_rows):
        self.name = name
        self.starting_index = starting_index
        self.number_of_rows = number_of_rows
        self.rows = {index: 0 for index in range(starting_index, starting_index + number_of_rows)}

    @property
    def quantity(self):
        return sum([val for _, val in self.rows.items()])

    def populate_rows(self, quantity, row_depth):
        self.rows = {}
        for index in range(self.starting_index, self.starting_index + self.number_of_rows):
            self.rows[index] = min(quantity, row_depth)
            quantity -= self.rows[index]

    def pick_up(self, delivery, row_depth):
        if self.quantity + delivery > row_depth * self.number_of_rows:
            raise NotEnoughSpaceException
        self.populate_rows(self.quantity + delivery, row_depth)


class VendingMachine:
    row_depth = 10

    def __init__(self, snack_space_requirements):
        self.fridge = []
        index = 0
        for name, number_of_rows in snack_space_requirements.items():
            space = SnackSpace(name, index, number_of_rows)
            self.fridge.append(space)
            index += number_of_rows

    @property
    def empty_rows(self):
        result = 0
        for snack_space in self.fridge:
            result += sum([1 for _, value in snack_space.rows.items() if value == 0])
        return result

    @property
    def quantity(self):
        return sum([snack.quantity for snack in self.fridge])

    def deliver(self, delivery: typing.Dict):
        for snack_space in self.fridge:
            snack_space.pick_up(delivery.get(snack_space.name, 0), self.row_depth)
