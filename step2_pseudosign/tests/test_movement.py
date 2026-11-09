
import unittest
from hamparse_py3.movement import getMovement

# Shared HamNoSys patterns used by Sarah's parser.
between = chr(0xE0E6)

sizes = "[" + chr(0xE0C6) + chr(0xE0C7) + "]"
speeds = "[" + chr(0xE0C8) + chr(0xE0C9) + "]"

repetitions = "[" + "".join(
    chr(cp) for cp in range(0xE0D8, 0xE0DD)
) + "]"

contact = "[" + "".join(
    chr(cp) for cp in range(0xE0D0, 0xE0D6)
) + "]"


class TestMovement(unittest.TestCase):

    def test_all_primary_path_movements(self):
        """Test 1: Extract all 36 primary PM symbols."""

        # 18 straight + 18 circular movement symbols.
        pm_primary = range(0xE080, 0xE0A4)

        for cp in pm_primary:
            with self.subTest(symbol=f"U+{cp:04X}"):
                hamnosys = chr(cp)
                expected = [chr(cp)]

                result = getMovement(
                    hamnosys, between, sizes, speeds,
                    repetitions, contact
                )

                self.assertEqual(result, expected)

    def test_all_internal_movements(self):
        """Test 2: Extract all 7 Step 1 IM symbols."""

        # IM categories defined in Step 1.
        im_all = [
            0xE0A4,  # Fingerplay
            0xE0A5,  # Nodding
            0xE0A6,  # Swinging
            0xE0A7,  # Twisting
            0xE0A8,  # Stir clockwise
            0xE0A9,  # Stir counter-clockwise
            0xE0AA,  # Replace handshape/orientation
        ]

        for cp in im_all:
            with self.subTest(symbol=f"U+{cp:04X}"):
                hamnosys = chr(cp)
                expected = [chr(cp)]

                result = getMovement(
                    hamnosys, between, sizes, speeds,
                    repetitions, contact
                )

                self.assertEqual(result, expected)


    def test_movement_with_modifiers(self):
        """Test 3: Preserve size and speed modifiers."""

        # Downward movement + small size + fast speed.
        hamnosys = "".join(chr(cp) for cp in [
            0xE084, 0xE0C6, 0xE0C8
        ])

        # All three symbols should stay in one movement.
        expected = [hamnosys]

        result = getMovement(
            hamnosys, between, sizes, speeds,
            repetitions, contact
        )

        self.assertEqual(result, expected)


    def test_parallel_pm_im_structure(self):
        """Test 4: Check extraction of parallel PM and IM."""

        # Parallel begin + PM + IM + parallel end.
        hamnosys = "".join(chr(cp) for cp in [
            0xE0E2, 0xE084, 0xE0A4, 0xE0E3
        ])

        result = getMovement(
            hamnosys, between, sizes, speeds,
            repetitions, contact
        )

        # Both movement symbols must be extracted.
        extracted = "".join(result)
        self.assertIn(chr(0xE084), extracted)
        self.assertIn(chr(0xE0A4), extracted)

        # Parallel boundaries must also be preserved.
        self.assertIn(chr(0xE0E2), extracted)
        self.assertIn(chr(0xE0E3), extracted)

    
    def test_parallel_vs_nonparallel(self):
        """Test 5: Compare parallel and non-parallel PM+IM."""

        # PM and IM inside a parallel structure.
        parallel = "".join(chr(cp) for cp in [
            0xE0E2, 0xE084, 0xE0A4, 0xE0E3
        ])

        # The same movements without parallel markers.
        nonparallel = "".join(chr(cp) for cp in [
            0xE084, 0xE0A4
        ])

        parallel_result = getMovement(
            parallel, between, sizes, speeds,
            repetitions, contact
        )

        nonparallel_result = getMovement(
            nonparallel, between, sizes, speeds,
            repetitions, contact
        )

        # Check whether the parser loses this distinction.
        self.assertEqual(parallel_result, nonparallel_result)

    
    def test_real_cc_bleistift(self):
        """Test 6: Inspect movement extraction from BLEISTIFT_1A."""

        codepoints = [
            0xE006, 0xE020, 0xE03D, 0xE050,
            0xE0E2, 0xE082, 0xE0C6, 0xE0A6, 0xE0E3
        ]
        hamnosys = "".join(chr(cp) for cp in codepoints)

        result = getMovement(
            hamnosys, between, sizes, speeds,
            repetitions, contact
        )

        expected_movements = "".join(chr(cp) for cp in [
            0xE082, 0xE0C6, 0xE0A6
        ])

        extracted = "".join(result)

        # Check movement content independently.
        self.assertEqual(extracted, expected_movements)

        # Inspect whether the parallel structure is preserved.
        print("\nBLEISTIFT_1A extracted MOV:")
        for i, item in enumerate(result, start=1):
            print(
                f"MOV {i}:",
                [f"U+{ord(c):04X}" for c in item]
            )


    def test_real_cc_bestellen(self):
        """Test 7: Inspect replacement movement in BESTELLEN_1A."""

        codepoints = [
            0xE0E9, 0xE004, 0xE00D, 0xE020,
            0xE03E, 0xE051, 0xE0E2, 0xE090,
            0xE0AA, 0xE029, 0xE0E3
        ]
        hamnosys = "".join(chr(cp) for cp in codepoints)

        result = getMovement(
            hamnosys, between, sizes, speeds,
            repetitions, contact
        )

        extracted = "".join(result)

        # Verify the path movement is extracted.
        self.assertIn(chr(0xE090), extracted)

        # Inspect the complete extraction.
        print("\nBESTELLEN_1A extracted MOV:")
        for i, item in enumerate(result, start=1):
            print(
                f"MOV {i}:",
                [f"U+{ord(c):04X}" for c in item]
            )

        # The original sign contains a replacement marker.
        self.assertIn(chr(0xE0AA), hamnosys)



if __name__ == "__main__":
    unittest.main()
