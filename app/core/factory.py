from abc import ABC, abstractmethod

class Operation(ABC):
    def __init__(self, a: float, b: float):
        self.a = a
        self.b = b

    @abstractmethod
    def execute(self) -> float:
        pass

class Add(Operation):
    def execute(self) -> float:
        return self.a + self.b

class Subtract(Operation):
    def execute(self) -> float:
        return self.a - self.b

class Multiply(Operation):
    def execute(self) -> float:
        return self.a * self.b

class Divide(Operation):
    def execute(self) -> float:
        if self.b == 0:
            raise ValueError("Cannot divide by zero.")
        return self.a / self.b

class CalculationFactory:
    _operations = {
        "add": Add,
        "subtract": Subtract,
        "multiply": Multiply,
        "divide": Divide,
    }

    @staticmethod
    def get_operation(op_type: str) -> type[Operation]:
        op_class = CalculationFactory._operations.get(op_type)
        if not op_class:
            raise KeyError(f"Operation '{op_type}' not supported.")
        return op_class