
"""
Structure-aware HamNoSys parameter extraction.

Preserve original symbols and their positions before
extracting HF, HP, LOC, and MOV components.
"""


def tokenize_hamnosys(hamnosys):
    """Return each HamNoSys symbol with its original position."""

    tokens = []

    for i, symbol in enumerate(hamnosys):

        token = {
            "index": i,
            "symbol": symbol,
            "codepoint": f"U+{ord(symbol):04X}"
        }

        tokens.append(token)

    return tokens



if __name__ == "__main__":

    sample = "".join(chr(cp) for cp in [
        0xE0E2, 0xE090, 0xE0AA, 0xE029, 0xE0E3
    ])

    result = tokenize_hamnosys(sample)

    for token in result:
        print(token["index"], token["codepoint"])
