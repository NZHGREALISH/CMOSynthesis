---
title: Example 4 — Factoring optimization (AB+AC)
---

# Example 4 — 因式分解：`AB + AC → A(B + C)`

同一个逻辑函数，用不同写法会影响“串并结构”的形态。工具里会做一轮因式分解（`steps.factor` / `steps.factorComplement`），用于减少网络复杂度。

本例展示一个经典变形：

```
F = AB + AC = A(B + C)
```

## 1) 输入与输出对照

把 `F` 写成 SOP（两项相加）：

- 输入：`AB+AC`（隐式 AND + `+` 表示 OR）

工具的因式分解阶段会给出：

- `factor: A(B+C)`

## 2) 运行一次（Python）

```bash
python - <<'PY'
from bool2cmos.backend.api.synthesize import synthesize
import json

expr = "AB+AC"
r = synthesize(expr)

print("parse:", r["steps"]["parse"]["expr"])
print("simplify:", r["steps"]["simplify"]["expr"])
print("nnf:", r["steps"]["nnf"]["expr"])
print("nnfComplement:", r["steps"]["nnfComplement"]["expr"])
print("factor:", r["steps"]["factor"]["expr"])
print("factorComplement:", r["steps"]["factorComplement"]["expr"])
print("count:", r["steps"]["count"])
print("pdn:", json.dumps(r["steps"]["pdn"]["network"], indent=2))
print("pun:", json.dumps(r["steps"]["pun"]["network"], indent=2))
PY
```

工具输出（核心部分）：

- `factor: A(B+C)`
- `factorComplement: !A+!B!C`

## 3) 结构直觉：为什么因式分解“更像电路”

把 `AB + AC` 直接按 SOP 读，会得到两条并联支路，每条两级串联。

而 `A(B+C)` 读起来更像：

- 先经过 `A`（一只晶体管）
- 再在 `B` 与 `C` 之间并联分流

这在很多情况下能减少“重复的 A”带来的结构冗余。

在本项目里，PDN/PUN 的构建会优先使用 `factor` / `factorComplement`，所以即便你输入 `AB+AC`，最终网络也会体现 `A(B+C)` 的结构。

## 4) 晶体管数量（本工具的结果）

对 `AB+AC`，工具输出：

- `pdnTransistors: 3`
- `punTransistors: 3`
- `inverterTransistors: 6`（`A/B/C` 都需要反相信号参与某一侧网络）
- `totalTransistors: 12`

（如果没有做因式分解，直觉上很容易画成“4 管一侧 + 4 管另一侧”的更大网络；本例用来说明工具为什么要做 factoring。）

## 5) PDN / PUN 的 JSON（实际输出）

这里 `factorComplement = !A+!B!C`，因此 PDN 的结构会非常直观：

- `OR` → 并联：`!A` 与 `(!B!C)` 两支并联
- `!B!C` 是 `AND` → 串联

PDN：

```json
{
  "type": "node",
  "kind": "parallel",
  "children": [
    { "type": "transistor", "kind": "nmos", "gate": "A", "gateInverted": true, "onWhen": 0 },
    {
      "type": "node",
      "kind": "series",
      "children": [
        { "type": "transistor", "kind": "nmos", "gate": "B", "gateInverted": true, "onWhen": 0 },
        { "type": "transistor", "kind": "nmos", "gate": "C", "gateInverted": true, "onWhen": 0 }
      ]
    }
  ]
}
```

PUN（对应 `factor = A(B+C)`，即 `A` 串联 `(B|C)` 并联）：

```json
{
  "type": "node",
  "kind": "series",
  "children": [
    { "type": "transistor", "kind": "pmos", "gate": "A", "gateInverted": true, "onWhen": 1 },
    {
      "type": "node",
      "kind": "parallel",
      "children": [
        { "type": "transistor", "kind": "pmos", "gate": "B", "gateInverted": true, "onWhen": 1 },
        { "type": "transistor", "kind": "pmos", "gate": "C", "gateInverted": true, "onWhen": 1 }
      ]
    }
  ]
}
```

