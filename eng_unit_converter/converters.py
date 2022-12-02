import math
from abc import ABC, abstractmethod


class Converter(ABC):
    def __init__(self,
                 base_low=None,
                 base_hi=None) -> None:

        self.base_hi = base_hi
        self.base_low = base_low

        if self.base_hi is not None:
            self.converted_hi = self.from_base(self.base_hi)
        else:
            self.converted_hi = None

        if self.base_low is not None:
            self.converted_low = self.from_base(self.base_low)
        else:
            self.converted_low = None

    def _check_limits(self,
                      value: float,
                      low_limit: float = None,
                      hi_limit: float = None,
                      precision: float = 2):
        if low_limit is not None:
            if round(value, precision) < round(low_limit, precision):
                raise ValueError(f'Value must be >= {low_limit}')

        if hi_limit is not None:
            if round(value, precision) > round(hi_limit, precision):
                raise ValueError(f'Value must be <= {hi_limit}')

    def from_base(self, value, precision: float = 2) -> float:
        self._check_limits(value, self.base_low, self.base_hi, precision)
        return self._from_base(value)

    def to_base(self, value, precision: float = 2) -> float:
        self._check_limits(value, self.converted_low, self.converted_hi, precision)
        return self._to_base(value)



    @abstractmethod
    def _from_base(self, value) -> float:
        pass

    @abstractmethod
    def _to_base(self, value) -> float:
        pass


class LinearConverter(Converter):
    def __init__(self,
                 from_base_coeff: float,
                 from_base_offset: float,
                 base_low: float = None,
                 base_hi: float = None):
        if from_base_coeff == 0:
            raise ValueError('from_base_coeff must be non zero!')

        self.from_base_coeff = from_base_coeff
        self.from_base_offset = from_base_offset
        super().__init__(
            base_low=base_low,
            base_hi=base_hi)

    def _from_base(self, value) -> float:
        return value*self.from_base_coeff+self.from_base_offset

    def _to_base(self, value) -> float:
        return (value-self.from_base_offset)/self.from_base_coeff


class MultConverter(LinearConverter):
    def __init__(self,
                 from_base_coeff: float,
                 base_low: float = None,
                 base_hi: float = None):
        if from_base_coeff == 0:
            raise ValueError('from_base_coeff must be non zero!')

        super().__init__(
            from_base_coeff=from_base_coeff,
            from_base_offset=0,
            base_low=base_low,
            base_hi=base_hi)


class PtResistConverter(Converter):
    def __init__(self,
                 R0: float,
                 A: float,
                 B: float,
                 C: float,
                 D: tuple,
                 base_low: float = -200,
                 base_hi: float = 850) -> None:
        self.R0 = R0
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        super().__init__(base_low, base_hi)

    def _from_base(self, t):
        #self._check_limits(t, self.base_low, self.base_hi)

        if -200 <= t <= 0:
            return self.R0*(1+self.A*t+self.B*(t**2)+self.C*(t-100)*(t**3))
        else:
            return self.R0*(1+self.A*t+self.B*(t**2))

    def _to_base(self, R):
        #self._check_limits(R, self.converted_low, self. converted_hi)

        if R/self.R0 >= 1:
            return ((math.sqrt((self.A**2)-4*self.B*(1-R/self.R0))-self.A)
                    /
                    (2*self.B))
        else:
            t = 0
            for i, d in enumerate(self.D):
                t = t + d*(R/self.R0-1)**(i+1)
                i = i+1
            return t


class CuResistConverter(Converter):
    def __init__(self,
                 R0: float,
                 A: float,
                 B: float,
                 C: float,
                 D: tuple,
                 base_low: float = -180,
                 base_hi: float = 200) -> None:

        self.R0 = R0
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        super().__init__(base_low, base_hi)

    def _from_base(self, t):
        self._check_limits(t, self.base_low, self.base_hi)

        if -180 <= t <= 0:
            return self.R0*(1+self.A*t+self.B*t*(t+6.7)+self.C*(t**3))
        else:
            return self.R0*(1+self.A*t)

    def _to_base(self, R):
        self._check_limits(R, self.converted_low, self. converted_hi)

        if R/self.R0 >= 1:
            return (R/self.R0-1)/self.A
        else:
            t = 0
            for i, d in enumerate(self.D):
                t = t+d*(R/self.R0-1)**(i+1)
            return t


class NiResistConverter(Converter):
    def __init__(self,
                 R0: float,
                 A: float,
                 B: float,
                 C: float,
                 D: tuple,
                 base_low: float = -60,
                 base_hi: float = 180) -> None:

        self.R0 = R0
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        super().__init__(base_low, base_hi)

    def _from_base(self, t):
        #self._check_limits(t, self.base_low, self.base_hi)

        if -60 <= t <= 100:
            return self.R0*(1+self.A*t+self.B*(t**2))
        else:
            return self.R0*(1+self.A*t+self.B*(t**2)+self.C*(t-100)*(t**2))

    def _to_base(self, R):
        #self._check_limits(R, self.converted_low, self. converted_hi)

        if R <= 161.72:  # t<=100
            return (math.sqrt((self.A**2)-4*self.B*(1-R/self.R0))-self.A)/(2*self.B)
        else:
            t = 100
            for i, d in enumerate(self.D):
                t = t + d*(R/self.R0-1.6172)**(i+1)
            return t

    @classmethod
    def get_Ni_100(cls):
        return cls(100,
                                         5.4963e-3,
                                         6.7556e-6,
                                         9.2004e-9,
                                         (144.096,
                                          -25.502,
                                          4.4876))