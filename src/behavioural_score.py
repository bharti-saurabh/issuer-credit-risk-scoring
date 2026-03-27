"""
Behavioural Credit Risk Model — Monthly Refresh Pipeline
Straive Strategic Analytics | Credit Risk Practice
"""
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score
import joblib, logging

log = logging.getLogger(__name__)

FEATURES = [
    "payment_ratio_3m","utilisation_trend","cash_advance_freq_6m",
    "overlimit_count_6m","bureau_score","bureau_score_change_6m",
    "delinquency_days_max_12m","revolving_balance","credit_limit",
    "txn_count_30d","months_since_last_payment","autopay_flag",
]

def compute_psi(expected, actual, bins=10):
    """Population Stability Index — alert if PSI > 0.1."""
    breaks = np.percentile(expected, np.linspace(0,100,bins+1))
    breaks[0], breaks[-1] = -np.inf, np.inf
    exp_pct = np.histogram(expected, breaks)[0] / len(expected)
    act_pct = np.histogram(actual, breaks)[0] / len(actual)
    exp_pct = np.where(exp_pct == 0, 1e-4, exp_pct)
    act_pct = np.where(act_pct == 0, 1e-4, act_pct)
    psi = np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))
    stability = "Stable" if psi < 0.1 else "Monitor" if psi < 0.25 else "ALERT — Rebuild"
    return round(psi, 4), stability

def train(df: pd.DataFrame, target: str = "bad_90dpd_12m", model_out: str = "behav_model.pkl"):
    X, y = df[FEATURES].fillna(0), df[target]
    model = XGBClassifier(n_estimators=350, max_depth=5, learning_rate=0.06,
                          scale_pos_weight=(y==0).sum()/(y==1).sum(),
                          random_state=42, n_jobs=-1, eval_metric="auc")
    model.fit(X, y, verbose=False)
    log.info(f"AUC: {roc_auc_score(y, model.predict_proba(X)[:,1]):.4f}")
    joblib.dump(model, model_out)
    return model

def monthly_refresh(model_path: str, new_data: pd.DataFrame, ref_scores: pd.Series):
    model = joblib.load(model_path)
    X = new_data[FEATURES].fillna(0)
    scores = model.predict_proba(X)[:,1]
    psi, status = compute_psi(ref_scores.values, scores)
    log.info(f"Monthly refresh | PSI: {psi} | Status: {status} | Scored: {len(scores):,}")
    return pd.Series(scores, index=new_data.index), psi, status
