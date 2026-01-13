---
title: Example 3 — De Morgan and “free” inversion
---

# Example 3 — 德摩根律与“哪些取反不需要额外反相器”

静态 CMOS 合成里一个常见误区是：看到 `!A` 就以为一定要做一个反相器。实际上：

- 在 **PDN（NMOS）** 中，实现 `!A` 通常需要 `A̅`（因为 NMOS 要门极=1 才导通）。
- 在 **PUN（PMOS）** 中，实现 `!A` 往往不需要额外反相器（因为 PMOS 门极=0 就导通，直接用 `A` 即可）。

本例用 `F = !(A|B)` 展示这一点。

## 1) 表达式与德摩根

```
F = !(A + B) = !A · !B
```

输入工具：

- `!(A|B)`

工具会把 `nnf` 推到 NNF：

- `nnf: !A&!B`

## 2) 运行一次（Python）

```bash
python - <<'PY'
from bool2cmos.backend.api.synthesize import synthesize
import json

expr = "!(A|B)"
r = synthesize(expr)

print("simplify:", r["steps"]["simplify"]["expr"])
print("nnf:", r["steps"]["nnf"]["expr"])
print("nnfComplement:", r["steps"]["nnfComplement"]["expr"])
print("count:", r["steps"]["count"])
print("pdn:", json.dumps(r["steps"]["pdn"]["network"], indent=2))
print("pun:", json.dumps(r["steps"]["pun"]["network"], indent=2))
PY
```

## 3) 中间结果（工具输出）

- `nnf`: `!A&!B`
- `nnfComplement`: `A|B`

含义：

- PUN 用 `F = !A&!B`
- PDN 用 `F' = A|B`

## 4) PDN / PUN 的 JSON（实际输出）

PDN（对应 `A|B` → 并联）：

```json
{
  "type": "node",
  "kind": "parallel",
  "children": [
    { "type": "transistor", "kind": "nmos", "gate": "A", "gateInverted": false, "onWhen": 1 },
    { "type": "transistor", "kind": "nmos", "gate": "B", "gateInverted": false, "onWhen": 1 }
  ]
}
```

PUN（对应 `!A&!B` → 串联）：

```json
{
  "type": "node",
  "kind": "series",
  "children": [
    { "type": "transistor", "kind": "pmos", "gate": "A", "gateInverted": false, "onWhen": 0 },
    { "type": "transistor", "kind": "pmos", "gate": "B", "gateInverted": false, "onWhen": 0 }
  ]
}
```

注意这里 PUN 里 `!A`/`!B` 的实现：

- 叶子是 `pmos`，且 `gateInverted: false`
- `onWhen: 0` 表示它在 `A=0` 时导通
- 这完全符合 PMOS 的物理特性：**门极电压为 0 时导通**，所以无需额外反相器。

## 5) 晶体管数量

工具输出：

- `pdnTransistors: 2`，`punTransistors: 2`
- `inverterTransistors: 0`
- `totalTransistors: 4`

这就是“取反不一定需要反相器”的典型情况：`!A` 落在 PUN（PMOS）侧时，常常可以直接用原信号实现。
