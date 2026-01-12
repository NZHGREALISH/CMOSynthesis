from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .ast import And, Node, Not, Or, Var
from .tokenizer import Token, tokenize


class ParseError(SyntaxError):
    pass


@dataclass
class _TokenStream:
    tokens: List[Token]
    i: int = 0

    def peek(self) -> Optional[Token]:
        if self.i >= len(self.tokens):
            return None
        return self.tokens[self.i]

    def pop(self) -> Token:
        tok = self.peek()
        if tok is None:
            raise ParseError("Unexpected end of input")
        self.i += 1
        return tok

    def match(self, typ: str) -> bool:
        tok = self.peek()
        if tok is None or tok.type != typ:
            return False
        self.i += 1
        return True

    def expect(self, typ: str) -> Token:
        tok = self.peek()
        if tok is None:
            raise ParseError(f"Expected {typ} but got end of input")
        if tok.type != typ:
            raise ParseError(f"Expected {typ} but got {tok.type} at {tok.pos}")
        self.i += 1
        return tok


def parse(text: str) -> Node:
    stream = _TokenStream(tokenize(text))
    expr = _parse_or(stream)
    if stream.peek() is not None:
        tok = stream.peek()
        raise ParseError(f"Unexpected token {tok.type} at {tok.pos}")
    return expr


def _parse_or(stream: _TokenStream) -> Node:
    left = _parse_and(stream)
    while stream.match("OR"):
        right = _parse_and(stream)
        left = Or(left, right)
    return left


def _parse_and(stream: _TokenStream) -> Node:
    left = _parse_not(stream)
    while stream.match("AND"):
        right = _parse_not(stream)
        left = And(left, right)
    return left


def _parse_not(stream: _TokenStream) -> Node:
    if stream.match("NOT"):
        return Not(_parse_not(stream))
    return _parse_atom(stream)


def _parse_atom(stream: _TokenStream) -> Node:
    tok = stream.peek()
    if tok is None:
        raise ParseError("Expected expression but got end of input")

    if stream.match("LPAREN"):
        expr = _parse_or(stream)
        stream.expect("RPAREN")
        return expr

    if tok.type == "VAR":
        stream.pop()
        return Var(tok.value or "")

    raise ParseError(f"Expected VAR or '(' but got {tok.type} at {tok.pos}")
