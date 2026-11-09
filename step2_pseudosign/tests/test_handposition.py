import unittest
from hamparse_py3.handposition import getHandposition

# Shared HamNoSys patterns from Sarah's hamparse.py
between = chr(0xE0E6)

repetitions = "[" + "".join(
    chr(cp) for cp in range(0xE0D8, 0xE0DD)
) + "]"

contact = "[" + "".join(
    chr(cp) for cp in range(0xE0D0, 0xE0D6)
) + "]"

alternating = chr(0xE0DD)

speeds = "[" + chr(0xE0C8) + chr(0xE0C9) + "]"


class TestHandposition(unittest.TestCase):
    
    def test_basic_handposition(self):
        """Test 1: Extract finger direction and palm orientation."""

        # U+E020: finger direction
        # U+E038: palm orientation
        hamnosys = chr(0xE020) + chr(0xE038)

        expected = [hamnosys]

        result = getHandposition(
            hamnosys, between, repetitions,
            contact, alternating, speeds
        )

        self.assertEqual(result, expected)


    def test_all_finger_directions(self):
        """Test 2: Extract all 18 basic finger directions."""

        # Keep palm orientation constant.
        palm_orientation = chr(0xE038)

        for cp in range(0xE020, 0xE032):
            with self.subTest(finger_direction=f"U+{cp:04X}"):

                hamnosys = chr(cp) + palm_orientation
                expected = [hamnosys]

                result = getHandposition(
                    hamnosys, between, repetitions,
                    contact, alternating, speeds
                )

                self.assertEqual(result, expected)


    def test_all_palm_orientations(self):
        """Test 3: Extract all 8 basic palm orientations."""

        # Keep finger direction constant.
        finger_direction = chr(0xE020)

        for cp in range(0xE038, 0xE040):
            with self.subTest(palm_orientation=f"U+{cp:04X}"):

                hamnosys = finger_direction + chr(cp)
                expected = [hamnosys]

                result = getHandposition(
                    hamnosys, between, repetitions,
                    contact, alternating, speeds
                )

                self.assertEqual(result, expected)

    def test_real_sign_ab_1a(self):
        """Test 4: Extract HP from the real DSGS sign AB_1A."""

        codepoints = [
            0xE002, 0xE00D, 0xE010,
            0xE029, 0xE03C,
            0xE051, 0xE059,
            0xE084, 0xE0C8
        ]

        hamnosys = "".join(chr(cp) for cp in codepoints)

        # Expected HP: finger direction + palm orientation.
        expected = [chr(0xE029) + chr(0xE03C)]

        result = getHandposition(
            hamnosys, between, repetitions,
            contact, alternating, speeds
        )

        self.assertEqual(result, expected)

    def test_real_sign_aathal_1a(self):
        """Test 5: Inspect HP extraction from AATHAL_1A."""

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

        result = getHandposition(
            hamnosys, between, repetitions,
            contact, alternating, speeds
        )

        # Preserve the observed extraction of all three HP components.
        # The third component contains only a palm orientation.
        expected = [
            chr(0xE020) + chr(0xE03C),
            chr(0xE029) + chr(0xE03E),
            chr(0xE03F)
        ]

        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()