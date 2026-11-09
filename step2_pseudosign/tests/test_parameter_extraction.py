
import unittest

from parameter_extraction import tokenize_hamnosys


class TestParameterExtraction(unittest.TestCase):

    def test_preserve_all_symbols(self):
        """Test 1: Preserve all original symbols."""

        codepoints = [
            0xE0E2, 0xE090, 0xE0AA, 0xE029, 0xE0E3
        ]

        hamnosys = "".join(chr(cp) for cp in codepoints)

        result = tokenize_hamnosys(hamnosys)

        reconstructed = "".join(
            token["symbol"] for token in result
        )

        self.assertEqual(len(result), 5)
        self.assertEqual(reconstructed, hamnosys)

    def test_preserve_symbol_positions(self):
        """Test 2: Preserve exact symbol positions."""

        codepoints = [
            0xE006, 0xE020, 0xE082, 0xE0A6
        ]

        hamnosys = "".join(chr(cp) for cp in codepoints)

        result = tokenize_hamnosys(hamnosys)

        actual_positions = [
            token["index"] for token in result
        ]

        actual_codepoints = [
            token["codepoint"] for token in result
        ]

        self.assertEqual(actual_positions, [0, 1, 2, 3])

        self.assertEqual(
            actual_codepoints,
            ["U+E006", "U+E020", "U+E082", "U+E0A6"]
        )


if __name__ == "__main__":
    unittest.main()
