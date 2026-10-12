"""
HamNoSys codepoint dictionary generator.

Parses the official hamnosys.dtx source file (Schulder & Hanke 2022,
CTAN v1.0.3, DOI 10.25592/uhhfdm.9901) and produces categorized
Python dictionaries for classification tasks.

The base codepoint -> symbol name -> section mapping
is extracted verbatim from the .dtx source. 
Sub-categorization within the Movement and Other-symbols sections (PM vs IM vs modifier, brackets etc.)
is based on symbol names + HamNoSys 4.0 User Guide (Robert Smith 2013)
Chapter 7 + Mann et al. (2010) operational definitions. 
"""

import re, json
from pathlib import Path

# Default path: look for hamnosys.dtx in the same folder as this script,
# regardless of where python is being run from.
DEFAULT_DTX_PATH = Path(__file__).parent / 'hamnosys.dtx'


def parse_dtx(path=DEFAULT_DTX_PATH):
    """Extract {section_name: [(symbol_name, codepoint), ...]} from .dtx."""
    text = Path(path).read_text()
    impl = text[text.find('% \\section{Implementation}'):]
    subsec = re.compile(r'%\s*\\subsubsection\{\s*([^}]+?)\s*\}')
    decl   = re.compile(r'\\DeclareTextCommand\{\\(ham\w+)\}\{TU\}\{'
                        r'\\texthamnosys\{\\char\s+"([0-9A-Fa-f]+)\}\}')
    matches = list(subsec.finditer(impl))
    sections = {}
    for i, m in enumerate(matches):
        name = m.group(1).strip()
        start, end = m.end(), (matches[i+1].start() if i+1 < len(matches) else len(impl))
        pairs = [(n, int(cp, 16)) for n, cp in decl.findall(impl[start:end])]
        if pairs:
            sections[name] = pairs
    return sections


if __name__ == '__main__':
    sections = parse_dtx()
    print(f"Parsed {sum(len(v) for v in sections.values())} symbols across {len(sections)} sections")