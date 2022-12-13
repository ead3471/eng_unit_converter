import unittest
from unittest import TestCase
from typing import Dict

from eng_unit_converter.measure import (Measure,
                                        Temperature,
                                        AnalogSensorMeasure,
                                        MassFlow,
                                        ThermoResistor)

from eng_unit_converter.converters import (Converter,
                                           LinearConverter,
                                           MultConverter,
                                           PtResistConverter,
                                           CuResistConverter,
                                           NiResistConverter)


from enum import Enum

PT_100_MEASURE_POINTS = {-200.0: 18.52,
                         -100.0: 60.26,
                         0.0: 100.0,
                         50.0: 119.4,
                         100.0: 138.51,
                         150.0: 157.33,
                         200.0: 175.86,
                         500.0: 280.98,
                         850.0: 390.48
                         }

P100_MEASURE_POINTS = {-200.0: 17.24,
                       -100.0: 59.64,
                       0.0: 100.0,
                       50.0: 119.7,
                       100.0: 139.11,
                       150.0: 158.22,
                       200.0: 177.04,
                       500.0: 283.85,
                       850.0: 395.16
                       }

CU_MEASURE_POINTS = {-180.0: 20.53,
                     -100.0: 56.54,
                     0.0: 100.0,
                     50.0: 121.4,
                     100.0: 142.8,
                     150.0: 164.2,
                     200.0: 185.6
                     }

NI_MEASURE_POINTS = {-60.0: 69.45,
                     0.0: 100.0,
                     50.0: 129.17,
                     100.0: 161.72,
                     150.0: 198.68,
                     180.0: 223.21
                     }


class TestConverters(TestCase):

    def check_converter_bounds(self, converter: Converter):

        base_value_borders = (converter.base_low-1, converter.base_hi+1)
        converted_value_borders = (converter.converted_low-1,
                                   converter.converted_hi+1)
        for base_value in base_value_borders:
            with self.subTest(base_value=base_value):
                with self.assertRaises(ValueError):
                    converter.from_base(base_value)

        for converted_value in converted_value_borders:
            with self.subTest(converted_value=converted_value):
                with self.assertRaises(ValueError):
                    converter.to_base(converted_value)

    def test_linear_converter(self):
        converter_1 = LinearConverter(from_base_coeff=1,
                                      from_base_offset=2,
                                      base_low=0,
                                      base_hi=5)
        self.check_converter_bounds(converter_1)
        self.assertEqual(converter_1.from_base(2), 4)
        self.assertEqual(converter_1.to_base(4), 2)

    def test_mult_converter_zero_coeff_raize(self):
        with self.assertRaises(ValueError):
            MultConverter(0)

    def test_mult_converter(self):
        converter = MultConverter(from_base_coeff=42, base_low=0, base_hi=50)
        self.check_converter_bounds(converter)
        self.assertEqual(converter.from_base(2), 84)
        self.assertEqual(converter.to_base(84), 2)

    def test_platinum_resist_converter(self):
        pt100_converter = PtResistConverter(100,
                                            3.9083e-3,
                                            -5.775e-7,
                                            -4.183e-12,
                                            (255.819,
                                             9.14550,
                                             -2.92363,
                                             1.79090))

        self.check_converter_bounds(pt100_converter)

        for temp, resist in PT_100_MEASURE_POINTS.items():
            with self.subTest(temp=temp, resist=resist):
                self.assertAlmostEqual(resist,
                                       pt100_converter.from_base(temp),
                                       delta=0.01)
                self.assertAlmostEqual(temp,
                                       pt100_converter.to_base(resist),
                                       delta=0.015)

    def test_cu_resist_converter(self):
        cu_converter = CuResistConverter(100,
                                         4.28e-3,
                                         -6.2032e-7,
                                         8.5154e-10,
                                         (233.87,
                                          7.9370,
                                          -2.0062,
                                          -0.3953))

        self.check_converter_bounds(cu_converter)

        for temp, resist in CU_MEASURE_POINTS.items():
            with self.subTest(temp=temp, resist=resist):
                self.assertAlmostEqual(resist,
                                       cu_converter.from_base(temp),
                                       delta=0.01)
                self.assertAlmostEqual(temp,
                                       cu_converter.to_base(resist),
                                       delta=0.01)

    def test_ni_resist_converter(self):
        ni_converter = NiResistConverter(100,
                                         5.4963e-3,
                                         6.7556e-6,
                                         9.2004e-9,
                                         (144.096,
                                          -25.502,
                                          4.4876))

        self.check_converter_bounds(converter=ni_converter)

        for temp, resist in NI_MEASURE_POINTS.items():
            with self.subTest(temp=temp, resist=resist):
                self.assertAlmostEqual(resist,
                                       ni_converter.from_base(temp),
                                       delta=0.01)
                self.assertAlmostEqual(temp,
                                       ni_converter.to_base(resist),
                                       delta=0.01)


class TestMeasure(TestCase):
    def check_converted_measure(self,
                                source_measure: Measure,
                                convert_unit: Enum,
                                expected_value: float,
                                precision: float = 0.001):

        new_measure: Measure = source_measure.convert_to(convert_unit)
        self.assertIsInstance(new_measure, source_measure.__class__)
        self.assertAlmostEqual(new_measure.value,
                               expected_value,
                               delta=precision)
        self.assertEqual(new_measure.unit, convert_unit)
        self.assertAlmostEqual(new_measure.base_value,
                               source_measure.base_value,
                               delta=precision)
        self.assertEqual(new_measure.base_unit, source_measure.base_unit)

    def check_measures(self,
                       source_measure: Measure,
                       measures: dict,
                       precision: float = 0.001):
        for unit, value in measures.items():
            with self.subTest(source_measure=source_measure,
                              unit=unit.name,
                              value=value):
                self.check_converted_measure(source_measure, unit, value)

    def test_temperature_measure(self):
        temp_in_C = Temperature(123.5, Temperature.SupportedUnits.C)
        temp_units = Temperature.SupportedUnits
        self.check_converted_measure(temp_in_C, temp_units.F, 254.3)
        self.check_converted_measure(temp_in_C, temp_units.K, 273.15+123.5)
        self.check_converted_measure(temp_in_C, temp_units.C, temp_in_C.value)

    def test_temperature_measure_arithmetic(self):
        units = Temperature.SupportedUnits
        value1 = Temperature(10, units.C)
        value2 = Temperature(283.15, units.K)  # 10 C
        summ: Temperature = value1 + value2
        self.assertIsInstance(summ, Temperature)
        self.assertEquals(summ.unit, units.C)
        self.assertEquals(summ.value, 20.0)

        summ: Temperature = value2 + value2
        self.assertIsInstance(summ, Temperature)
        self.assertEquals(summ.unit, units.K)
        self.assertEquals(summ.value, 293.15)

        value3 = Temperature(95, units.F)  # 35C
        summ: Temperature = value3+value2+value1
        self.assertIsInstance(summ, Temperature)
        self.assertEquals(summ.unit, units.F)
        self.assertEquals(summ.value, 131.0)  # 55C

        summ: Temperature = value3-value2-value1
        self.assertIsInstance(summ, Temperature)
        self.assertEquals(summ.unit, units.F)
        self.assertEquals(summ.value, 59.0)  # 15C

    def test_analog_sensor_measure(self):
        measure_units = AnalogSensorMeasure.SupportedUnits
        measure_hi = 250
        measure_low = 50

        check_dict: Dict(int, Dict(measure_units, float)) = {
            0: {
                measure_units.mA_4_20: 4,
                measure_units.mA_0_20: 0,
                measure_units.V_1_5: 1,
                measure_units.MEASURE: measure_low
            },
            50: {
                measure_units.mA_4_20: 12,
                measure_units.mA_0_20: 10,
                measure_units.V_1_5: 3,
                measure_units.MEASURE: (measure_low+measure_hi)/2

            },
            100: {
                measure_units.mA_4_20: 20,
                measure_units.mA_0_20: 20,
                measure_units.V_1_5: 5,
                measure_units.MEASURE: measure_hi

            }
        }

        for percent, measure_pairs in check_dict.items():
            analog_measure = AnalogSensorMeasure(percent,
                                                 measure_units.persent,
                                                 measure_low,
                                                 measure_hi,
                                                 'some_unit')

            self.check_measures(analog_measure, measure_pairs)

    def test_analog_masure_to_str(self):
        units = AnalogSensorMeasure.SupportedUnits
        test_measure = AnalogSensorMeasure(12, units.mA_4_20, 0, 100, 'kPa')
        physical_measure = test_measure.convert_to(units.MEASURE)
        self.assertEquals('50.0 kPa', str(physical_measure))

    def test_mass_flow(self):
        units = MassFlow.SupportedUnits
        mass_measure = MassFlow(50, units.kg_h)
        measures = {
            units.kg_d: 50*24,
            units.kg_s: 50/3600,
            units.t_h: 50/1000,
            units.t_s: 50/1000/3600
        }
        self.check_measures(mass_measure, measures)

    def test_thermo_resistor(self):
        units = ThermoResistor.SupportedUnits

        values_dicts: Dict(units.__class__, Dict(float, float)) = {
            units.P100_Ohm: P100_MEASURE_POINTS,
            units.Pt100_Ohm: PT_100_MEASURE_POINTS,
            units.Cu100_Ohm: CU_MEASURE_POINTS,
            units.Ni100_Ohm: NI_MEASURE_POINTS,
            units.F: {0: 32, 50: 122},
            units.K: {0: 273.15, 50: 50+273.15}
        }

        for unit, test_measures in values_dicts.items():
            for celsius_value, converted_value in test_measures.items():
                resistor = ThermoResistor(celsius_value, units.C)
                with self.subTest(resistor=resistor,
                                  unit=unit.name,
                                  converted_value=converted_value):
                    self.check_converted_measure(
                        resistor, unit, converted_value, precision=0.01)


if __name__ == "__main__":
    unittest.main()
