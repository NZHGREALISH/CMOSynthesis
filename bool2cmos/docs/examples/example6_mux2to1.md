---
title: Example 6 — 2:1 MUX
---

# Example 6 — 2:1 多路选择器（MUX）

2:1 MUX 的布尔表达式（选择信号 `S`，数据 `D0/D1`）：

```
F = S·D1 + !S·D0
```

对应输入：

- `S&D1|!S&D0`

## 1) 运行一次（Python）

```bash
python - <<'PY'
from bool2cmos.backend.api.synthesize import synthesize

expr = "S&D1|!S&D0"
r = synthesize(expr)

print("simplify:", r["steps"]["simplify"]["expr"])
print("nnf:", r["steps"]["nnf"]["expr"])
print("nnfComplement:", r["steps"]["nnfComplement"]["expr"])
print("count:", r["steps"]["count"])
PY
```

工具输出（关键）：

- `simplify`: `!S&D0|D1&S`
- `nnfComplement`: `(!D0|S)&(!D1|!S)`
- `count.totalTransistors: 14`
- `invertedInputs: ['D0', 'D1', 'S']`

## 2) 解释：为什么 D0/D1 也会出现在 invertedInputs

直觉上 MUX 只有 `S` 需要取反，但在静态 CMOS 合成里：

- PDN 要实现 `F'`（哪些情况把输出拉到 0）
- `F'` 的形式里往往会出现 `!D0` 或 `!D1` 这样的文字面量（见上面的 `nnfComplement`）

因此如果你以“纯组合逻辑”角度看没有显式 `!D0`，工具仍可能在某一侧网络里需要 `D0̅`/`D1̅`。

## 3) PDN / PUN 的 JSON（实际输出）

PDN（实现 `F' = (!D0|S)&(!D1|!S)`）：

```json
{
  "type": "node",
  "kind": "series",
  "children": [
    {
      "type": "node",
      "kind": "parallel",
      "children": [
        { "type": "transistor", "kind": "nmos", "gate": "D0", "gateInverted": true, "onWhen": 0 },
        { "type": "transistor", "kind": "nmos", "gate": "S", "gateInverted": false, "onWhen": 1 }
      ]
    },
    {
      "type": "node",
      "kind": "parallel",
      "children": [
        { "type": "transistor", "kind": "nmos", "gate": "D1", "gateInverted": true, "onWhen": 0 },
        { "type": "transistor", "kind": "nmos", "gate": "S", "gateInverted": true, "onWhen": 0 }
      ]
    }
  ]
}
```

PUN（实现 `F = (!S&D0)|(D1&S)`）：

```json
{
  "type": "node",
  "kind": "parallel",
  "children": [
    {
      "type": "node",
      "kind": "series",
      "children": [
        { "type": "transistor", "kind": "pmos", "gate": "S", "gateInverted": false, "onWhen": 0 },
        { "type": "transistor", "kind": "pmos", "gate": "D0", "gateInverted": true, "onWhen": 1 }
      ]
    },
    {
      "type": "node",
      "kind": "series",
      "children": [
        { "type": "transistor", "kind": "pmos", "gate": "D1", "gateInverted": true, "onWhen": 1 },
        { "type": "transistor", "kind": "pmos", "gate": "S", "gateInverted": true, "onWhen": 1 }
      ]
    }
  ]
}
```

