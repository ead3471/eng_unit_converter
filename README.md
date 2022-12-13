# Engineering unit converter
Supports base set of Engineering units.
You can convert one unit to another and create on conversion.
Also supports convertion base set of termoresistors(Pt100, 100P, Cu etc) and analog sensors(4-20mA, 1-5V)
## Using Samples
1. Temperature<br>
```
    units = Temperature.SupportedUnits
    value_C = Temperature(10, units.C)
    print(value_C)  # 10 C
    value_K = value_C.convert_to(units.K)
    print(value_K)  # 283.15 C
    print(value_C+value_K)  # 20 C
    print(value_K+value_C)  # 293.15 K
    value_F = Temperature(95, units.F)  # 35 C
    print((value_F-value_C).convert_to(units.C))  # 25 C
```
2. Thermoresistors
```
    units = ThermoResistor.SupportedUnits
    pt_100 = ThermoResistor(119.4, units.Pt100_Ohm)
    celsius = pt_100.convert_to(units.C)
    print(celsius)  # 0.00746647419036 C
```
3. Analog measures
```
    units = AnalogSensorMeasure.SupportedUnits
    measure = AnalogSensorMeasure(12, units.mA_4_20, 0, 100, 'kPa')
    print(measure)  # 12 mA
    sensor_measure = measure.convert_to(units.MEASURE)
    print(sensor_measure)  # 50.0 kPa
    print(sensor_measure.convert_to(units.persent))  # 50 %
