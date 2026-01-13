---
title: Example 1 — F = A·B + C
---

# Example 1 — `F = (A & B) | C`

这个例子对应文件名里的 “ab_or_c”：当 `A` 与 `B` 同为 1 **或** `C=1` 时，输出为 1。

## 1) 表达式写法（等价）

以下写法都等价：

- 显式 AND/OR：`A&B|C`
- 也可以写成：`(A&B)|C`（括号可读性更强）
- 如果你喜欢 `+` 表示 OR：`A&B+C`
- 隐式 AND（注意解析规则，详见 `example8_shorthand_identifiers.md`）：`AB+C`

本文以下用 `A&B|C`。

## 2) 用 Python 跑一次（可复制）

```bash
python - <<'PY'
from bool2cmos.backend.api.synthesize import synthesize
import json

expr = "A&B|C"
r = synthesize(expr)

print("parse:", r["steps"]["parse"]["expr"])
print("simplify:", r["steps"]["simplify"]["expr"])
print("complement:", r["steps"]["complement"]["expr"])
print("nnf:", r["steps"]["nnf"]["expr"])
print("nnfComplement:", r["steps"]["nnfComplement"]["expr"])
print("factor:", r["steps"]["factor"]["expr"])
print("factorComplement:", r["steps"]["factorComplement"]["expr"])
print("count:", r["steps"]["count"])
print("pdn:", json.dumps(r["steps"]["pdn"]["network"], indent=2))
print("pun:", json.dumps(r["steps"]["pun"]["network"], indent=2))
PY
```

## 3) 关键中间结果（工具输出）

对 `F = A&B|C`：

- `simplify`: `A&B|C`（本例不需要进一步代数化简）
- `nnf`: `A&B|C`（已是 NNF）
- `nnfComplement`: `(!A|!B)&!C`

解释一下 `F'`：

```
F' = !(A·B + C)
   = !(A·B) · !C
   = (!A + !B) · !C
```

这一步非常重要：**PDN 是由 `F'` 构建的**（导通时输出被拉到 0）。

## 4) 从表达式到 PDN/PUN（结构直觉）

这里用“串并结构”描述网络：

- **PDN (NMOS)** 使用 `F' = (!A|!B)&!C`
  - `AND` → 串联：`(... ) & !C` 变成“先走 `(... )` 再走 `!C`”
  - `OR` → 并联：`(!A|!B)` 变成“`!A` 与 `!B` 两条并联支路”
- **PUN (PMOS)** 使用 `F = (A&B)|C`
  - `OR` → 并联：`(A&B)` 与 `C` 两条并联支路
  - `AND` → 串联：`A` 与 `B` 串联

## 5) PDN / PUN 的 JSON（实际输出）

PDN（由 `F'` 构建）：

```json
{
  "type": "node",
  "kind": "series",
  "children": [
    {
      "type": "node",
      "kind": "parallel",
      "children": [
        {
          "type": "transistor",
          "kind": "nmos",
          "gate": "A",
          "gateInverted": true,
          "onWhen": 0
        },
        {
          "type": "transistor",
          "kind": "nmos",
          "gate": "B",
          "gateInverted": true,
          "onWhen": 0
        }
      ]
    },
    {
      "type": "transistor",
      "kind": "nmos",
      "gate": "C",
      "gateInverted": true,
      "onWhen": 0
    }
  ]
}
```

PUN（由 `F` 构建）：

```json
{
  "type": "node",
  "kind": "parallel",
  "children": [
    {
      "type": "node",
      "kind": "series",
      "children": [
        {
          "type": "transistor",
          "kind": "pmos",
          "gate": "A",
          "gateInverted": true,
          "onWhen": 1
        },
        {
          "type": "transistor",
          "kind": "pmos",
          "gate": "B",
          "gateInverted": true,
          "onWhen": 1
        }
      ]
    },
    {
      "type": "transistor",
      "kind": "pmos",
      "gate": "C",
      "gateInverted": true,
      "onWhen": 1
    }
  ]
}
```

### 如何读 `gateInverted` / `onWhen`

以 PDN 的 `!A` 为例：

- NMOS 在“门极=1”时导通，但我们希望它在 “A=0” 时导通（因为是 `!A`）。
- 因此需要一个反相信号 `A̅` 去驱动门极：这就是 `gateInverted: true`。
- 从“原始 A 值”的角度看，它在 `A=0` 时导通：这就是 `onWhen: 0`。

类似地，在 PUN 中：

- PMOS 在“门极=0”时导通。
- 若叶子是正文字面量 `A`（希望 `A=1` 时导通），就需要用 `A̅` 把门极拉低：所以也会出现 `gateInverted: true, onWhen: 1`。

## 6) 晶体管数量（含输入反相器）

本例工具输出的计数是：

- `pdnTransistors: 3`（网络里 3 个 NMOS）
- `punTransistors: 3`（网络里 3 个 PMOS）
- `inverterTransistors: 6`（为 `A/B/C` 各生成一个输入反相器，共 3 个反相器，每个 2 个晶体管）
- `totalTransistors: 12`

`invertedInputs: ['A', 'B', 'C']` 表示最终网络需要同时使用 `A` 与 `A̅`（或等价的“门极需要反相信号”）。
