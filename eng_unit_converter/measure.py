from typing import TypeVar, Dict, Union
from enum import Enum
from abc import ABC, abstractmethod
from .converters import (Converter,
                        LinearConverter,
                        MultConverter,
                        PtResistConverter,
                        CuResistConverter,
                        NiResistConverter)

class UnitsHolder:
    def __init__(self, eu) -> None:
        self.eu = eu
    def __str__(self):
        return self.eu


class Measure(ABC):
    def __init__(self, value: float, unit: Enum, scale_hi: float = None, scale_low: float = None) -> None:
        self.value = value
        self.unit = unit
        self.base_value = 0
        self.base_unit = unit
        self._converters: Dict[Enum, Converter] = self._get_converters()
        self.base_scale_low: float = None
        self.base_scale_hi: float = None
        self._set_base_values()

    _Self = TypeVar('_Self', bound='Measure')

    @abstractmethod
    def _set_base_values(self):
        """Method should set base internal representation of physical value, eng units and converion limits for base_value"""
        pass

    class SupportedUnits:
        BaseUnit = UnitsHolder('BU')

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
        return (f'Value:{self.value} {self.unit.value}.'
                f' Base: {self.base_value} {self.base_unit.value}')


class Temperature(Measure):
    class SupportedUnits(Enum):
        C = UnitsHolder('C')
        F = UnitsHolder('F')
        K = UnitsHolder('K')

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


class Pressure(Measure):
    class SupportedUnits(Enum):
        Pa = UnitsHolder('Pa')
        kPa = UnitsHolder('kPa')
        MPa = UnitsHolder('MPa')
        kgs_sm_2 = UnitsHolder('kgs/sm2')
        kgs_m_2 = UnitsHolder('kgs/m2')
        bar = UnitsHolder('bar')
        mm_hg = UnitsHolder('mm.hg')
        mm_h20 = UnitsHolder('mm.H2O')
        m_h20 = UnitsHolder('m.H2O')
        atm = UnitsHolder('atm')

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
        kg_h = 'kg/h'
        t_h = 't/h'
        kg_d = 'kg/d'
        kg_s = 'kg/s'
        t_s = 't/s'

    def _get_converters(self) -> Dict[Enum, Converter]:
        return {
            self.SupportedUnits.kg_h: MultConverter(1),
            self.SupportedUnits.t_h: MultConverter(0.001),
            self.SupportedUnits.kg_d: MultConverter(24),
            self.SupportedUnits.kg_s: MultConverter(1/3600),
            self.SupportedUnits.t_s: MultConverter(0.001/3600)
        }

    def _set_base_values(self):
        self.base_unit = MassFlow.SupportedUnits.kg_h
        converter = self._converters[self.unit]
        self.base_value = converter.to_base(self.value)


class ThermoResistor(Measure):
    """Work with resistive temperature sensors
      SupportedUnits:
      P100_Ohm - Russian 100П (alpha=0.0391)
    """
    class SupportedUnits(Enum):
        C = UnitsHolder('C')
        F = UnitsHolder('F')
        K = UnitsHolder('K')
        P100_Ohm = UnitsHolder('Ohms')
        P50_Ohm = UnitsHolder('Ohms')

        Pt100_Ohm = UnitsHolder('Ohms')

        Pt50_Ohm = UnitsHolder('Ohms')

        Ni100_Ohm = UnitsHolder('Ohms')

        Cu100_Ohm = UnitsHolder('Ohms')

    def _get_converters(self) -> Dict[Enum, Converter]:
        return {
            self.SupportedUnits.C: MultConverter(1),
            self.SupportedUnits.F: LinearConverter(1.8, 32),
            self.SupportedUnits.K: LinearConverter(1, 273.15),
            self.SupportedUnits.P100_Ohm: PtResistConverter(100,
                                                    3.9690e-3,
                                                    -5.841e-7,
                                                    -4.330e-12,
                                                    (251.903,
                                                    8.80035,
                                                    -2.91506,
                                                    1.67611)),

            self.SupportedUnits.P50_Ohm: PtResistConverter(50,
                                                    3.9690e-3,
                                                    -5.841e-7,
                                                    -4.330e-12,
                                                    (251.903,
                                                    8.80035,
                                                    -2.91506,
                                                    1.67611)),

            self.SupportedUnits.Pt100_Ohm: PtResistConverter(100,
                                                    3.9083e-3,
                                                    -5.775e-7,
                                                    -4.183e-12,
                                                    (255.819,
                                                        9.14550,
                                                        -2.92363,
                                                        1.79090)),

            self.SupportedUnits.Pt50_Ohm: PtResistConverter(50,
                                                    3.9083e-3,
                                                    -5.775e-7,
                                                    -4.183e-12,
                                                    (255.819,
                                                    9.14550,
                                                    -2.92363,
                                                    1.79090)),

            self.SupportedUnits.Ni100_Ohm: NiResistConverter.get_Ni_100(),

            self.SupportedUnits.Cu100_Ohm: CuResistConverter(100,
                                                    4.28e-3,
                                                    -6.2032e-7,
                                                    8.5154e-10,
                                                    (233.87,
                                                    7.9370,
                                                        -2.0062,
                                                        -0.3953)),

            }

    def _set_base_values(self):
        self.base_unit = ThermoResistor.SupportedUnits.C
        converter = self._converters[self.unit]
        self.base_value = converter.to_base(self.value)


class AnalogSensorMeasure(Measure):
    def __init__(self, value: float,
                 unit: Enum,
                 measure_scale_low: float,
                 measure_scale_hi: float,
                 measure_eu: str) -> None:
        self.measure_scale_low = measure_scale_hi
        self.measure_scale_hi = measure_scale_low
        self.measure_eu = measure_eu

        super().__init__(value, unit)

    class SupportedUnits(Enum):
        persent = UnitsHolder('%')
        mA_4_20 = UnitsHolder('mA')
        mA_0_20 = UnitsHolder('mA')
        V_1_5 = UnitsHolder('V')
        MEASURE = UnitsHolder('EU')

    def _set_base_values(self):
        self.base_unit = AnalogSensorMeasure.SupportedUnits.persent
        converter = self._converters[self.unit]
        self.base_value = converter.to_base(self.value)

    def _get_converters(self) -> Dict[Enum, Converter]:
        return {
            self.SupportedUnits.persent: MultConverter(1),
            self.SupportedUnits.mA_4_20: LinearConverter(from_base_coeff=0.16,
                                                         from_base_offset=4),
            self.SupportedUnits.mA_0_20: LinearConverter(from_base_coeff=0.2,
                                                         from_base_offset=0),
            self.SupportedUnits.V_1_5: LinearConverter(from_base_coeff=0.04,
                                                         from_base_offset=1),
            self.SupportedUnits.MEASURE: LinearConverter(from_base_coeff=(self.measure_scale_low-self.measure_scale_hi)/100, from_base_offset=self.measure_scale_hi)
        }

    def convert_to(self, unit: Enum) -> Measure:
        converter = self._converters[unit]
        converted_value = converter.from_base(self.base_value)
        return self.__class__(converted_value, unit, self.measure_scale_hi, self.measure_scale_low, self.measure_eu)

    def __str__(self) -> str:
        if self.unit == self.SupportedUnits.MEASURE:
            return f'{self.value} {self.measure_eu}'
        else:
            return super().__str__()

    def __repr__(self) -> str:
        if self.unit == self.SupportedUnits.MEASURE:
            (f'Value:{self.value} {self.measure_eu}.'
             f' Base: {self.base_value} {self.base_unit}')
        else:
            return super().__repr__()
