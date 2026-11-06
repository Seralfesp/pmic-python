import ast
from pathlib import Path
import unittest

from nidcpower_channel_ganging import SweepType, generate_sequence


class DecadeLinearTests(unittest.TestCase):
    def test_round_number_points(self):
        expected = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 2.0]
        self.assertEqual(generate_sequence(SweepType.DecadeLinear, 0.1, 2.0, 10), expected)
        self.assertEqual(
            generate_sequence(SweepType.DecadeLinear, -0.1, -2.0, 10),
            [-value for value in expected],
        )

    def test_higher_density(self):
        values = generate_sequence(SweepType.DecadeLinear, 0.1, 2.0, 100)
        expected = [index / 100 for index in range(10, 100)]
        expected += [index / 10 for index in range(10, 21)]
        self.assertEqual(values, expected)
        self.assertEqual(len(values), 101)

    def test_arbitrary_endpoints(self):
        self.assertEqual(
            generate_sequence(SweepType.DecadeLinear, 0.15, 2.35, 10),
            [0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 2.0, 2.35],
        )
        self.assertEqual(
            generate_sequence(SweepType.DecadeLinear, 0.15, 2.35, 10, False),
            [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 2.0],
        )

    def test_decade_boundaries(self):
        values = generate_sequence(SweepType.DecadeLinear, 0.01, 100, 10)
        self.assertEqual(len(values), 37)
        self.assertEqual(len(set(values)), len(values))
        self.assertTrue(all(a < b for a, b in zip(values, values[1:])))
        for boundary in (0.01, 0.1, 1, 10, 100):
            self.assertEqual(values.count(boundary), 1)

    def test_equal_endpoints_and_nonpositive_steps(self):
        self.assertEqual(generate_sequence(SweepType.DecadeLinear, 0.2, 0.2, 10), [0.2])
        self.assertEqual(generate_sequence(SweepType.DecadeLinear, 0.2, 0.2, 10, False), [])
        for steps in (0, -1):
            self.assertEqual(generate_sequence(SweepType.DecadeLinear, 0.1, 2, steps), [])

    def test_invalid_endpoints(self):
        for start, stop in ((0, 2), (1, 0), (-1, 2), (2, 1), (-2, -1),
                            (float("nan"), 2), (1, float("inf"))):
            with self.subTest(start=start, stop=stop):
                with self.assertRaises(ValueError):
                    generate_sequence(SweepType.DecadeLinear, start, stop, 10)

    def test_load_sweep_type_mapping(self):
        tree = ast.parse(Path(__file__).with_name("measurement.py").read_text())
        measure = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                       and node.name == "measure")
        configuration = next(node for node in measure.body if isinstance(node, ast.Try)).body[0]
        for name, expected in (("Linear", SweepType.Linear),
                               ("Logarithmic", SweepType.Logarithmic),
                               ("Decade-linear", SweepType.DecadeLinear),
                               ("DECADE-LINEAR", SweepType.DecadeLinear)):
            namespace = {"SweepType": SweepType, "load_sweep_type": name,
                         "load_sweep_type_enum": SweepType.Linear}
            exec(compile(ast.Module(body=[configuration], type_ignores=[]), "mapping", "exec"),
                 namespace)
            self.assertEqual(namespace["load_sweep_type_enum"], expected)


if __name__ == "__main__":
    unittest.main()
