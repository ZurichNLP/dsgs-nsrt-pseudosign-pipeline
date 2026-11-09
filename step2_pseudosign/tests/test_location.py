
import unittest
from hamparse_py3.location import getLocation

# Shared HamNoSys patterns used by Sarah's parser.
between = chr(0xE0E6)

contact = "[" + "".join(
    chr(cp) for cp in range(0xE0D0, 0xE0D6)
) + "]"

repetitions = "[" + "".join(
    chr(cp) for cp in range(0xE0D8, 0xE0DD)
) + "]"


class TestLocation(unittest.TestCase):
    
    def test_real_sign_ab_1a(self):
        """Test 1: Extract LOC from the real DSGS sign AB_1A."""

        codepoints = [
            0xE002, 0xE00D, 0xE010,
            0xE029, 0xE03C,
            0xE051, 0xE059,
            0xE084, 0xE0C8
        ]

        hamnosys = "".join(chr(cp) for cp in codepoints)

        # Expected location component.
        expected = [chr(0xE051) + chr(0xE059)]

        result = getLocation(
            hamnosys, between, contact, repetitions
        )

        self.assertEqual(result, expected)


    def test_no_location(self):
        """Test 2: Return no LOC when only HF and HP exist."""

        # U+E000: base handshape
        # U+E020: finger direction
        # U+E038: palm orientation
        hamnosys = "".join(chr(cp) for cp in [
            0xE000, 0xE020, 0xE038
        ])

        expected = []

        result = getLocation(
            hamnosys, between, contact, repetitions
        )

        self.assertEqual(result, expected)

    def test_location_with_contact(self):
        """Test 3: Extract a location with a contact marker."""

        # U+E051, U+E059: location symbols
        # U+E0D0: contact-related symbol (hamclose)
        hamnosys = "".join(chr(cp) for cp in [
            0xE051, 0xE059, 0xE0D0
        ])

        expected = [hamnosys]

        result = getLocation(
            hamnosys, between, contact, repetitions
        )

        self.assertEqual(result, expected)

    def test_real_sign_aathal_1a_inspection(self):
        """Test 4: Inspect LOC extraction from AATHAL_1A."""

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

        result = getLocation(
            hamnosys, between, contact, repetitions
        )

        print("\nAATHAL_1A extracted LOC:")
        for i, component in enumerate(result, start=1):
            print(f"LOC {i}:", [f"U+{ord(c):04X}" for c in component])

        # U+E06A occurs twice in the original HamNoSys.
        self.assertEqual(result.count(chr(0xE06A)), 2)

if __name__ == "__main__":
    unittest.main()