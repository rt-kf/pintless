
import unittest

from pintless import Registry, Quantity, Unit


class UnitTest(unittest.TestCase):

    def setUp(self) -> None:
        self.r = Registry()

    def test_dimensionless_unit(self):

        unit = self.r.get_unit("meter")
        assert unit.dimensionless_unit == self.r.get_unit("")
        assert unit.dimensionless_unit == (unit / unit)


    def test_equality(self):

        r = self.r

        # Basic building blocks are the base units
        base_unit_a = r.meter.numerator_units[0]
        base_unit_b = r.meter.numerator_units[0]
        assert base_unit_a == base_unit_b

        base_unit_a = r.kilometer.numerator_units[0]
        base_unit_b = r.meter.numerator_units[0]
        assert base_unit_a != base_unit_b

        # Units with different scales in the same dimension
        # are not equal
        assert r.meter != r.kilometer
        assert r.dimensionless != r.kilodimensionless

        # Check product units
        assert r.meter * r.second == r.meter * r.second
        assert r.Hz == r.dimensionless / r.second

    def test_dimensionality(self):

        length_b = self.r.get_unit("meter")
        length_a = self.r.get_unit("inch")

        assert length_a.unit_type == "[length]/[dimensionless]"
        assert length_b.unit_type == "[length]/[dimensionless]"

        # length/length should cancel to be dimensionless
        assert (length_a / length_b).unit_type == "[dimensionless]/[dimensionless]"

    def test_conversion_factor(self):

        r = self.r

        # Basics.
        assert r.meter.conversion_factor(r.cm) == 100
        assert r.meter.conversion_factor(r.kilometer) == 0.001

        # Conversion for more complex types
        assert r.Hz.conversion_factor(r.kHz) == 0.001

        # Conversion between incompatible types
        with self.assertRaises(TypeError):
            r.meter.conversion_factor(r.hour)
        with self.assertRaises(TypeError):
            r.meter.conversion_factor(r.Hz)
        with self.assertRaises(TypeError):
            r.meter.conversion_factor(r.dimensionless)

    def test_simplify(self):

        r = self.r

        time = r.H
        distance = r.mile
        assert (time / distance).name == "H/mile"

        # Cancelling denominator units
        assert (r.kW * r.hour) / (r.mile * r.hour) == (r.kW / r.mile)

        # Cancelling with and without conversion factor
        self.assertEqual((10 * r.km) / (20 * r.km), 0.5 * r.dimensionless)
        self.assertEqual((10 * r.km) / (20 * r.meter), 500)
        self.assertEqual((10 * r.km) * (5 * r.meter), 50 * r.km * r.meter)
