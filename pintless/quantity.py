
from __future__ import annotations
from typing import Union, TYPE_CHECKING

import pintless.unit as unit


class Quantity:
    """Represents a value paired with a unit.  The value can be any python object, but is
    expected to be a numeric type (typically float, int, complex) that responds to the
    usual __add__, __mul__, etc.

    Quantity objects can be constructed by multiplying a python object by a Unit object.

    Quantity objects can have their values extracted using .magnitude(), and can be converted
    to new units using .to() or .ito().  This follows the API established by the pint library."""

    def __init__(self, magnitude, unit) -> None:
        self.magnitude = magnitude
        self._set_unit(unit)

    def _set_unit(self, unit) -> None:
        """Set self.unit.  This should only be set when the object is constructed,
        or when the in-place conversion method ito() is called.

        This is a pint compatibility effort: ideally self.units and self.dimensionality
        would not exist"""
        self.unit = unit

        # These two are for pint compatibility
        self.units = self.unit
        self.dimensionality = self.unit.unit_type

    def to(self, target_unit: Union[str, unit.Unit]) -> Quantity:
        """Convert this Quantity to another unit"""

        if isinstance(target_unit, str):
            if self.unit.registry is None:
                raise ValueError("Cannot process string input for conversion if a registry is not linked to the units.  Set link_to_registry=True when creating units.")
            target_unit = self.unit.registry.get_unit(target_unit)

        return Quantity(self.magnitude * self.unit.conversion_factor(target_unit),
                        target_unit)

    # def ito(self, target_unit: Union[str, Unit]) -> None:
    def ito(self, target_unit: Union[str, unit.Unit]) -> None:
        """In-place version of to"""

        if isinstance(target_unit, str):
            if self.unit.registry is None:
                raise ValueError("Cannot process string input for conversion if a registry is not linked to the units.  Set link_to_registry=True when creating units.")
            target_unit = self.unit.registry.get_unit(target_unit)

        self.magnitude *= self.unit.conversion_factor(target_unit)
        self._set_unit(target_unit)

    # https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types

    def __bool__(self) -> bool:
        # This is valid because this lib doesn't support non-0-centred values
        return self.magnitude.__bool__()

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, Quantity) and self.magnitude == __o.magnitude and self.unit == __o.unit

    def __lt__(self, __o: object) -> bool:
        return isinstance(__o, Quantity) and self.magnitude < __o.magnitude * self.unit.conversion_factor(__o.unit)

    def __add__(self, __o: object) -> Quantity:
        if not isinstance(__o, Quantity):
            raise ValueError("Cannot add Quantity and non-Quantity, use .to('unit').magnitude to strip units first")
        assert self.unit.unit_type == __o.unit.unit_type

        # Convert other unit to this unit, then create new Quantity
        return Quantity(self.magnitude + (__o.magnitude * __o.unit.conversion_factor(self.unit)), self.unit)

    def __neg__(self) -> Quantity:
        """Unary negation of the obect, as in -1"""
        return Quantity(-self.magnitude, self.unit)

    def __pos__(self) -> Quantity:
        """Unary positation of the obect, as in -1"""
        return Quantity(+self.magnitude, self.unit)

    def __abs__(self) -> Quantity:
        """Unary positation of the obect, as in -1"""
        return Quantity(abs(self.magnitude), self.unit)

    def __mul__(self, __o: object) -> Quantity:
        """Multiply the Quantity.  Outputs something with compound units"""

        # Someone is 'adding' units to this quantity
        if isinstance(__o, unit.Unit):
            return Quantity(self.magnitude, self.unit * __o)

        if not isinstance(__o, Quantity):
            # Assume it's a magnitude.  Maybe warn on this condition?
            __o = Quantity(__o, self.unit.dimensionless_unit)

        multiplied_magnitude = self.magnitude * __o.magnitude
        conversion_factor, simplified_new_unit = (self.unit * __o.unit).simplify()
        # Units have multiply logic built in, and numbers do: 10s * 5kW = 50kW*s
        return Quantity(multiplied_magnitude * conversion_factor, simplified_new_unit)

    def __truediv__(self, __o: object) -> Quantity:
        """'true' division, where 2/3 is 0.66 rather than 0"""

        if not isinstance(__o, Quantity):
            # Assume it's a magnitude.  Maybe warn on this condition?
            __o = Quantity(__o, self.unit.dimensionless_unit)

        # divide, then simplify.
        divided_magnitude = self.magnitude / __o.magnitude
        conversion_factor, simplified_new_unit = (self.unit / __o.unit).simplify()
        return Quantity(divided_magnitude * conversion_factor, simplified_new_unit)



    # # TODO
    # object.__truediv__(self, other)
    # object.__floordiv__(self, other)
    # object.__mod__(self, other)
    # object.__divmod__(self, other)
    # object.__pow__(self, other[, modulo])
    # object.__lshift__(self, other)
    # object.__rshift__(self, other)
    # object.__and__(self, other)
    # object.__xor__(self, other)
    # object.__or__(self, other)

    def __invert__(self) -> Quantity:
        """Unary positation of the obect, as in -1"""
        return Quantity(~self.magnitude, self.unit)

    def __round__(self, ndigits=None):
        return Quantity(round(self.magnitude, ndigits), self.unit)

    def __trunc__(self):
        return Quantity(trunc(self.magnitude), self.unit)

    def __floor__(self):
        return Quantity(floor(self.magnitude), self.unit)

    def __ceil__(self):
        return Quantity(ceil(self.magnitude), self.unit)

    def __complex__(self) -> complex:
        """Return a complex number with the imaginary component as 0"""
        return complex(self.magnitude, 0)

    def __float__(self) -> float:
        return float(self.magnitude)

    def __int__(self) -> int:
        return int(self.magnitude)

    def __str__(self) -> str:
        return f"{self.magnitude} {self.unit.name}"

    def __repr__(self) -> str:
        return f"<Quantity({self.magnitude}, '{self.unit.name}')>"
        return self.__str__()
