from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union


class SynthesisError(ValueError):
    pass


# ---- AST ----


@dataclass(frozen=True, slots=True)
class Var:
    name: str


@dataclass(frozen=True, slots=True)
class Const:
    value: bool


@dataclass(frozen=True, slots=True)
class Not:
    child: "Expr"


@dataclass(frozen=True, slots=True)
class And:
    children: Tuple["Expr", ...]


@dataclass(frozen=True, slots=True)
class Or:
    children: Tuple["Expr", ...]


Expr = Union[Var, Const, Not, And, Or]

@dataclass(frozen=True, slots=True)
class RenderStyle:
    not_op: str = "!"
    and_op: str = "&"
    or_op: str = "|"
    implicit_and: bool = False


def expr_to_str(expr: Expr, style: Optional[RenderStyle] = None) -> str:
    style = style or RenderStyle()

    def prec(e: Expr) -> int:
        if isinstance(e, (Var, Const)):
            return 4
        if isinstance(e, Not):
            return 3
        if isinstance(e, And):
            return 2
        if isinstance(e, Or):
            return 1
        return 0

    def render(e: Expr, parent_prec: int) -> str:
        p = prec(e)
        if isinstance(e, Var):
            s = e.name
        elif isinstance(e, Const):
            s = "1" if e.value else "0"
        elif isinstance(e, Not):
            child = render(e.child, p)
            s = f"{style.not_op}{child}"
        elif isinstance(e, And):
            parts = [render(c, p) for c in e.children]
            if style.implicit_and:
                s = "".join(parts)
            else:
                s = style.and_op.join(parts)
        elif isinstance(e, Or):
            s = style.or_op.join(render(c, p) for c in e.children)
        else:
            raise AssertionError(f"Unknown Expr: {type(e)}")

        if p < parent_prec:
            return f"({s})"
        return s

    return render(expr, 0)


# ---- Parser ----


Token = Tuple[str, str]  # (kind, lexeme)


def _tokenize(text: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch in ("(", ")"):
            tokens.append((ch, ch))
            i += 1
            continue
        if ch in ("!", "~"):
            tokens.append(("NOT", ch))
            i += 1
            continue
        if ch in ("&", "*"):
            tokens.append(("AND", ch))
            i += 1
            continue
        if ch in ("|", "+"):
            tokens.append(("OR", ch))
            i += 1
            continue
        if ch.isdigit():
            if ch not in ("0", "1"):
                raise SynthesisError(f"Only constants 0/1 are supported, got: {ch}")
            tokens.append(("CONST", ch))
            i += 1
            continue
        if ch.isalpha() or ch == "_":
            j = i + 1
            while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                j += 1
            ident = text[i:j]
            upper = ident.upper()
            if upper in ("AND", "OR", "NOT"):
                tokens.append((upper, ident))
            elif ident.isalpha() and len(upper) > 1:
                # Shorthand support: "AB" => "A AND B"
                for c in upper:
                    tokens.append(("IDENT", c))
            else:
                tokens.append(("IDENT", upper))
            i = j
            continue
        raise SynthesisError(f"Unexpected character: {ch!r}")

    # Insert implicit ANDs: A(B+C), AB, A!B, )A, 1A, etc.
    def can_end_expr(kind: str) -> bool:
        return kind in ("IDENT", "CONST", ")")

    def can_start_expr(kind: str) -> bool:
        return kind in ("IDENT", "CONST", "(", "NOT")

    with_implicit: List[Token] = []
    for tok in tokens:
        if with_implicit:
            prev_kind, _ = with_implicit[-1]
            if can_end_expr(prev_kind) and can_start_expr(tok[0]):
                with_implicit.append(("AND", ""))  # inserted
        with_implicit.append(tok)

    with_implicit.append(("EOF", ""))
    return with_implicit


def _detect_style(text: str) -> RenderStyle:
    not_op = "~" if "~" in text else "!"
    or_op = "+" if "+" in text else "|"
    explicit_and = ("&" in text) or ("*" in text)
    implicit_and = False
    if not explicit_and:
        toks = _tokenize(text)
        implicit_and = any(kind == "AND" and lex == "" for kind, lex in toks)
    return RenderStyle(not_op=not_op, and_op="&", or_op=or_op, implicit_and=implicit_and)


class _Parser:
    def __init__(self, tokens: Sequence[Token]):
        self.tokens = tokens
        self.pos = 0

    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _eat(self, kind: str) -> Token:
        tok = self._peek()
        if tok[0] != kind:
            raise SynthesisError(f"Expected {kind}, got {tok[0]} ({tok[1]!r})")
        self.pos += 1
        return tok

    def parse(self) -> Expr:
        expr = self._parse_or()
        if self._peek()[0] != "EOF":
            kind, lex = self._peek()
            raise SynthesisError(f"Unexpected trailing token: {kind} ({lex!r})")
        return expr

    def _parse_or(self) -> Expr:
        left = self._parse_and()
        children = [left]
        while self._peek()[0] == "OR":
            self.pos += 1
            children.append(self._parse_and())
        if len(children) == 1:
            return children[0]
        return Or(tuple(children))

    def _parse_and(self) -> Expr:
        left = self._parse_not()
        children = [left]
        while self._peek()[0] == "AND":
            self.pos += 1
            children.append(self._parse_not())
        if len(children) == 1:
            return children[0]
        return And(tuple(children))

    def _parse_not(self) -> Expr:
        if self._peek()[0] == "NOT":
            self.pos += 1
            return Not(self._parse_not())
        return self._parse_atom()

    def _parse_atom(self) -> Expr:
        kind, lex = self._peek()
        if kind == "(":
            self.pos += 1
            expr = self._parse_or()
            self._eat(")")
            return expr
        if kind == "IDENT":
            self.pos += 1
            return Var(lex)
        if kind == "CONST":
            self.pos += 1
            return Const(lex == "1")
        raise SynthesisError(f"Expected identifier/constant/parenthesized expression, got {kind} ({lex!r})")


def parse_expr(text: str) -> Expr:
    tokens = _tokenize(text)
    return _Parser(tokens).parse()


# ---- Logic transforms ----


def _flatten(op_type: type, items: Iterable[Expr]) -> List[Expr]:
    out: List[Expr] = []
    for item in items:
        if isinstance(item, op_type):
            out.extend(item.children)  # type: ignore[attr-defined]
        else:
            out.append(item)
    return out


def _literal_key(expr: Expr) -> Optional[Tuple[str, bool]]:
    if isinstance(expr, Var):
        return (expr.name, True)
    if isinstance(expr, Not) and isinstance(expr.child, Var):
        return (expr.child.name, False)
    return None


def simplify(expr: Expr) -> Expr:
    if isinstance(expr, (Var, Const)):
        return expr
    if isinstance(expr, Not):
        child = simplify(expr.child)
        if isinstance(child, Const):
            return Const(not child.value)
        if isinstance(child, Not):
            return simplify(child.child)
        return Not(child)
    if isinstance(expr, And):
        children = [simplify(c) for c in _flatten(And, expr.children)]
        # Annihilators / identities
        if any(isinstance(c, Const) and not c.value for c in children):
            return Const(False)
        children = [c for c in children if not (isinstance(c, Const) and c.value)]
        if not children:
            return Const(True)
        # x & !x => 0
        lits: Dict[str, Set[bool]] = {}
        uniq: Dict[Expr, None] = {}
        for c in children:
            key = _literal_key(c)
            if key is not None:
                name, pos = key
                lits.setdefault(name, set()).add(pos)
                if lits[name] == {True, False}:
                    return Const(False)
            uniq[c] = None
        children = list(uniq.keys())
        children.sort(key=expr_to_str)
        if len(children) == 1:
            return children[0]
        return And(tuple(children))
    if isinstance(expr, Or):
        children = [simplify(c) for c in _flatten(Or, expr.children)]
        if any(isinstance(c, Const) and c.value for c in children):
            return Const(True)
        children = [c for c in children if not (isinstance(c, Const) and not c.value)]
        if not children:
            return Const(False)
        # x | !x => 1
        lits: Dict[str, Set[bool]] = {}
        uniq: Dict[Expr, None] = {}
        for c in children:
            key = _literal_key(c)
            if key is not None:
                name, pos = key
                lits.setdefault(name, set()).add(pos)
                if lits[name] == {True, False}:
                    return Const(True)
            uniq[c] = None
        children = list(uniq.keys())
        children.sort(key=expr_to_str)
        if len(children) == 1:
            return children[0]
        return Or(tuple(children))
    raise AssertionError(f"Unknown Expr: {type(expr)}")


def complement(expr: Expr) -> Expr:
    return Not(expr)


def nnf(expr: Expr) -> Expr:
    expr = simplify(expr)

    def push(e: Expr) -> Expr:
        if isinstance(e, (Var, Const)):
            return e
        if isinstance(e, And):
            return simplify(And(tuple(push(c) for c in e.children)))
        if isinstance(e, Or):
            return simplify(Or(tuple(push(c) for c in e.children)))
        if isinstance(e, Not):
            c = simplify(e.child)
            if isinstance(c, Const):
                return Const(not c.value)
            if isinstance(c, Var):
                return Not(c)
            if isinstance(c, Not):
                return push(c.child)
            if isinstance(c, And):
                return simplify(Or(tuple(push(Not(x)) for x in c.children)))
            if isinstance(c, Or):
                return simplify(And(tuple(push(Not(x)) for x in c.children)))
            raise AssertionError(f"Unknown Not child: {type(c)}")
        raise AssertionError(f"Unknown Expr: {type(e)}")

    return push(expr)


def _factor_once(expr: Expr) -> Expr:
    # OR of AND terms: factor common literals: (a&b) | (a&c) => a & (b|c)
    if isinstance(expr, Or):
        terms = [t if isinstance(t, And) else And((t,)) for t in expr.children]
        literal_sets: List[Set[Expr]] = [set(t.children) for t in terms]
        if not literal_sets:
            return expr
        common = set.intersection(*literal_sets)
        if common:
            common_sorted = sorted(common, key=expr_to_str)
            new_terms: List[Expr] = []
            for t in terms:
                rest = [c for c in t.children if c not in common]
                if not rest:
                    new_terms.append(Const(True))
                elif len(rest) == 1:
                    new_terms.append(rest[0])
                else:
                    new_terms.append(And(tuple(sorted(rest, key=expr_to_str))))
            factored = And(
                tuple(common_sorted)
                + (
                    simplify(Or(tuple(sorted(new_terms, key=expr_to_str)))),
                )
            )
            return simplify(factored)
    # AND of OR terms: (a|b) & (a|c) => a | (b&c)
    if isinstance(expr, And):
        terms = [t if isinstance(t, Or) else Or((t,)) for t in expr.children]
        literal_sets = [set(t.children) for t in terms]
        if not literal_sets:
            return expr
        common = set.intersection(*literal_sets)
        if common:
            common_sorted = sorted(common, key=expr_to_str)
            new_terms: List[Expr] = []
            for t in terms:
                rest = [c for c in t.children if c not in common]
                if not rest:
                    new_terms.append(Const(False))
                elif len(rest) == 1:
                    new_terms.append(rest[0])
                else:
                    new_terms.append(Or(tuple(sorted(rest, key=expr_to_str))))
            factored = Or(
                tuple(common_sorted)
                + (
                    simplify(And(tuple(sorted(new_terms, key=expr_to_str)))),
                )
            )
            return simplify(factored)
    return expr


def factor(expr: Expr, max_passes: int = 4) -> Expr:
    expr = simplify(expr)
    for _ in range(max_passes):
        before = expr
        if isinstance(expr, And):
            expr = And(tuple(factor(c, max_passes=0) for c in expr.children))
        elif isinstance(expr, Or):
            expr = Or(tuple(factor(c, max_passes=0) for c in expr.children))
        elif isinstance(expr, Not):
            expr = Not(factor(expr.child, max_passes=0))
        expr = simplify(expr)
        expr = _factor_once(expr)
        expr = simplify(expr)
        if expr == before:
            break
    return expr


# ---- Network representation ----


@dataclass(frozen=True, slots=True)
class Transistor:
    kind: str  # "nmos" | "pmos"
    gate: str
    gate_inverted: bool
    on_when: int  # 0 or 1 (logical requirement for the variable)


@dataclass(frozen=True, slots=True)
class NetworkNode:
    kind: str  # "series" | "parallel"
    children: Tuple["Network", ...]


Network = Union[Transistor, NetworkNode]


def _iter_literals(expr: Expr) -> Iterable[Tuple[str, int]]:
    if isinstance(expr, Var):
        yield (expr.name, 1)
        return
    if isinstance(expr, Not) and isinstance(expr.child, Var):
        yield (expr.child.name, 0)
        return
    raise SynthesisError(f"Expected literal in NNF, got: {expr_to_str(expr)}")


def build_network(expr_nnf: Expr, transistor_kind: str) -> Network:
    if transistor_kind not in ("nmos", "pmos"):
        raise ValueError("transistor_kind must be 'nmos' or 'pmos'")

    def build(e: Expr) -> Network:
        if isinstance(e, Const):
            # For visualization, model constants as empty networks by short-circuiting in caller.
            raise SynthesisError("Cannot build a transistor network directly from a constant.")
        if isinstance(e, Var) or (isinstance(e, Not) and isinstance(e.child, Var)):
            name, required = next(iter(_iter_literals(e)))
            if transistor_kind == "nmos":
                gate_inverted = required == 0
            else:
                gate_inverted = required == 1
            return Transistor(
                kind=transistor_kind,
                gate=name,
                gate_inverted=gate_inverted,
                on_when=required,
            )
        if isinstance(e, And):
            return NetworkNode(kind="series", children=tuple(build(c) for c in e.children))
        if isinstance(e, Or):
            return NetworkNode(kind="parallel", children=tuple(build(c) for c in e.children))
        if isinstance(e, Not):
            raise SynthesisError(f"NNF violation (unexpected NOT): {expr_to_str(e)}")
        raise AssertionError(f"Unknown Expr: {type(e)}")

    expr_nnf = nnf(expr_nnf)
    if isinstance(expr_nnf, Const):
        # A constant function is special: represent as a degenerate network.
        # - PDN true means output always pulled down
        # - PUN true means output always pulled up
        return NetworkNode(kind="parallel", children=tuple())
    return build(expr_nnf)


def _count_transistors(net: Network) -> int:
    if isinstance(net, Transistor):
        return 1
    return sum(_count_transistors(c) for c in net.children)


def _collect_inverted_gates(net: Network) -> Set[str]:
    if isinstance(net, Transistor):
        return {net.gate} if net.gate_inverted else set()
    out: Set[str] = set()
    for c in net.children:
        out |= _collect_inverted_gates(c)
    return out


def export_network_json(net: Network) -> Dict[str, Any]:
    if isinstance(net, Transistor):
        return {
            "type": "transistor",
            "kind": net.kind,
            "gate": net.gate,
            "gateInverted": net.gate_inverted,
            "onWhen": net.on_when,
        }
    return {
        "type": "node",
        "kind": net.kind,
        "children": [export_network_json(c) for c in net.children],
    }


# ---- Pipeline ----


def synthesize(expression: str) -> Dict[str, Any]:
    if not isinstance(expression, str) or not expression.strip():
        raise SynthesisError("Expression must be a non-empty string.")

    style = _detect_style(expression)
    parsed = parse_expr(expression)
    simplified = simplify(parsed)
    comp = complement(simplified)
    nnf_expr = nnf(simplified)
    nnf_comp = nnf(comp)
    factored = factor(nnf_expr)
    factored_comp = factor(nnf_comp)

    pdn = build_network(factored_comp, transistor_kind="nmos")  # conducts when F=0
    pun = build_network(factored, transistor_kind="pmos")  # conducts when F=1

    pdn_transistors = _count_transistors(pdn)
    pun_transistors = _count_transistors(pun)
    inverted_gates = _collect_inverted_gates(pdn) | _collect_inverted_gates(pun)
    inverter_count = 2 * len(inverted_gates)  # CMOS inverter = 2 transistors

    return {
        "input": {
            "expression": expression,
            "style": {
                "not": style.not_op,
                "and": "" if style.implicit_and else style.and_op,
                "or": style.or_op,
            },
        },
        "steps": {
            "parse": {"expr": expr_to_str(parsed, style)},
            "simplify": {"expr": expr_to_str(simplified, style)},
            "complement": {"expr": expr_to_str(comp, style)},
            "nnf": {"expr": expr_to_str(nnf_expr, style)},
            "nnfComplement": {"expr": expr_to_str(nnf_comp, style)},
            "factor": {"expr": expr_to_str(factored, style)},
            "factorComplement": {"expr": expr_to_str(factored_comp, style)},
            "pdn": {"network": export_network_json(pdn)},
            "pun": {"network": export_network_json(pun)},
            "count": {
                "pdnTransistors": pdn_transistors,
                "punTransistors": pun_transistors,
                "inverterTransistors": inverter_count,
                "totalTransistors": pdn_transistors + pun_transistors + inverter_count,
                "invertedInputs": sorted(inverted_gates),
            },
            "export": {"format": "json"},
        },
    }


def inspect_complement_nnf(expression: str) -> Dict[str, Any]:
    if not isinstance(expression, str) or not expression.strip():
        raise SynthesisError("Expression must be a non-empty string.")

    style = _detect_style(expression)
    parsed = parse_expr(expression)
    simplified = simplify(parsed)
    comp = complement(simplified)
    nnf_expr = nnf(simplified)
    nnf_comp = nnf(comp)

    vars_: List[str] = sorted({name for name in _collect_vars(parsed)})
    max_full_vars = 8
    full = len(vars_) <= max_full_vars

    if full:
        rows = []
        for mask in range(1 << len(vars_)):
            env = {vars_[i]: bool((mask >> i) & 1) for i in range(len(vars_))}
            f = _eval(parsed, env)
            nnf_f = _eval(nnf_expr, env)
            nnf_fc = _eval(nnf_comp, env)
            rows.append(
                {
                    "in": {k: int(v) for k, v in env.items()},
                    "f": int(f),
                    "nnfF": int(nnf_f),
                    "nnfNotF": int(nnf_fc),
                }
            )
        checks = {
            "checkedBy": "truthTable",
            "vars": vars_,
            "nnfEquivalent": all(r["f"] == r["nnfF"] for r in rows),
            "nnfComplementEquivalent": all(r["nnfNotF"] == (1 - r["f"]) for r in rows),
        }
    else:
        import random

        samples = 256
        ok_nnf = True
        ok_comp = True
        for _ in range(samples):
            env = {k: bool(random.getrandbits(1)) for k in vars_}
            f = _eval(parsed, env)
            ok_nnf = ok_nnf and (_eval(nnf_expr, env) == f)
            ok_comp = ok_comp and (_eval(nnf_comp, env) == (not f))
        rows = []
        checks = {
            "checkedBy": "random",
            "samples": samples,
            "vars": vars_,
            "nnfEquivalent": ok_nnf,
            "nnfComplementEquivalent": ok_comp,
        }

    return {
        "input": {
            "expression": expression,
            "style": {
                "not": style.not_op,
                "and": "" if style.implicit_and else style.and_op,
                "or": style.or_op,
            },
        },
        "steps": {
            "parse": {"expr": expr_to_str(parsed, style)},
            "simplify": {"expr": expr_to_str(simplified, style)},
            "complement": {"expr": expr_to_str(comp, style)},
            "nnf": {"expr": expr_to_str(nnf_expr, style)},
            "nnfComplement": {"expr": expr_to_str(nnf_comp, style)},
        },
        "checks": checks,
        "truthTable": rows,
    }


def _collect_vars(expr: Expr) -> Iterable[str]:
    if isinstance(expr, Var):
        yield expr.name
    elif isinstance(expr, Const):
        return
    elif isinstance(expr, Not):
        yield from _collect_vars(expr.child)
    elif isinstance(expr, (And, Or)):
        for c in expr.children:
            yield from _collect_vars(c)


def _eval(expr: Expr, env: Dict[str, bool]) -> bool:
    if isinstance(expr, Var):
        try:
            return env[expr.name]
        except KeyError:
            raise SynthesisError(f"Missing variable assignment: {expr.name}")
    if isinstance(expr, Const):
        return expr.value
    if isinstance(expr, Not):
        return not _eval(expr.child, env)
    if isinstance(expr, And):
        out = True
        for c in expr.children:
            out = out and _eval(c, env)
        return out
    if isinstance(expr, Or):
        out = False
        for c in expr.children:
            out = out or _eval(c, env)
        return out
    raise AssertionError(f"Unknown Expr: {type(expr)}")


# ---- Optional FastAPI binding ----


def _try_build_router():
    try:
        from fastapi import APIRouter, HTTPException
        from pydantic import BaseModel
    except Exception:
        return None

    router = APIRouter()

    class SynthesizeRequest(BaseModel):
        expr: str

    @router.post("/synthesize")
    def synthesize_route(payload: SynthesizeRequest) -> Dict[str, Any]:
        try:
            return synthesize(payload.expr)
        except SynthesisError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/debug/nnf")
    def debug_nnf_route(payload: SynthesizeRequest) -> Dict[str, Any]:
        try:
            return inspect_complement_nnf(payload.expr)
        except SynthesisError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return router


router = _try_build_router()


__all__ = [
    "SynthesisError",
    "parse_expr",
    "simplify",
    "complement",
    "nnf",
    "factor",
    "build_network",
    "export_network_json",
    "synthesize",
    "inspect_complement_nnf",
    "router",
]
