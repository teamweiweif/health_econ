# SIPP 官方来源、版本、权重与 Raw Data 二次全面审计

审计日期：2026-07-16

## 一句话结论

**现代版 SIPP 2018-2025 raw archive 通过真实性与完整性复核；用于正式推断则是 CONDITIONAL PASS。**

- 本地 50 个 canonical CSV ZIP 与 Census 当前官方远端逐字节一致，合计比较 7,537,185,902 bytes。
- 2018-2021 已是当前修订版 v1.1；2022-2025 是当前 v1.0。
- primary、年度 replicate、2/3/4 年 longitudinal weight 及对应 replicate 产品均已覆盖。
- raw ZIP 未被解压后重打包、改写或替换；Parquet 和 correction patch 都是单独的衍生文件。
- 这不是全部历史 SIPP。1984-2014 legacy panel/wave 只完成官方目录与 1,413 个链接的 metadata catalog，没有下载历史 heavy raw。
- 正式论文仍需处理官方医保 user note、正确选择 point weight、使用 240 个 replicate weights 做 Fay-BRR，并正视纵向 attrition。

## 1. “版本”必须区分四个概念

1. **年度 public-use file**：2018、2019、...、2025 SIPP。每个文件按访谈/数据收集年份命名，但主要回顾前一自然年。例如 2025 SIPP 覆盖 2024 年 1-12 月。
2. **同一年度文件里的 overlapping panels**：2025 文件合并 2022 Panel Wave 4、2023 Panel Wave 3、2024 Panel Wave 2 和 2025 Panel Wave 1。它不是一个单独“横截面 panel”。
3. **纵向估计产品**：`FINYR2`、`FINYR3`、`FINYR4` 及匹配 replicate files，用于连续 2、3、4 年 cohort。
4. **legacy panels**：1984-1993、1996、2001、2004、2008、2014 的旧 panel/wave 系统，文件结构和现代 2018+ annual overlapping-panel redesign 不同。

因此，现代年度文件既提供月度 person records，也可在正确权重下支持某一月份的横截面估计、年度估计和特定连续年度的纵向估计。不能简单称为“现在只有横截面版本”。

## 2. 官方渠道再核实

本次没有只依赖一个网页入口，而是同时核实以下 Census 官方层级：

| 官方层级 | 用途 | 本次发现 |
|---|---|---|
| [SIPP datasets landing page](https://www.census.gov/programs-surveys/sipp/data/datasets.html) | 人工导航 | 页面更新可能慢于 direct archive |
| `https://www2.census.gov/programs-surveys/sipp/data/datasets/{year}/` | raw file source of record | 实时重爬 2018-2025，共 371 个目录条目 |
| [Technical documentation](https://www.census.gov/programs-surveys/sipp/tech-documentation.html) | guide、dictionary、release notes、source/accuracy | 当前 2025 文档在 direct technical directories 中可得 |
| [User notes](https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes.html) | 官方已知错误和解释限制 | 2018-2025 共抓取并归档 345 个 note pages |
| [2025 Users Guide](https://www2.census.gov/programs-surveys/sipp/tech-documentation/methodology/2025_SIPP_Users_Guide.pdf) | 设计、panel、权重使用 | 本地 PDF 与官方当前 bytes 一致 |
| [2025 Source and Accuracy Statement](https://www2.census.gov/programs-surveys/sipp/tech-documentation/source-accuracy-statements/2025/SIPP-2025-SA.pdf) | response、attrition、variance | 本地 PDF 与官方当前 bytes 一致 |

关键经验：在本次最终网页检查时，datasets landing page 已列出 2025，并明确其覆盖 2024 年；但 Users' Guide、Source and Accuracy、complete technical documentation 等导航页仍停在 2024，而 direct `www2.census.gov` archive 已有 2025 release note、Users Guide 和 Source and Accuracy Statement。以后 freshness check 必须同时看 direct directories。

## 3. 当前本地 modern raw 产品矩阵

| 产品类型 | 数量 | 本地状态 |
|---|---:|---|
| Primary public-use CSV ZIP | 8 | 2018-2025 全部下载 |
| Annual/cross-sectional replicate ZIP | 8 | 2018-2025 全部下载 |
| Longitudinal point-weight ZIP | 17 | 所有官方发布的 2/3/4 年产品 |
| Longitudinal replicate-weight ZIP | 17 | 与上述 17 个逐一匹配 |
| **Canonical raw total** | **50** | **50/50** |

年度产品分布：

| File year | Primary | Annual replicate | Longitudinal horizons | Canonical total |
|---|---:|---:|---|---:|
| 2018 | 1 | 1 | 无 | 2 |
| 2019 | 1 | 1 | 2-year | 4 |
| 2020 | 1 | 1 | 2-, 3-year | 6 |
| 2021 | 1 | 1 | 2-, 3-, 4-year | 8 |
| 2022 | 1 | 1 | 2-, 3-year | 6 |
| 2023 | 1 | 1 | 2-, 3-, 4-year | 8 |
| 2024 | 1 | 1 | 2-, 3-, 4-year | 8 |
| 2025 | 1 | 1 | 2-, 3-, 4-year | 8 |

2022 没有 4-year 产品是官方目录事实，不是漏下载。SAS、Stata 和 standalone GZIP 是相同官方产品的替代编码，已 catalog，但没有重复下载；本地 canonical raw 选择官方 pipe-delimited CSV ZIP。

## 4. Raw 身份与完整性检验

本轮实时重新连接官方远端，而不是沿用旧 manifest：

- 8/8 年度 direct directories 抓取成功。
- 50/50 expected canonical products 仍在官方目录中。
- 50/50 本地 size 与当前远端 `Content-Length` 一致。
- 50/50 从第一 byte 到最后一 byte 与当前远端一致。
- 实际比较总量：7,537,185,902 bytes，约 7.020 GiB。
- 50/50 ZIP 可完整读到结尾并通过 CRC。
- ZIP 内 CSV header 与官方 JSON schema 对齐。
- 逐行计数与官方 validation workbook 对齐。
- `.part` 残留为 0。

Census 没有为这些产品统一发布 cryptographic checksum。本项目的 SHA-256 是项目生成的 provenance，不冒充官方 checksum；“当前远端逐字节比较 + 本地 SHA-256 + ZIP CRC + schema + official row count”是现有最强组合验证。

## 5. Release versions 与官方修订

| File years | 当前版本 | 当前 release note 状态 |
|---|---|---|
| 2018-2021 | v1.1，2025-07-24 更新 | 修正 `TSSSAMT` 中 Medicare B/C/D deduction double counting，并重建依赖的个人/家庭/住户收入和贫困 recodes；2018-2020 另有 `THTOTINCT2` 小修正 |
| 2022-2025 | v1.0 | 当前 release notes 未记录后续 public-use version |

本地 8 份 release-note PDF 均与当前官方远端逐字节一致。更重要的是，当前 analysis-ready panel 中 2018-2021 的 8 个受影响收入/贫困字段，按 4 年逐项回连当前 raw 后为 **32/32 完全对齐、0 mismatch**。所以 v1.1 问题已经在 raw 和当前 panel 两层得到验证，不再只是看文件名推断。

## 6. 权重：什么问题用什么 weight

| 估计目标 | Point weight | 必要行限制/样本 | Replicate source |
|---|---|---|---|
| 某一个月的横截面估计 | `WPFINWGT` | `MONTHCODE` 等于目标月 | 当年 `rwYYYY` 的 `REPWGT1-REPWGT240` |
| 自然年度横截面估计 | `WPFINWGT` | 先构建年度变量，再使用 `MONTHCODE=12` | 当年 `rwYYYY` 的 December replicates |
| 连续 2 年纵向估计 | `FINYR2` | 官方 2-year eligible cohort | 匹配 `lgtrwYYYYyr2` |
| 连续 3 年纵向估计 | `FINYR3` | 官方 3-year eligible cohort | 匹配 `lgtrwYYYYyr3` |
| 连续 4 年纵向估计 | `FINYR4` | 官方 4-year eligible cohort | 匹配 `lgtrwYYYYyr4` |

Annual replicate merge key 是 `SSUID + PNUM + MONTHCODE`；longitudinal replicate merge key 是 `SSUID + PNUM`。官方建议用 Fay modified BRR，`rho=0.5`，MSE 形式：

```text
variance = sum((replicate_estimate - full_sample_estimate)^2) /
           (240 * 0.5^2)
```

不能做的事情：

- 不能把 `TSSSAMT` 当 weight。它是 Social Security income amount。
- 不能把非正 `WPFINWGT` 随意换成 1。
- 不能把每人 12 个月当作 12 个独立年度观察。
- 不能用 `WPFINWGT` 代替 `FINYR2/3/4` 来声称总体连续多年纵向估计。
- 不能只报普通 HC1 标准误就称为最终 SIPP survey inference。

本轮发现的 35 个 idea-screen 脚本中的错误 `TSSSAMT` fallback 已全部移除。现在非正 `WPFINWGT` 设为缺失，并由模型的 `weight > 0` mask 排除。历史结果若要进入论文仍需重新生成。

## 7. 官方 health-insurance user note

Census 官方 note 说明，2018-2023 文件中 Medicare、Medicaid 和 other coverage 的 begin/end month processing 有错误，并影响若干 edited monthly variables 和 downstream recodes。

本项目采取 additive、可逆处理：

- 原 panel 不覆盖、不改写。
- 新增 correction patch，只保存 key、原始值和 note-consistent corrected value。
- patch 覆盖 19,625 个 unique person-month rows、2,983 persons。
- `RHLTHMTH` 的年度修正率约为 0.10%-0.36%，不是大规模重写。
- 7 个源/结果字段在 2018-2023 回连当前 raw 为 42/42 对齐、0 mismatch。

仍有一个必须公开的文档冲突：Census web table 在重建 `RPRIMTH` 时打印 `EHEMPLY{1:2}=1`，但 data dictionary 把 `EHEMPLY` 定义为多类别 source code，照字面执行也与原始 recode 和 note 声称的 affected-record 数量级冲突。本项目采用月度 private-plan indicators `EPR1MTH/EPR2MTH` 来实现相同 begin/end logic，并保留 original-versus-corrected sensitivity。该解释不是冒充 Census 已明确澄清的最终答案。

## 8. Response、nonresponse 与 longitudinal attrition

2025 Source and Accuracy Statement 报告：

- CY2025 file 约 14,000 个 interviewed households / 32,500 eligible households。
- 当前 cross-sectional weighted household response rate：42.63%。
- 2022 Panel Wave 4 cumulative weighted response：13.21%，sample loss 86.79%。
- 2023 Panel Wave 3：19.21%，sample loss 80.79%。
- 2024 Panel Wave 2：22.79%，sample loss 77.21%。
- 2025 Panel Wave 1：35.17%，sample loss 64.83%。
- 纵向 person response：FINYR2 61.67%，FINYR3 42.42%，FINYR4 25.75%。

这些数字不是 raw corruption。官方权重做了 noninterview 和 second-stage adjustments，但低 response 和随 horizon 增强的 attrition 仍是实质性外推风险。论文必须报告所用 horizon、权重和样本留存，并做 2/3/4-year sensitivity，而不能只说“已经加权所以没有偏差”。

## 9. 变量解释边界

- `RMARKTPLACE` 不是保险类型变量。Census 明确说明 private、Medicaid 和 other coverage 都可能被报告为 Marketplace coverage。
- 因此 `RMARKTPLACE=1` 不能单独命名为“nongroup private Marketplace enrollment”。至少应与 `RPRIMTH`、`RPRITYPE2`、`EPRIEXCH*`、`EMDEXCH`、subsidy 和 public coverage variables 交叉构造，并做路径分解。
- 默认 pooled Parquet 有 97 列，其中 90 个是官方 source fields、7 个是 technical/harmonization fields。它是 selected extract，不是约 5,000 列 primary raw 的完整列复制。

## 10. 对 ARPA 400% FPL 题目的实际影响

在相同 3.5-4.5 FPL local-linear difference-in-discontinuities screen 中：

| 数据处理 | `above400 x post` uninsured coefficient | Person-cluster SE | Person-cluster t | N person-months |
|---|---:|---:|---:|---:|
| 旧 weight fallback + 原 health values | -0.026256 | 0.014275 | -1.839 | 217,096 |
| 仅正的官方 `WPFINWGT` | -0.026260 | 0.014275 | -1.840 | 216,811 |
| 正 `WPFINWGT` + health correction | -0.027105 | 0.014294 | -1.896 | 216,857 |

解释：方向与约 2.6-2.7 percentage point 的量级没有被 raw/weight 修正推翻；health correction 使估计略微更负。但 person-cluster `|t|=1.896` 仍低于常用 1.96 门槛，约等于双侧 `p=0.058`。HC1 `t=-3.779` 明显更大，说明 inference choice 非常重要。

因此当前结论是：

- **研究题目：CONDITIONAL GO。**
- **不能写成已经证实 ARPA 因果降低 uninsurance。**
- 下一道硬门槛是 matching 240 replicate weights 的 Fay-BRR inference、placebo thresholds、bandwidth sensitivity、pre-trend/shape diagnostics 和 outcome-definition sensitivity。

## 11. 最终状态分层

| 层面 | 状态 | 含义 |
|---|---|---|
| Modern 2018-2025 raw authenticity | PASS | 50/50 当前官方远端逐字节一致 |
| Modern official product completeness | PASS | canonical CSV 的 8+8+17+17 完整 |
| Release version currency | PASS | 2018-2021 v1.1；2022-2025 v1.0 |
| Derived selected panel provenance | PASS | v1.1 和 health source fields 均回连 raw |
| Health outcome readiness | CONDITIONAL PASS | 需用 additive patch，并披露公式冲突 |
| Weight selection | CONDITIONAL PASS | point-weight 源码已修；旧输出需重跑 |
| Final variance/inference | NOT YET PASS | 尚未完成 Fay-BRR final inference |
| Complete historical SIPP archive | NO | legacy heavy raw 未下载，范围已明示 |

## 12. 核心机器证据

- `data/metadata/sipp_live_official_channel_reaudit_20260716.csv`
- `data/sample_audits/sipp_remote_byte_comparison_20260716.csv`
- `data/sample_audits/sipp_remote_source_reaudit_checks_20260716.csv`
- `data/metadata/sipp_release_version_ledger_2018_2025.csv`
- `data/metadata/sipp_weight_product_use_ledger.csv`
- `data/metadata/sipp_2025_response_and_attrition_summary.csv`
- `data/metadata/sipp_official_user_notes_inventory_2018_2025.csv`
- `data/sample_audits/sipp_v11_correction_panel_alignment.csv`
- `data/sample_audits/sipp_health_insurance_usernote_correction_counts.csv`
- `data/sample_audits/sipp_raw_and_weight_issue_register_20260716.csv`
- `data/sample_audits/sipp_reaudit_final_checks_20260716.csv`
- `report/107_arpa400_raw_data_quality_sensitivity.md`

## 13. 可重复执行

```powershell
python script/01_ingest/07_reaudit_sipp_official_sources.py
python script/01_ingest/08_audit_sipp_versions_weights_user_notes.py
python script/01_ingest/08_audit_sipp_versions_weights_user_notes.py --issues-only
python script/01_ingest/09_audit_panel_alignment_and_health_corrections.py
python script/01_ingest/10_arpa400_raw_data_quality_sensitivity.py
python script/01_ingest/11_verify_sipp_raw_reaudit_outputs.py
```

重新运行第一个命令会再次传输约 7.5 GB，因为它执行逐字节 remote comparison；不应在每次普通模型迭代时运行。

最终独立收口检查结果：**15/15 PASS**。
