# Issuer Credit Risk Scoring

**Segment:** Issuer | **Category:** Risk Scoring | **Owner:** Straive Strategic Analytics | **Year:** 2023

## Objective
Dual-stage credit risk framework: application scoring for new accounts and behavioural scoring for portfolio management. Target: predict 90+ DPD within 12 months.

## Methodology
1. Application scorecard — WoE logistic regression with characteristic analysis
2. Behavioural score — XGBoost with monthly refresh
3. Model monitoring: Gini, KS, PSI, characteristic stability
4. Segmentation: Good / Bad / Indeterminate
5. Override and policy rule integration

## Performance
| Model | Gini | KS | PSI (stable <0.1) |
|---|---|---|---|
| Application | 0.68 | 0.51 | 0.04 |
| Behavioural | 0.74 | 0.58 | 0.06 |
