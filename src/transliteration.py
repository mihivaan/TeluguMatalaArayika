"""
తెలుగు మాటల అరయిక (TLRE)

Phonetic Transliteration Engine

Version: 0.2.0
Reference Point: RP-007

Deterministic RTS / phonetic transliteration from Latin tokens
to Unicode Telugu script.

Design:
- longest-prefix tokenizer
- abugida-aware state machine parser
- pass-through for whitespace, punctuation, numbers, and
  pre-existing Telugu Unicode
"""

from __future__ import annotations

import sys
from typing import Final


INDEPENDENT_VOWELS: Final[dict[str, str]] = {
    "a": "అ",
    "aa": "ఆ",
    "A": "ఆ",
    "i": "ఇ",
    "ii": "ఈ",
    "I": "ఈ",
    "u": "ఉ",
    "uu": "ఊ",
    "U": "ఊ",
    "~ru": "ఋ",
    "~ri": "ఋ",
    "~ruu": "ౠ",
    "~rU": "ౠ",
    "~lu": "ఌ",
    "~luu": "ౡ",
    "e": "ఎ",
    "ee": "ఏ",
    "E": "ఏ",
    "ai": "ఐ",
    "o": "ఒ",
    "oo": "ఓ",
    "O": "ఓ",
    "au": "ఔ",
}

MATRAS: Final[dict[str, str]] = {
    "a": "",
    "aa": "ా",
    "A": "ా",
    "i": "ి",
    "ii": "ీ",
    "I": "ీ",
    "u": "ు",
    "uu": "ూ",
    "U": "ూ",
    "~ru": "ృ",
    "~ri": "ృ",
    "~ruu": "ౄ",
    "~rU": "ౄ",
    "~lu": "ౢ",
    "~luu": "ౣ",
    "e": "ె",
    "ee": "ే",
    "E": "ే",
    "ai": "ై",
    "o": "ొ",
    "oo": "ో",
    "O": "ో",
    "au": "ౌ",
    "ae": "ాే",
    "AE": "ాే",
    "Ae": "ాే",
    "aE": "ాే",
    "~ae": "ాె",
}

CONSONANTS: Final[dict[str, str]] = {
    # Gutturals
    "k": "క",
    "kh": "ఖ",
    "g": "గ",
    "gh": "ఘ",
    "nG": "ఙ",
    # Palatals
    "c": "చ",
    "ch": "చ",
    "chh": "ఛ",
    "j": "జ",
    "jh": "ఝ",
    "nY": "ఞ",
    "ts": "ౘ",
    "dz": "ౙ",
    # Retroflexes
    "T": "ట",
    "Th": "ఠ",
    "D": "డ",
    "Dh": "ఢ",
    "N": "ణ",
    # Dentals
    "t": "త",
    "th": "థ",
    "d": "ద",
    "dh": "ధ",
    "n": "న",
    # Labials
    "p": "ప",
    "ph": "ఫ",
    "b": "బ",
    "bh": "భ",
    "m": "మ",
    # Foreign / nukta-style combinations
    "f": "ప఼",
    "z": "జ఼",
    # Semivowels & liquids
    "y": "య",
    "r": "ర",
    "l": "ల",
    "v": "వ",
    "w": "వ",
    # Sibilants & aspirate
    "sh": "శ",
    "Sh": "ష",
    "shh": "ష",
    "s": "స",
    "h": "హ",
    "L": "ళ",
    # Classical / historical
    "R": "ఱ",
    "rr": "ఱ",
    "zh": "ఴ",
    "~tra": "ౚ",
    "~tta": "ౚ",
    "~tr": "ౚ",
    "~tt": "ౚ",
}

SPECIAL_SIGNS: Final[dict[str, str]] = {
    # Canonical anusvara token is uppercase M to avoid collision with consonant m.
    "M": "ం",
    # Ara-sunna / candrabindu
    "~m": "ఁ",
    "@": "ఁ",
    "~n": "ఁ",
    # Visarga
    "H": "ః",
    # Standalone nukta and avagraha
    "~q": "఼",
    "~a": "ఽ",
    # Reserved / historical markers
    "r^": "౯",
    "n^": "ౝ",
    # Virama / halant
    ".": "్",
    "~": "్",
}

VIRAMA: Final[str] = "్"

_TOKEN_KEYS: Final[tuple[str, ...]] = tuple(
    sorted(
        set(
            [
                *INDEPENDENT_VOWELS.keys(),
                *MATRAS.keys(),
                *CONSONANTS.keys(),
                *SPECIAL_SIGNS.keys(),
            ]
        ),
        key=lambda token: (-len(token), token),
    )
)

_MAX_TOKEN_LENGTH: Final[int] = max((len(token) for token in _TOKEN_KEYS), default=1)


def tokenize(text: str) -> list[str]:
    """
    Split the input into the longest possible matching phonetic tokens.

    Unrecognized characters are preserved as single-character tokens so they can
    pass through unchanged in the parser.
    """
    tokens: list[str] = []
    i = 0
    n = len(text)

    while i < n:
        matched = None

        for length in range(_MAX_TOKEN_LENGTH, 0, -1):
            if i + length > n:
                continue
            candidate = text[i : i + length]
            if candidate in INDEPENDENT_VOWELS or candidate in MATRAS or candidate in CONSONANTS or candidate in SPECIAL_SIGNS:
                matched = candidate
                break

        if matched is None:
            tokens.append(text[i])
            i += 1
        else:
            tokens.append(matched)
            i += len(matched)

    return tokens


def parse_tokens(tokens: list[str]) -> str:
    """
    Convert token stream to Unicode Telugu using a state machine.

    Rules:
    - Pending consonant tracks the current abugida base.
    - Vowels apply as matras when a consonant is pending.
    - Consonants stack using VIRAMA when another consonant follows.
    - Whitespace / punctuation / unknown characters flush a pending consonant
      with implicit అ and pass through unchanged.
    """
    out: list[str] = []
    pending_consonant: str | None = None

    def flush_pending(with_virama: bool = False) -> None:
        nonlocal pending_consonant
        if pending_consonant is None:
            return
        out.append(pending_consonant + (VIRAMA if with_virama else ""))
        pending_consonant = None

    for token in tokens:
        if token in INDEPENDENT_VOWELS:
            if pending_consonant is not None:
                out.append(pending_consonant + MATRAS[token])
                pending_consonant = None
            else:
                out.append(INDEPENDENT_VOWELS[token])
            continue

        if token in CONSONANTS:
            if pending_consonant is not None:
                flush_pending(with_virama=True)
            pending_consonant = CONSONANTS[token]
            continue

        if token in SPECIAL_SIGNS:
            sign = SPECIAL_SIGNS[token]

            if token in {".", "~"}:
                if pending_consonant is not None:
                    flush_pending(with_virama=True)
                else:
                    out.append(sign)
                continue

            if token == "n^":
                if pending_consonant is not None:
                    flush_pending(with_virama=False)
                out.append(sign)
                continue

            if pending_consonant is not None:
                out.append(pending_consonant + sign)
                pending_consonant = None
            else:
                out.append(sign)
            continue

        # Pass-through for whitespace, punctuation, numbers, and pre-existing Telugu text.
        if pending_consonant is not None:
            flush_pending(with_virama=False)
        out.append(token)

    if pending_consonant is not None:
        flush_pending(with_virama=False)

    return "".join(out)


def rts_to_telugu(text: str) -> str:
    """
    Public transliteration entry point.
    """
    if not text:
        return ""
    return parse_tokens(tokenize(text))


def main() -> None:
    """
    Standalone test runner.
    """
    samples = [
        "telugu",
        "gaaDida",
        "aDa~mgu",
        "saruDu",
        "saMskRta",
        "ksha",
    ]

    for sample in samples:
        print(f"{sample} -> {rts_to_telugu(sample)}")


if __name__ == "__main__":
    main()