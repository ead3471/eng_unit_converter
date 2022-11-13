from typing import Callable, Dict

class Measure:
    def __init__(self) -> None:
        pass

class Converter():
    def __init__(self, from_base: Callable[[float], float], to_base:Callable[[float], float]) -> None:
        self.from_base = from_base
        self.to_base = to_base

class Temperature(Measure):
    def __init__(self, value:float, unit: str) -> None:
        if unit not in self.units:
            raise ValueError(f'Unit parameter must be in {self.units.keys()}. {unit} given')
        self.value = value
        self.unit = unit
        self.base_value = self.units[unit].to_base(value)
        self.base_units = 'C'
        super().__init__()

    units: Dict[str,Converter] = {
        'C': Converter(
            lambda t: t,
            lambda t: t
        ),

        'F': Converter(
            from_base = lambda t: 1.8*t+32,
            to_base = lambda t: (t-32)/1.8
        ),

        'K': Converter(
            from_base = lambda t: t+273.15,
            to_base = lambda t: t-273.15
        )
    }

    def convert_to(self, unit:str) -> Measure:
        if unit in self.units:
            converter = self.units.get(unit)
            value = converter.from_base(self.base_value)
            return Temperature(value, unit)
        else:
            raise ValueError(f'Unit parameter must be in {self.units.keys()}. {unit} given')

    def __str__(self) -> str:
        return f'{self.value} {self.unit}'


if __name__ == "__main__":
    temp_c = Temperature(0,'C')
    print(f'{temp_c} = {temp_c.convert_to("F")} = {temp_c.convert_to("K")}')
    temp_f = Temperature(234,'F')
    print(f'{temp_f} = {temp_f.convert_to("C")} = {temp_f.convert_to("K")}')




