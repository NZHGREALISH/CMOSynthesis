---
title: Example 5 — XOR (A⊕B)
---

# Example 5 — XOR：`A ⊕ B`

项目语法不直接支持 `^`，所以 XOR 通常写成：

```
F = A⊕B = A·!B + !A·B
```

对应输入：

- `A&!B|!A&B`

## 1) 运行一次（Python）

```bash
python - <<'PY'
from bool2cmos.backend.api.synthesize import synthesize
import json

expr = "A&!B|!A&B"
r = synthesize(expr)

print("simplify:", r["steps"]["simplify"]["expr"])
print("nnf:", r["steps"]["nnf"]["expr"])
print("nnfComplement:", r["steps"]["nnfComplement"]["expr"])
print("count:", r["steps"]["count"])
print("pdn:", json.dumps(r["steps"]["pdn"]["network"], indent=2))
print("pun:", json.dumps(r["steps"]["pun"]["network"], indent=2))
PY
```

工具输出（关键）：

- `simplify`: `!A&B|!B&A`（会做一些交换/规范化，但逻辑等价）
- `nnfComplement`: `(!A|B)&(!B|A)`
- `count.totalTransistors: 12`
- `invertedInputs: ['A', 'B']`（需要 `A̅`/`B̅`）

## 2) XOR 为什么“贵”

与 `AND/OR` 相比，XOR 的 SOP/NNF 往往会同时用到正负文字面量：

- PUN 实现 `F` 时要表达 “A=1 且 B=0” 以及 “A=0 且 B=1”
- PDN 实现 `F'` 时同样需要混合条件

因此通常需要输入反相器来同时提供 `A`/`A̅`、`B`/`B̅`，也会带来更多串并结构节点。

## 3) PDN / PUN 的 JSON（实际输出）

PDN（实现 `F' = (!A|B)&(!B|A)`，因此是两段串联、每段两个并联）：

```json
{
  "type": "node",
  "kind": "series",
  "children": [
    {
      "type": "node",
      "kind": "parallel",
      "children": [
        { "type": "transistor", "kind": "nmos", "gate": "A", "gateInverted": true, "onWhen": 0 },
        { "type": "transistor", "kind": "nmos", "gate": "B", "gateInverted": false, "onWhen": 1 }
      ]
    },
    {
      "type": "node",
      "kind": "parallel",
      "children": [
        { "type": "transistor", "kind": "nmos", "gate": "B", "gateInverted": true, "onWhen": 0 },
        { "type": "transistor", "kind": "nmos", "gate": "A", "gateInverted": false, "onWhen": 1 }
      ]
    }
  ]
}
```

PUN（实现 `F = (!A&B)|(!B&A)`，因此是两条并联支路，每条两级串联）：

```json
{
  "type": "node",
  "kind": "parallel",
  "children": [
    {
      "type": "node",
      "kind": "series",
      "children": [
        { "type": "transistor", "kind": "pmos", "gate": "A", "gateInverted": false, "onWhen": 0 },
        { "type": "transistor", "kind": "pmos", "gate": "B", "gateInverted": true, "onWhen": 1 }
      ]
    },
    {
      "type": "node",
      "kind": "series",
      "children": [
        { "type": "transistor", "kind": "pmos", "gate": "B", "gateInverted": false, "onWhen": 0 },
        { "type": "transistor", "kind": "pmos", "gate": "A", "gateInverted": true, "onWhen": 1 }
      ]
    }
  ]
}
```

