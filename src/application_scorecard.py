"""
Application Credit Scorecard — WoE Logistic Regression
Straive Strategic Analytics | Credit Risk Practice
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import logging

log = logging.getLogger(__name__)

FEATURES = ["bureau_score","annual_income","debt_to_income_ratio",
            "employment_type","time_at_address_months",
            "num_existing_accounts","requested_credit_limit",
            "num_inquiries_6m","months_since_last_delinquency"]

def compute_woe_iv(df, feature, target, bins=10):
    """Compute Weight of Evidence and Information Value for a feature."""
    df = df[[feature, target]].copy().dropna()
    if df[feature].dtype in ["object","category"]:
        groups = df.groupby(feature)[target].agg(["sum","count"])
    else:
        df["bin"] = pd.qcut(df[feature], q=bins, duplicates="drop")
        groups = df.groupby("bin")[target].agg(["sum","count"])
    groups.columns = ["bads","total"]
    groups["goods"] = groups["total"] - groups["bads"]
    total_bad  = groups["bads"].sum()
    total_good = groups["goods"].sum()
    groups["dist_bad"]  = groups["bads"]  / total_bad
    groups["dist_good"] = groups["goods"] / total_good
    groups["woe"] = np.log(groups["dist_good"] / groups["dist_bad"].replace(0, 1e-9))
    groups["iv"]  = (groups["dist_good"] - groups["dist_bad"]) * groups["woe"]
    return groups, groups["iv"].sum()

def train(df: pd.DataFrame, target: str = "bad_90dpd_12m"):
    X = df[FEATURES]; y = df[target]
    log.info(f"Training: {len(df):,} rows | bad rate: {y.mean():.2%}")
    woe_map = {}
    for feat in FEATURES:
        try:
            _, iv = compute_woe_iv(df, feat, target)
            woe_map[feat] = iv
            log.info(f"  {feat}: IV={iv:.3f} ({'Strong' if iv>0.3 else 'Medium' if iv>0.1 else 'Weak'})")
        except Exception as e:
            log.warning(f"  {feat}: {e}")
    model = LogisticRegression(max_iter=500, random_state=42)
    model.fit(X.fillna(X.median()), y)
    proba = model.predict_proba(X.fillna(X.median()))[:,1]
    log.info(f"Train AUC: {roc_auc_score(y, proba):.4f}")
    return model, woe_map
