---
title: Example 8 — Syntax, shorthand, and identifiers
---

# Example 8 — 输入语法、隐式 AND、变量命名规则

这一页专门讲“怎么写表达式不会被误解”，尤其是隐式 AND 与变量命名。

## 1) 运算符与别名

- NOT：`!A`、`~A`、`NOT A`
- AND：`A&B`、`A*B`、`A AND B`、隐式 `AB` / `A(B+C)` / `A!B`
- OR：`A|B`、`A+B`、`A OR B`
- 常量：`0`、`1`

## 1.1) 优先级（从高到低）

- `!`（NOT）
- `&` / 隐式 AND
- `|` / `+`（OR）

例如 `!A&B|C` 会按 `((!A)&B)|C` 解析；如果你不确定，推荐显式加括号。

## 1.2) 隐式 AND 插入规则（直观版）

解析器会在“一个子表达式结束”和“下一个子表达式开始”之间自动插入 AND，例如：

- `A(B+C)` 视为 `A&(B+C)`
- `AB` 视为 `A&B`
- `A!B` 视为 `A&(!B)`
- `)A`、`1A` 这种也会插入 AND（不常用，但规则一致）

## 2) 重要规则：纯字母多字符 token 会被当成“shorthand AND”

解析器对“纯字母、长度>1 的 token”（例如 `AB`、`SUM`）会当成 shorthand：

- `AB` 会被拆成 `A AND B`
- `SUM` 会被拆成 `S AND U AND M`

这是为了支持教科书式写法 `AB + C`。

如果你真的需要多字符变量名，请用以下方式之一：

- 含数字：`A1`、`SUM0`
- 含下划线：`SUM_BIT`、`carry_in`

## 3) 快速验证（Python）

```bash
python - <<'PY'
from bool2cmos.backend.api.synthesize import synthesize

examples = [
    "AB+C",        # AB 被当成 A&B
    "A_B+C",       # A_B 是一个变量
    "SUM+Cin",     # SUM 被拆成 S&U&M；Cin 也会被拆成 C&I&N（都是纯字母）
    "SUM0+Cin1",   # SUM0/Cin1 作为整体变量
]

for expr in examples:
    r = synthesize(expr)
    print(expr, "=> parse:", r["steps"]["parse"]["expr"])
PY
```

## 4) 建议

- 想用隐式 AND：可以写 `AB+CD` 这类“单字母变量”的教科书写法。
- 想用多字符变量名：务必包含数字/下划线（`A_B`、`DATA0`），否则会被拆开。
- 大多数情况下，建议显式写 `&` / `|`，可读性更强，也更不容易踩坑。
