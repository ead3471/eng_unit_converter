from typing import Callable, Dict, TypeVar
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


class Converter():
    def __init__(self, from_base: Callable[[float], float], to_base:Callable[[float], float]) -> None:
        self.from_base = from_base
        self.to_base = to_base

class Measure(ABC):
    def __init__(self, value:float, unit:Enum) -> None:
        self.value = value
        self.unit = unit
        self.base_value = 0
        self.base_unit = unit
        self._set_base_values()

    _Self = TypeVar('_Self', bound='Measure')

    @abstractmethod
    def _set_base_values(self):
        pass

    class SupportedUnits(Enum):
        BaseUnit = Converter(
            lambda t: t,
            lambda t: t
        )

    def convert_to(self, unit:Enum) -> _Self:
        converter = unit.value
        converted_value = converter.from_base(self.base_value)
        return Temperature(converted_value, unit)


    def __add__(self, other:_Self):
        if not isinstance(other, self.__class__):
            raise TypeError(f'Values must have the same type. {self.__class__} and {other.__class__} are given')
        
        result_base_value = self.base_value + other.base_value
        result = self.__class__(result_base_value, self.base_unit).convert_to(self.unit)
        return result
    
    def __sub__(self, other:_Self):
        if not isinstance(other, self.__class__):
            raise TypeError(f'Values must have the same type. {self.__class__} and {other.__class__} are given')
        
        result_base_value = self.base_value - other.base_value
        result = self.__class__(result_base_value, self.base_unit).convert_to(self.unit)
        return result

    def __str__(self) -> str:
        return f'{self.value} {self.unit.name}'

    def __repr__(self) -> str:
        return f'Values:{self.value} {self.unit.name}. Base: {self.base_value} {self.base_unit}'



class Temperature(Measure):

    class SupportedUnits(Enum):
        C = Converter(
            lambda t: t,
            lambda t: t
        )
        F = Converter(
            from_base = lambda t: 1.8*t+32,
            to_base = lambda t: (t-32)/1.8
        )
        K = Converter(
            from_base = lambda t: t+273.15,
            to_base = lambda t: t-273.15)

    def __init__(self, value:float, unit: SupportedUnits) -> None:
        super().__init__(value, unit)
    
    def _set_base_values(self):
        self.base_value = self.unit.value.to_base(self.value)
        self.base_unit = Temperature.SupportedUnits.C

    


if __name__ == "__main__":
    temp_units = Temperature.SupportedUnits
    temp_c = Temperature(1,temp_units.C)
    print(f'{temp_c} = {temp_c.convert_to(Temperature.SupportedUnits.F)} = {temp_c.convert_to(Temperature.SupportedUnits.K)}')
    temp_f = Temperature(2,Temperature.SupportedUnits.F)
    print(f'{temp_f} = {temp_f.convert_to(Temperature.SupportedUnits.C)} = {temp_f.convert_to(Temperature.SupportedUnits.K)}')

    result = Temperature(1,Temperature.SupportedUnits.C)+Temperature(2,Temperature.SupportedUnits.F)
    print(result)

    result = Temperature(1,Temperature.SupportedUnits.C)-Temperature(2,Temperature.SupportedUnits.F)
    print(result)




