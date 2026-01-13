---
title: Example 2 — 3-input Majority
---

# Example 2 — 3 输入多数函数（Majority）

多数函数（3 输入）定义为：三路输入里至少有两路为 1，则输出为 1。

一个标准的和项之和（SOP）写法：

```
F = AB + AC + BC
```

在工具语法里可以写成：

- `A&B|A&C|B&C`
- 或 `AB+AC+BC`（`+` 表示 OR，`AB` 代表隐式 AND）

本文以下用显式写法 `A&B|A&C|B&C`。

## 1) 运行一次（Python）

```bash
python - <<'PY'
from bool2cmos.backend.api.synthesize import synthesize
import json

expr = "A&B|A&C|B&C"
r = synthesize(expr)

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

## 2) 中间结果（工具输出）

- `simplify`: `A&B|A&C|B&C`
- `nnf`: `A&B|A&C|B&C`（SOP 本身已是 NNF）
- `nnfComplement`: `(!A|!B)&(!A|!C)&(!B|!C)`

直观解释 `F'`：

- `F` 代表“至少两路为 1”
- 所以 `F'` 代表“至少两路为 0”
- 这正对应上面三个括号：`(!A|!B)` 表示 `A=0 或 B=0`，三个括号一起 `AND` 则等价于“至少两路为 0”

## 3) PDN/PUN 网络结构直觉

因为 PDN 由 `F'` 构建：

- `F'` 是 3 个括号的 `AND`：所以 PDN 是 **3 段串联**；
- 每个括号是 `OR`：所以每段内部是 **2 个 NMOS 并联**（分别对应 `!A`/`!B`、`!A`/`!C`、`!B`/`!C`）。

PUN 由 `F` 构建：

- `F` 是 3 个与项的 `OR`：所以 PUN 是 **3 条并联支路**；
- 每条支路是 `AND`：所以支路内部是 **2 个 PMOS 串联**（对应 `A&B`、`A&C`、`B&C`）。

## 4) PDN / PUN 的 JSON（实际输出）

PDN：

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
        { "type": "transistor", "kind": "nmos", "gate": "B", "gateInverted": true, "onWhen": 0 }
      ]
    },
    {
      "type": "node",
      "kind": "parallel",
      "children": [
        { "type": "transistor", "kind": "nmos", "gate": "A", "gateInverted": true, "onWhen": 0 },
        { "type": "transistor", "kind": "nmos", "gate": "C", "gateInverted": true, "onWhen": 0 }
      ]
    },
    {
      "type": "node",
      "kind": "parallel",
      "children": [
        { "type": "transistor", "kind": "nmos", "gate": "B", "gateInverted": true, "onWhen": 0 },
        { "type": "transistor", "kind": "nmos", "gate": "C", "gateInverted": true, "onWhen": 0 }
      ]
    }
  ]
}
```

PUN：

```json
{
  "type": "node",
  "kind": "parallel",
  "children": [
    {
      "type": "node",
      "kind": "series",
      "children": [
        { "type": "transistor", "kind": "pmos", "gate": "A", "gateInverted": true, "onWhen": 1 },
        { "type": "transistor", "kind": "pmos", "gate": "B", "gateInverted": true, "onWhen": 1 }
      ]
    },
    {
      "type": "node",
      "kind": "series",
      "children": [
        { "type": "transistor", "kind": "pmos", "gate": "A", "gateInverted": true, "onWhen": 1 },
        { "type": "transistor", "kind": "pmos", "gate": "C", "gateInverted": true, "onWhen": 1 }
      ]
    },
    {
      "type": "node",
      "kind": "series",
      "children": [
        { "type": "transistor", "kind": "pmos", "gate": "B", "gateInverted": true, "onWhen": 1 },
        { "type": "transistor", "kind": "pmos", "gate": "C", "gateInverted": true, "onWhen": 1 }
      ]
    }
  ]
}
```

## 5) 晶体管数量（含反相器）

工具给出的计数：

- `pdnTransistors: 6`，`punTransistors: 6`
- `inverterTransistors: 6`（需要 `A̅/B̅/C̅`）
- `totalTransistors: 18`

为什么这里“明明表达式没有 `!A`”也需要反相器？

- 因为 **PDN 必须实现 `F'`**，而 `F'` 里出现了 `!A,!B,!C`；
- 同时 **PUN 实现 `F`**，里面又需要正向的 `A,B,C`；
- 最终电路需要同时具备 `A` 与 `A̅`，所以要为每个输入生成一对 CMOS 反相器（2 个晶体管/反相器）。
