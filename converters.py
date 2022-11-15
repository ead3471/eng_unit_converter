from typing import Callable
import math


class Converter():
    def __init__(self,
                 from_base: Callable[[float], float],
                 to_base: Callable[[float], float],
                 base_hi=None,
                 base_low=None) -> None:
        self.from_base = from_base
        self.to_base = to_base

        self.base_hi=base_hi
        self.base_low=base_low
        if self.base_hi is not None:
            self.converted_hi = self.from_base(self.base_hi)
        else:
            self.base_hi = None
        
        if self.base_low is not None:
            self.converted_low = self.from_base(self.base_low)
        else:
            self.base_hi = None

class LinearConverter(Converter):
    def __init__(self, from_base_coeff: float, from_base_offset: float):
        if from_base_coeff == 0:
            raise ValueError('from_base_coeff must be non zero!')
        super().__init__(
            from_base=lambda v: v*from_base_coeff+from_base_offset,
            to_base=lambda v: (v-from_base_offset)/from_base_coeff)


class MultConverter(Converter):
    def __init__(self, from_base_coeff: float):
        if from_base_coeff == 0:
            raise ValueError("from_base_coeff must be non zero")
        super().__init__(
            from_base=lambda v: v*from_base_coeff,
            to_base=lambda v: v/from_base_coeff)


class PtResistConverter(Converter):
    def __init__(self,
                 R0: float,
                 A: float,
                 B: float,
                 C: float,
                 D: tuple) -> None:

        def from_base(t):
            if t < -200 or t > 850:
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
                for i, d in enumerate(D):
                    t = t + d*(R/R0-1)**(i+1)
                    i = i+1
                return t

        super().__init__(from_base, to_base)


class CuResistConverter(Converter):
    def __init__(self,
                 R0: float,
                 A: float,
                 B: float,
                 C: float,
                 D: tuple) -> None:

        def from_base(t):
            if t < -180 or t > 200:
                raise ValueError("t must be in [-180, 200] C")
            if -180 <= t <= 0:
                return R0*(1+A*t+B*t*(t+6.7)+C*(t**3))
            else:
                return R0*(1+A*t)

        def to_base(R):
            if R < 20.53 or R > 185.6:
                raise ValueError('R must be ')

            if R/R0 >= 1:
                return (R/R0-1)/A
            else:
                t = 0
                for i, d in enumerate(D):
                    t = t+d*(R/R0-1)**(i+1)
                return t

        super().__init__(from_base, to_base)


class NiResistConverter(Converter):
    def __init__(self,
                 R0: float,
                 A: float,
                 B: float,
                 C: float,
                 D: tuple) -> None:

        def from_base(t):
            if t < -60 or t > 180:
                raise ValueError("t must be in [-60,100] C")
            if -60 <= t <= 100:
                return R0*(1+A*t+B*(t**2))
            else:
                return R0*(1+A*t+B*(t**2)+C*(t-100)*(t**2))

        def to_base(R):
            if R > 223.21 or R < 69.45:
                raise ValueError('R must be in [69.45, 223.21]')

            if R <= 161.72:  # t<=100
                return (math.sqrt((A**2)-4*B*(1-R/R0))-A)/(2*B)
            else:
                t = 100
                for i, d in enumerate(D):
                    t = t + d*(R/R0-1.6172)**(i+1)
                return t

        super().__init__(from_base, to_base)
