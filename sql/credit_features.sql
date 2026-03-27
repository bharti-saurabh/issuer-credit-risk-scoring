-- Credit Feature Extraction — Application and Bureau Features
-- Straive Strategic Analytics | Credit Risk Practice

SELECT
    a.account_id,
    a.application_date                                          AS obs_date,
    -- Bureau features
    cb.bureau_score,
    cb.num_tradelines_total,
    cb.num_tradelines_open,
    cb.revolving_utilisation_bureau,
    cb.months_since_most_recent_delinquency,
    cb.num_inquiries_6m,
    cb.bankrupt_flag,
    cb.total_derogatory_count,
    cb.mortgage_tradeline_flag,
    -- Internal account features
    a.requested_credit_limit,
    a.annual_income_stated,
    a.debt_to_income_ratio,
    a.employment_type,
    a.time_at_address_months,
    a.time_with_employer_months,
    -- Derived
    COALESCE(cb.revolving_utilisation_bureau, 0.5)             AS utilisation_imputed,
    CASE WHEN cb.bankrupt_flag = 1 OR cb.months_since_most_recent_delinquency < 12
         THEN 1 ELSE 0 END                                     AS recent_adverse_flag,
    a.requested_credit_limit / NULLIF(a.annual_income_stated, 0) AS limit_to_income_ratio
FROM dim_accounts a
JOIN fact_credit_bureau cb
    ON a.account_id = cb.account_id
    AND cb.pull_date = a.application_date
WHERE a.application_date BETWEEN :start_date AND :end_date
  AND a.application_decision IN ('APPROVED','DECLINED')        -- full population for scorecard
ORDER BY a.application_date
