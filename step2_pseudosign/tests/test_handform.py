

import unittest

from hamparse_py3.handform import getHandform


# --- Regex parameters ---

between = chr(0xE0E6)

repetitions = "[" + "".join(
    chr(cp) for cp in range(0xE0D8, 0xE0DD)
) + "]"


class TestHandform(unittest.TestCase):

    def test_base_handshape(self):
        """Test 1: Extract a single base handshape."""

        # U+E000  hamfist -> A (fist)
        hamnosys = chr(0xE000)
        expected = [chr(0xE000)]

        result = getHandform(hamnosys, between, repetitions)

        self.assertEqual(result, expected)

    def test_handshape_with_handposition(self):
        """Test 2: Extract HF without including HP."""

        # U+E000  hamfist
        # U+E020  finger direction
        # U+E038  palm orientation
        hamnosys = "".join([
            chr(0xE000),
            chr(0xE020),
            chr(0xE038)
        ])

        expected = [chr(0xE000)]

        result = getHandform(hamnosys, between, repetitions)

        self.assertEqual(result, expected)

    def test_handshape_with_modifier(self):
        """Test 3: Extract base handshape + modifier."""

        # U+E000  hamfist
        # U+E00C  handshape modifier
        hamnosys = "".join([
            chr(0xE000),
            chr(0xE00C)
        ])

        expected = [chr(0xE000) + chr(0xE00C)]

        result = getHandform(hamnosys, between, repetitions)

        self.assertEqual(result, expected)

    def test_no_handshape(self):
        """Test 4: No handshape should be extracted from HP symbols."""

        # U+E020  finger direction
        # U+E038  palm orientation
        hamnosys = chr(0xE020) + chr(0xE038)

        expected = []

        result = getHandform(hamnosys, between, repetitions)

        self.assertEqual(result, expected)
    

    def test_all_base_handshapes(self):
        """Test 5: Extract all 12 HamNoSys base handshapes."""

        for cp in range(0xE000, 0xE00C):
            with self.subTest(codepoint=f"U+{cp:04X}"):

                hamnosys = chr(cp)
                expected = [chr(cp)]

                result = getHandform(hamnosys, between, repetitions)

                self.assertEqual(result, expected)


    def test_all_handshape_modifiers(self):
        """Test 6: Extract base handshape with each modifier."""

        # Modifier codepoints from Sarah's handform.py
        modifier_cps = [
            0xE00C, 0xE00D, 0xE00E,
            0xE010, 0xE011, 0xE012, 0xE013, 0xE014
        ]

        # U+E000  hamfist -> A (fist)
        base_cp = 0xE000

        for modifier_cp in modifier_cps:
            with self.subTest(modifier=f"U+{modifier_cp:04X}"):

                # Keep the complete HF; complexity uses only the base.
                hamnosys = chr(base_cp) + chr(modifier_cp)
                expected = [hamnosys]

                result = getHandform(hamnosys, between, repetitions)

                self.assertEqual(result, expected)
        
    def test_multiple_handshape_modifiers(self):
        """Test 7: Extract a handshape with multiple modifiers."""

        # U+E000  hamfist -> A (fist)
        # U+E00C, U+E00D  handshape modifiers
        hamnosys = "".join([
            chr(0xE000),
            chr(0xE00C),
            chr(0xE00D)
        ])

        expected = [hamnosys] # expect the full handshape with modifiers to be returned.

        result = getHandform(hamnosys, between, repetitions)

        self.assertEqual(result, expected)


    def test_real_sign_ab_1a(self):
        """Test 8: Extract HF from the real DSGS sign AB_1A."""

        hamnosys = "".join(chr(cp) for cp in [
            0xE002, 0xE00D, 0xE010,
            0xE029, 0xE03C,
            0xE051, 0xE059,
            0xE084, 0xE0C8
        ])

        # Expected full HF: base handshape + two modifiers
        expected = [
            chr(0xE002) + chr(0xE00D) + chr(0xE010)
        ]

        result = getHandform(hamnosys, between, repetitions)

        self.assertEqual(result, expected)

    def test_real_sign_ae_1a_inspection(self):
        """Inspect HF extraction for the real sign Ä_1A."""

        # Real DSGS sign containing a handshape replacement.
        hamnosys = "".join(chr(cp) for cp in [
            0xE000, 0xE00C, 0xE020, 0xE03C,
            0xE051, 0xE059, 0xE0AA, 0xE000, 0xE0D8
        ])

        result = getHandform(hamnosys, between, repetitions)

        # Sarah's parser attaches the repeat-from-start marker to the second HF.
        expected = [
            chr(0xE000) + chr(0xE00C),
            chr(0xE000) + chr(0xE0D8)     # U+E0D8 is a repetition marker, not a handshape modifier.
        ]

        self.assertEqual(result, expected)


    def test_real_sign_aathal_1a_inspection(self):
        """Test 10: Inspect HF extraction from AATHAL_1A."""

        # Full HamNoSys notation from the real DSGS sign.
        codepoints = [
            0xE000, 0xE020, 0xE03C, 0xE051, 0xE059,
            0xE089, 0xE0C6, 0xE0E7, 0xE0E9,
            0xE001, 0xE029, 0xE03E, 0xE051, 0xE059,
            0xE0E6, 0xE052, 0xE059, 0xE0E2,
            0xE085, 0xE0BC, 0xE0C6, 0xE0AA,
            0xE03F, 0xE0E3, 0xE0E2, 0xE06A,
            0xE0E7, 0xE06A, 0xE0E3, 0xE0D1
        ]

        hamnosys = "".join(chr(cp) for cp in codepoints)

        result = getHandform(hamnosys, between, repetitions)

        expected = [
            chr(0xE000),
             chr(0xE001)
        ]

        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
