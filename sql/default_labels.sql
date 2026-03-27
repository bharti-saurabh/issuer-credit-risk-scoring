-- Default Label Generation — 90+ DPD Outcome Window
-- Straive Strategic Analytics | Credit Risk Practice

WITH dpd_events AS (
    SELECT account_id,
        MAX(days_past_due)                                      AS max_dpd_12m,
        MAX(CASE WHEN days_past_due >= 90 THEN 1 ELSE 0 END)   AS reached_90dpd
    FROM fact_delinquency_events
    WHERE event_date BETWEEN :obs_date AND :obs_date + INTERVAL '12 months'
    GROUP BY account_id
),

cured AS (
    -- Account cured if it returned to current status after being 90+DPD
    SELECT account_id, 1 AS cured_flag
    FROM fact_delinquency_events
    WHERE days_past_due = 0
      AND event_date > (
          SELECT MIN(event_date) FROM fact_delinquency_events de2
          WHERE de2.account_id = fact_delinquency_events.account_id
            AND de2.days_past_due >= 90
            AND de2.event_date BETWEEN :obs_date AND :obs_date + INTERVAL '12 months'
      )
)

SELECT
    pop.account_id,
    :obs_date                                                   AS observation_date,
    :obs_date + INTERVAL '12 months'                            AS outcome_date,
    COALESCE(d.max_dpd_12m, 0)                                 AS max_dpd,
    COALESCE(d.reached_90dpd, 0)                               AS ever_90dpd,
    CASE
        WHEN d.reached_90dpd = 1 AND c.cured_flag IS NULL  THEN 'Bad'
        WHEN d.reached_90dpd = 1 AND c.cured_flag = 1      THEN 'Indeterminate'
        WHEN d.reached_90dpd IS NULL OR d.reached_90dpd = 0 THEN 'Good'
    END                                                         AS performance_label
FROM stg_scoring_population pop
LEFT JOIN dpd_events d ON pop.account_id = d.account_id
LEFT JOIN cured c      ON pop.account_id = c.account_id
