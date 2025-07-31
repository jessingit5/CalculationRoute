from pydantic import BaseModel, model_validator, computed_field, ConfigDict
from enum import Enum
from ..core.factory import CalculationFactory

class CalculationType(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"

class CalculationCreate(BaseModel):
    a: float
    b: float
    type: CalculationType

    @model_validator(mode='after')
    def check_division_by_zero(self) -> 'CalculationCreate':
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Division by zero is not allowed.")
        return self

class CalculationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    a: float
    b: float
    type: str
    user_id: int

    @computed_field
    @property
    def result(self) -> float:
        operation = CalculationFactory.get_operation(self.type)
        return operation(self.a, self.b).execute()