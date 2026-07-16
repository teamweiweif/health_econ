# SIPP Raw Data 与权重问题台账

审计日期：2026-07-16

## 判定原则

本台账把问题拆成四层：

1. **raw archive**：文件是否来自当前官方远端、是否完整、是否损坏。
2. **official data issue**：Census 自己记录的 processing/correction/comparability 问题。
3. **derived data/code**：本地 Parquet、变量构造和 weight code 是否忠实。
4. **inference/scope**：权重、标准误、attrition 和“全部版本”的边界。

不能因为第一层 PASS 就说所有变量没有问题，也不能因为第三层出现代码错误就误说 Census raw 已损坏。

## 最高优先级

### P0：错误 weight fallback，源码已修、旧输出待重跑

- 原问题：35 个 idea-screen scripts 在 `WPFINWGT<=0` 时错误使用 `TSSSAMT`，再失败则用 1。
- 性质：本地 analysis-code bug，不是 Census raw bug。
- 暴露范围：全 panel 有 13,628 rows 的 `WPFINWGT<=0`；旧代码会给其中 987 rows 一个正的假权重。
- 当前状态：35/35 matching source instances 已移除；现在仅保留正 `WPFINWGT`，非正值为 missing 并被模型 mask 排除。
- 剩余动作：进入论文的历史 idea-screen outputs 必须重跑。ARPA 400% FPL 已完成单独 sensitivity，系数量级几乎不变。

### P0/P1：最终 survey variance 尚未完成

- 当前多数 screen 使用 HC1 或 person-cluster standard errors。
- Census 的正式建议是匹配 `REPWGT1-REPWGT240` 做 Fay modified BRR，`rho=0.5`。
- ARPA corrected screen 的 HC1 `t=-3.779`，但 person-cluster `t=-1.896`。差异本身证明 inference 不能草率锁定。
- 当前状态：**OPEN**。在 Fay-BRR 完成前，不能把 5% significance 当作稳健结论。

## 官方已知数据问题

### 2018-2021 v1.1 income/poverty correction

- 官方修正 `TSSSAMT` Medicare deductions double counting 以及 downstream income/poverty recodes。
- 本地 raw 已是 v1.1。
- 当前 panel 的 32 个 year-variable comparisons 为 32/32 PASS、0 mismatch。
- 状态：**MITIGATED AND VERIFIED**。

### 2018-2023 monthly health-insurance processing error

- 影响 Medicare、Medicaid、other coverage begin/end months 及 downstream monthly recodes。
- 已生成 additive patch，19,625 unique affected person-month rows；原值未覆盖。
- 状态：**MITIGATED WITH PATCH**。

### Health note 中 private recode 公式不一致

- web table 打印的 `EHEMPLY{1:2}=1` 与 dictionary、raw recode 和官方 affected-record 数量级不一致。
- patch 使用 `EPR1MTH/EPR2MTH` 月度 plan indicators，并保存 original/corrected sensitivity。
- 状态：**OPEN DOCUMENTATION INCONSISTENCY**。正式论文必须披露；最好向 Census 请求澄清。

### `RMARKTPLACE` 语义

- `RMARKTPLACE` 不是保险类型；private、Medicaid、other coverage 都可能为 1。
- 状态：**CONFIRMED SCOPE LIMIT**。不得单独命名为纯 nongroup Marketplace enrollment。

## Sampling 与非响应风险

- 2025 cross-sectional weighted household response rate：42.63%。
- FINYR2/3/4 longitudinal person response：61.67% / 42.42% / 25.75%。
- 官方 weights 调整 nonresponse，但不能证明所有非响应偏差都消失。
- 状态：**RESIDUAL HIGH RISK**，尤其 4-year cohort。

## 估计对象与 weight 误用风险

- 月度横截面：目标月的 `WPFINWGT`。
- 年度横截面：先构造年度指标，再限制 `MONTHCODE=12`。
- 连续 2/3/4 年：使用 `FINYR2/3/4` 及对应 eligible cohort。
- 把 12 个 person-month 当 12 个独立年度观察，或用 `WPFINWGT` 声称总体 multi-year longitudinal effect，均不成立。
- 状态：**OPEN FOR EACH MODEL REVIEW**。

## 范围和 provenance 问题

| Issue | 状态 | 解释 |
|---|---|---|
| 50 canonical modern ZIP identity | PASS | 当前官方远端逐字节 50/50 一致 |
| 官方 uniform checksum | 不存在 | 保留项目 SHA-256、CRC 和定期 remote byte comparison |
| Narrative landing page lag | CONFIRMED | direct archive 才是 freshness 核心渠道 |
| 97-column pooled Parquet | SELECTED EXTRACT | 不是 primary raw 全部约 5,000 列 |
| Legacy 1984-2014 heavy raw | NOT DOWNLOADED | 已 catalog 15 panel pages 和 1,413 links |
| 2021 FINYR4 period label | FLAGGED | 官方 metadata 内部标签异常，raw 值未修改 |
| 345 user notes | CATALOGED | 63 个自动 high-priority；每个具体 outcome 锁定前仍需人工定向复核 |

## 当前 Go/No-Go

| 问题 | 判定 |
|---|---|
| 是否需要重新下载 modern 2018-2025 canonical raw？ | **NO**，当前 50/50 与官方一致 |
| 能否直接把 pooled Parquet 当“全部 SIPP raw”？ | **NO**，它是 selected derived extract |
| 能否继续 ARPA 400% FPL 研究？ | **CONDITIONAL GO** |
| 能否宣称主结果已稳健显著？ | **NO**，Fay-BRR 与完整 falsification 尚未完成 |
| 是否已有全部历史 SIPP？ | **NO**，legacy heavy raw 明确未下载 |

机器可读台账：`data/sample_audits/sipp_raw_and_weight_issue_register_20260716.csv`。
