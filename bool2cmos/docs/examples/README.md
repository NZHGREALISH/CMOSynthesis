# Examples (bool2cmos)

本目录给出一些“从布尔表达式 → 静态 CMOS(PUN/PDN)”的完整例子，尽量把每一步的中间结果（化简、NNF/补 NNF、因式分解、网络结构与晶体管数量）都写清楚，方便对照代码与前端可视化。

## 快速运行（Python）

在仓库根目录：

```bash
python - <<'PY'
from bool2cmos.backend.api.synthesize import synthesize
import json

expr = "A&B|C"
r = synthesize(expr)
print("simplify:", r["steps"]["simplify"]["expr"])
print("nnf:", r["steps"]["nnf"]["expr"])
print("nnfComplement:", r["steps"]["nnfComplement"]["expr"])
print("count:", r["steps"]["count"])
print("pdn:", json.dumps(r["steps"]["pdn"]["network"], indent=2))
print("pun:", json.dumps(r["steps"]["pun"]["network"], indent=2))
PY
```

## 快速运行（API / curl）

先启动后端（参考根目录 `README.md`），然后：

```bash
curl -sS -X POST http://localhost:8000/synthesize \
  -H 'content-type: application/json' \
  -d '{"expr":"A&B|C"}' | python -m json.tool
```

## 输出里几个关键概念

- `steps.parse/simplify/nnf/.../factor`：各阶段表达式（用与你输入一致的运算符风格渲染）。
- `PDN`（NMOS 下拉网络）：导通条件对应 **F=0**，因此 PDN 实际上由 **F 的补函数 F'** 构建。
- `PUN`（PMOS 上拉网络）：导通条件对应 **F=1**，PUN 由 **F 本身** 构建。
- `series / parallel`：
  - **PDN**：`AND` → 串联（series），`OR` → 并联（parallel）。
  - **PUN**：`AND` → 串联（series），`OR` → 并联（parallel）。但注意 PUN 用的是 F，本质上实现“拉高条件”。
- 叶子节点（`type: transistor`）字段：
  - `kind`: `nmos` / `pmos`
  - `gate`: 门极接到的“变量名”
  - `gateInverted`: 是否需要额外反相器来得到该门极信号（比如 PMOS 想在输入=1 时导通，需要用输入的反相信号驱动门极）
  - `onWhen`: 该晶体管在**原始变量值**为 `0` 或 `1` 时导通（结合 `gateInverted` 一起理解最清楚）

## 目录内容

- `example1_ab_or_c.md`：`F = A·B + C` 的完整链路（含 PDN/PUN JSON）。
- `example2_majority.md`：3 输入多数函数 `F = AB + AC + BC`（多数门）。
- `example3_de_morgan.md`：德摩根 + “为什么某些取反不需要额外反相器”。
- `example4_factoring_optimization.md`：因式分解如何减少网络结构（例如 `AB+AC → A(B+C)`）。
- `example5_xor.md`：XOR 的经典展开式与代价（反相器/晶体管数）。
- `example6_mux2to1.md`：2:1 MUX：`F = S·D1 + !S·D0`。
- `example7_constants_and_simplification.md`：常量折叠、互补律（`A+!A=1` 等）与“0 晶体管”结果。
- `example8_shorthand_identifiers.md`：输入语法细节与常见坑（`AB` 代表 `A&B`、变量命名规则等）。

