---
title: Example 7 — Constants and simplification
---

# Example 7 — 常量与化简：为什么会出现“0 晶体管”

工具会做基本的代数化简与常量折叠；有些表达式会直接化成常量 `0/1`，这意味着不需要任何 PUN/PDN 网络。

## 1) 典型恒等式/互补律

```
A + !A = 1
A · !A = 0
A + 0 = A
A · 1 = A
```

## 2) 运行一次（Python）

```bash
python - <<'PY'
from bool2cmos.backend.api.synthesize import synthesize

tests = [
    "A|!A",
    "A&!A",
    "A|0",
    "A&1",
    "(A|B)&0",
    "(A|B)&1",
]

for expr in tests:
    r = synthesize(expr)
    print(expr, "=> simplify:", r["steps"]["simplify"]["expr"], "count:", r["steps"]["count"])
PY
```

你会看到类似结果：

- `A|!A => simplify: 1`，且 `totalTransistors: 0`
- `A&!A => simplify: 0`，且 `totalTransistors: 0`

对于不会化成常量、但会化成更小表达式的情况（例如 `A|0` 或 `A&1`）：

- `A|0 => simplify: A`
- `A&1 => simplify: A`

## 3) 一个最小非平凡例子：`F = A`

`F=A` 看起来简单，但静态 CMOS 需要同时提供：

- PUN：在 `A=1` 时拉高输出
- PDN：在 `A=0` 时拉低输出

因此工具会报告需要 `A̅`（让 PMOS/NMOS 在目标条件下导通），最终计数为 `totalTransistors: 4`（1 NMOS + 1 PMOS + 1 个输入反相器）。

你可以这样查看：

```bash
python - <<'PY'
from bool2cmos.backend.api.synthesize import synthesize
import json

r = synthesize("A")
print("count:", r["steps"]["count"])
print("pdn:", json.dumps(r["steps"]["pdn"]["network"], indent=2))
print("pun:", json.dumps(r["steps"]["pun"]["network"], indent=2))
PY
```

## 4) “0 晶体管”在工程上意味着什么

这里的“0 晶体管”是指：对纯组合逻辑网络部分（PUN/PDN + 输入反相器）不需要新增晶体管。

在真实电路里，输出如果要稳定为常 1/常 0，通常仍会涉及供电/接地的连接方式或上一级驱动，但从“由布尔式合成静态 CMOS 网络”的角度，合成结果确实可以为空网络。
