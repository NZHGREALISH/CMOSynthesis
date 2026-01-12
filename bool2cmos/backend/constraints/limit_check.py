from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LimitCheckResult:
    ok: bool
    limit: int
    total: int
    message: str | None = None
    suggestion: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "limit": self.limit,
            "total": self.total,
            "message": self.message,
            "suggestion": self.suggestion,
        }


def check_transistor_limit(
    total_transistors: int,
    *,
    limit: int = 100,
    on_exceed: str = "raise",
) -> LimitCheckResult:
    """
    Enforces a hard limit on transistor count.

    If exceeded:
      - on_exceed="raise": raises ValueError
      - on_exceed="return": returns a LimitCheckResult with a suggestion
    """

    if limit <= 0:
        raise ValueError("limit must be > 0")
    if total_transistors < 0:
        raise ValueError("total_transistors must be >= 0")
    if on_exceed not in {"raise", "return"}:
        raise ValueError('on_exceed must be "raise" or "return"')

    if total_transistors <= limit:
        return LimitCheckResult(ok=True, limit=limit, total=total_transistors)

    message = f"Transistor limit exceeded: {total_transistors} > {limit}"
    suggestion = (
        "Consider splitting the boolean expression into smaller sub-expressions "
        "and synthesizing each block separately (auto-splitting can be added later)."
    )

    if on_exceed == "raise":
        raise ValueError(f"{message}. {suggestion}")

    return LimitCheckResult(
        ok=False,
        limit=limit,
        total=total_transistors,
        message=message,
        suggestion=suggestion,
    )
