from typing import Callable, TypeVar
from enum import Enum
from abc import ABC, abstractmethod
import math


class Converter():
    def __init__(self,
                 from_base: Callable[[float], float],
                 to_base: Callable[[float], float]) -> None:
        self.from_base = from_base
        self.to_base = to_base


class LinearConverter(Converter):
    def __init__(self, from_base_coeff: float, from_base_offset: float):
        super().__init__(
            from_base=lambda v: v*from_base_coeff+from_base_offset,
            to_base=lambda v: (v-from_base_offset)/from_base_coeff)


class MultConverter(Converter):
    def __init__(self, from_base_coeff: float):
        if from_base_coeff == 0:
            raise ValueError("Coeff must be != 0")
        super().__init__(
            from_base=lambda v: v*from_base_coeff,
            to_base=lambda v: v/from_base_coeff)


class Measure(ABC):
    def __init__(self, value: float, unit: Enum) -> None:
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

    def convert_to(self, unit: Enum) -> _Self:
        converter = unit.value
        converted_value = converter.from_base(self.base_value)
        return Temperature(converted_value, unit)

    def __add__(self, other: _Self):
        if not isinstance(other, self.__class__):
            raise TypeError((f'Values must have the same type {self.__class__}'
                            f' and {other.__class__} are given'))

        result_base_value = self.base_value + other.base_value
        result = (self.
                  __class__(result_base_value, self.base_unit).
                  convert_to(self.unit))
        return result

    def __sub__(self, other: _Self):
        if not isinstance(other, self.__class__):
            raise TypeError((f'Values must have the same type {self.__class__}'
                             f' and {other.__class__} are given'))

        result_base_value = self.base_value - other.base_value
        result = (self.
                  __class__(result_base_value, self.base_unit).
                  convert_to(self.unit))
        return result

    def __str__(self) -> str:
        return f'{self.value} {self.unit.name}'

    def __repr__(self) -> str:
        return (f'Values:{self.value} {self.unit.name}.'
                f' Base: {self.base_value} {self.base_unit}')


class Temperature(Measure):
    class SupportedUnits(Enum):
        C = LinearConverter(1, 0)
        F = LinearConverter(1.8, 32)
        K = LinearConverter(1, 273.15)

    def __init__(self, value: float, unit: SupportedUnits) -> None:
        super().__init__(value, unit)

    def _set_base_values(self):
        self.base_value = self.unit.value.to_base(self.value)
        self.base_unit = Temperature.SupportedUnits.C


class Pressure(Measure):
    class SupportedUnits(Enum):
        Pa = MultConverter(1)
        kPa = MultConverter(1000)
        MPa = MultConverter(1000000)
        kgs_sm_2 = MultConverter(0.0000102)
        kgs_m_2 = MultConverter(0.10197162)
        bar = MultConverter(1e-5)
        mm_hg = MultConverter(0.0075006158)
        mm_h20 = MultConverter(0.10197162)
        m_h20 = MultConverter(0.00010197162)
        atm = MultConverter(0.0000098692327)

    def _set_base_values(self):
        self.base_value = self.unit.value.to_base(self.value)
        self.base_unit = Pressure.SupportedUnits.Pa


class Mass_Flow(Measure):
    class SupportedUnits(Enum):
        kg_h = MultConverter(1)
        t_h = MultConverter(0.001)
        kg_d = MultConverter(24)
        kg_s = MultConverter(1/3600)
        t_s = MultConverter(0.001/3600)

    def _set_base_values(self):
        self.base_value = self.unit.value.to_base(self.value)
        self.base_unit = Mass_Flow.SupportedUnits.kg_h


class PtResistToTemperatureConverter(Converter):
    def __init__(self, R0: float, A: float, B: float, C: float, D:tuple) -> None:

        def from_base(t):
            if t<-200 or t > 850:
                raise ValueError("t must be in [-200,850] C")
            if -200 <= t <= 0:
                return R0*(1+A*t+B*(t**2)+C*(t-100)*(t**3))
            else:
                return R0*(1+A*t+B*(t**2))
        
        def to_base(R):
            if R/R0 >= 1:
                return (math.sqrt((A**2)-4*B*(1-R/R0))-A)/(2*B)
            else:
                t = 0
                i = 1
                for d in D:
                    t = t + d*(R/R0-1)**i
            
        super().__init__(from_base, to_base)


class P100(Measure):
    class SupportedUnits(Enum):
        C = MultConverter(1)
        Ohm = PtResistToTemperatureConverter(100,
                                             3.9690e-3,
                                             -5.841e-7,
                                             -4.330e-12,
                                             (251.903, 8.80035, -2.91506, 1.67611))
        F = LinearConverter(1.8, 32)
        K = LinearConverter(1, 273.15)

    def _set_base_values(self):
        self.base_value = self.unit.value.to_base(self.value)
        self.base_unit = P100.SupportedUnits.Ohm

class Pt100(Measure):
    class SupportedUnits(Enum):
        C = MultConverter(1)
        Ohm = PtResistToTemperatureConverter(100,
                                             3.9083e-3,
                                             -5.775e-7,
                                             -4.183e-12,
                                             (255.819, 9.14550, -2.92363, 1.79090))
        F = LinearConverter(1.8, 32)
        K = LinearConverter(1, 273.15)

    def _set_base_values(self):
        self.base_value = self.unit.value.to_base(self.value)
        self.base_unit = P100.SupportedUnits.Ohm


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

    pres_units = Pressure.SupportedUnits
    press_Pa = Pressure(101325, pres_units.Pa)
    print(press_Pa.convert_to(pres_units.atm))

    p100_units = P100.SupportedUnits
    p100 = P100(-200, p100_units.C)
    print(p100.convert_to(p100_units.C))

    print(f'{p100} = {p100.convert_to(p100_units.Ohm)} = {p100.convert_to(p100_units.F)}  = {p100.convert_to(p100_units.K)}')

    pt100_units = Pt100.SupportedUnits
    pt100 = Pt100(-50,pt100_units.C)
    print(f'{pt100} = {pt100.convert_to(pt100_units.Ohm)} = {pt100.convert_to(pt100_units.F)}  = {pt100.convert_to(pt100_units.K)}')

