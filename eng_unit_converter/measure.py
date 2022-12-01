from typing import TypeVar, Dict
from enum import Enum
from abc import ABC, abstractmethod
from .converters import (Converter,
                        LinearConverter,
                        MultConverter,
                        PtResistConverter,
                        CuResistConverter,
                        NiResistConverter)


class Measure(ABC):
    def __init__(self, value: float, unit: Enum, scale_hi: float = None, scale_low: float = None) -> None:
        self.value = value
        self.unit = unit
        self.base_value = 0
        self.base_unit = unit
        self._converters: Dict[Enum, Converter] = self._get_converters()
        self.base_scale_low:float = None
        self.base_scale_hi:float = None
        self._set_base_values()

    _Self = TypeVar('_Self', bound='Measure')

    @abstractmethod
    def _set_base_values(self):
        """Method should set base internal representation of physical value, eng units and converion limits for base_value"""
        pass

    class SupportedUnits(Enum):
        BaseUnit = 'BU'

    @abstractmethod
    def _get_converters(self) -> Dict[Enum, Converter]:
        pass

    def convert_to(self, unit: Enum) -> _Self:
        converter = self._converters[unit]
        converted_value = converter.from_base(self.base_value)
        return self.__class__(converted_value, unit)

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
        return f'{self.value} {self.unit.value}'

    def __repr__(self) -> str:
        return (f'Values:{self.value} {self.unit.value}.'
                f' Base: {self.base_value} {self.base_unit}')


class Temperature(Measure):
    class SupportedUnits(Enum):
        C = 'C'
        F = 'F'
        K = 'K'

    def __init__(self, value: float, unit: SupportedUnits) -> None:
        super().__init__(value, unit)

    def _get_converters(self) -> Dict[Enum, Converter]:
        return {
            self.SupportedUnits.C: LinearConverter(1, 0),
            self.SupportedUnits.F: LinearConverter(1.8, 32),
            self.SupportedUnits.K: LinearConverter(1, 273.15)
        }

    def _set_base_values(self):
        self.base_unit = Temperature.SupportedUnits.C
        current_unit_converter = self._converters[self.unit]
        self.base_value = current_unit_converter.to_base(self.value)

        #self._converters[self.base_unit].base_hi = current_unit_converter.to_base(self.base_scale_hi)
        #self._converters[self.base_unit].base_low = current_unit_converter.to_base(self.base_scale_low)





class Pressure(Measure):
    class SupportedUnits(Enum):
        Pa = 'Pa'
        kPa = 'kPa'
        MPa = 'MPa'
        kgs_sm_2 = 'kgs/sm2'
        kgs_m_2 = 'kgs/m2'
        bar = 'bar'
        mm_hg = 'mm.hg'
        mm_h20 = 'mm.H2O'
        m_h20 = 'm.H2O'
        atm = 'atm'

    def _set_base_values(self):
        self.base_unit = Pressure.SupportedUnits.Pa
        self.base_value = self._converters[self.unit].to_base(self.value)

    def _get_converters(self) -> Dict[Enum, Converter]:
        return {
            self.SupportedUnits.Pa: MultConverter(1),
            self.SupportedUnits.kPa: MultConverter(1000),
            self.SupportedUnits.MPa: MultConverter(1000000),
            self.SupportedUnits.kgs_sm_2: MultConverter(0.0000102),
            self.SupportedUnits.kgs_m_2: MultConverter(0.10197162),
            self.SupportedUnits.bar: MultConverter(1e-5),
            self.SupportedUnits.mm_hg: MultConverter(0.0075006158),
            self.SupportedUnits.mm_h20: MultConverter(0.10197162),
            self.SupportedUnits.m_h20: MultConverter(0.00010197162),
            self.SupportedUnits.atm: MultConverter(0.0000098692327)

        }


class MassFlow(Measure):
    class SupportedUnits(Enum):
        kg_h = MultConverter(1)
        t_h = MultConverter(0.001)
        kg_d = MultConverter(24)
        kg_s = MultConverter(1/3600)
        t_s = MultConverter(0.001/3600)

    def _set_base_values(self):
        self.base_unit = MassFlow.SupportedUnits.kg_h
        self.base_value = self.unit.value.to_base(self.value)


class PlatinumThermoResist(Measure):
    """Work with resistive temperature sensors
      SupportedUnits:
      P100_Ohm - Russian 100П (alpha=0.0391)
    """
    class SupportedUnits(Enum):
        C = MultConverter(1)
        F = LinearConverter(1.8, 32)
        K = LinearConverter(1, 273.15)
        P100_Ohm = PtResistConverter(100,
                                                  3.9690e-3,
                                                  -5.841e-7,
                                                  -4.330e-12,
                                                  (251.903,
                                                   8.80035,
                                                   -2.91506,
                                                   1.67611))

        P50_Ohm = PtResistConverter(50,
                                                 3.9690e-3,
                                                 -5.841e-7,
                                                 -4.330e-12,
                                                 (251.903,
                                                  8.80035,
                                                  -2.91506,
                                                  1.67611))

        Pt100_Ohm = PtResistConverter(100,
                                                   3.9083e-3,
                                                   -5.775e-7,
                                                   -4.183e-12,
                                                   (255.819,
                                                    9.14550,
                                                    -2.92363,
                                                    1.79090))

        Pt50_Ohm = PtResistConverter(50,
                                                  3.9083e-3,
                                                  -5.775e-7,
                                                  -4.183e-12,
                                                  (255.819,
                                                   9.14550,
                                                   -2.92363,
                                                   1.79090))

        Ni100_Ohm = NiResistConverter(100,
                                                   5.4963e-3,
                                                   6.7556e-7,
                                                   -4.183e-12,
                                                   (144.096,
                                                    -25.502,
                                                    -4.4876))

        Cu100_Ohm = CuResistConverter(100,
                                                   4.28e-3,
                                                   -6.2032e-7,
                                                   8.5154e-10,
                                                   (233.87,
                                                   7.9370,
                                                    -2.0062,
                                                    -0.3953))

    def _set_base_values(self):
        self.base_unit = PlatinumThermoResist.SupportedUnits.P100_Ohm
        self.base_value = self.unit.value.to_base(self.value)


class CurrentSensorMeasure(Measure):
    def __init__(self, value: float,
                 unit: Enum,
                 scale_hi: float,
                 scale_low: float) -> None:
        self.scale_hi = scale_hi
        self.scale_low = scale_low
        super().__init__(value, unit)

    class SupportedUnits(Enum):
        persent = '%'
        mA = 'mA'
        EU = 'EU'

    def _set_base_values(self):
        self.base_unit = Temperature.SupportedUnits.C
        self.base_value = self._converters[self.unit].to_base(self.value)

    def _get_converters(self) -> Dict[Enum, Converter]:
        return {
            self.SupportedUnits.persent: MultConverter(1),
            self.SupportedUnits.mA: LinearConverter(to)
        }



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

    # pres_units = Pressure.SupportedUnits
    # press_Pa = Pressure(101325, pres_units.Pa)
    # print(press_Pa.convert_to(pres_units.atm))

    # platinum_units = PlatinumThermoResist.SupportedUnits
    # platinum_resistor = PlatinumThermoResist(-200, platinum_units.C)
    # print(platinum_resistor.convert_to(platinum_units.C))

    # print(f'{platinum_resistor} = {platinum_resistor.convert_to(platinum_units.P100_Ohm)} = {platinum_resistor.convert_to(platinum_units.F)}  = {platinum_resistor.convert_to(platinum_units.K)}')

    
