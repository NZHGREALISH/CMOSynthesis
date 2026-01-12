import unittest

from bool2cmos.backend.api.synthesize import inspect_complement_nnf, synthesize


class TestShorthand(unittest.TestCase):
    def test_implicit_and_roundtrip(self):
        out = synthesize("AB")
        self.assertEqual(out["steps"]["parse"]["expr"], "AB")
        self.assertEqual(out["steps"]["simplify"]["expr"], "AB")

    def test_plus_or_roundtrip(self):
        out = synthesize("A+B")
        self.assertEqual(out["steps"]["parse"]["expr"], "A+B")
        self.assertEqual(out["steps"]["simplify"]["expr"], "A+B")
        # User typed shorthand OR (+) and no explicit AND, so ANDs should render implicitly.
        self.assertEqual(out["steps"]["nnfComplement"]["expr"], "!A!B")

    def test_explicit_ops_roundtrip(self):
        out = synthesize("A&(B|!C)")
        self.assertEqual(out["steps"]["parse"]["expr"], "A&(B|!C)")

    def test_debug_exposes_complement_nnf(self):
        out = inspect_complement_nnf("A+B")
        self.assertIn("nnfComplement", out["steps"])
        self.assertIn("nnf", out["steps"])
        self.assertIn("checks", out)


if __name__ == "__main__":
    unittest.main()
