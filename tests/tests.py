import unittest
from unittest import TestCase
from eng_unit_converter.converters import (Converter,
                                           LinearConverter,
                                           MultConverter,
                                           PtResistConverter,
                                           CuResistConverter,
                                           NiResistConverter)


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



if __name__ == "__main__":
    unittest.main()
