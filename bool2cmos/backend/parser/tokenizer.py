from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True, slots=True)
class Token:
    type: str
    value: Optional[str] = None
    pos: int = 0

    def __repr__(self) -> str:
        if self.value is None:
            return f"Token({self.type})"
        return f"Token({self.type},{self.value!r})"


KEYWORDS = {
    "AND": "AND",
    "OR": "OR",
    "NOT": "NOT",
}

SYMBOLS = {
    "&": "AND",
    "|": "OR",
    "~": "NOT",
    "!": "NOT",
    "(": "LPAREN",
    ")": "RPAREN",
}


def tokenize(text: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0

    while i < len(text):
        ch = text[i]

        if ch.isspace():
            i += 1
            continue

        if ch in SYMBOLS:
            tokens.append(Token(SYMBOLS[ch], pos=i))
            i += 1
            continue

        if ch.isalpha():
            start = i
            while i < len(text) and text[i].isalpha():
                i += 1
            word = text[start:i].upper()

            if word in KEYWORDS:
                tokens.append(Token(KEYWORDS[word], pos=start))
                continue

            if len(word) == 1 and "A" <= word <= "Z":
                tokens.append(Token("VAR", value=word, pos=start))
                continue

            raise SyntaxError(f"Unexpected identifier {text[start:i]!r} at {start}")

        raise SyntaxError(f"Unexpected character {ch!r} at {i}")

    return tokens
