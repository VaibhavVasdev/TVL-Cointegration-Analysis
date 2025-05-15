import requests
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss, coint
from statsmodels.tsa.vector_ar.vecm import coint_johansen, VECM


def fetch_tvl(protocol: str) -> pd.DataFrame:
    url = f"https://api.llama.fi/protocol/{protocol}"
    resp = requests.get(url)
    resp.raise_for_status()
    payload = resp.json()

    history = payload.get('tvlHistory') or payload.get('tvl')
    if not history:
        raise RuntimeError(f"No historical TVL data found for {protocol}")

    df = pd.DataFrame(history)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], unit='ms')
    else:
        raise RuntimeError("No 'date' field in TVL history")

    if 'totalLiquidityUSD' in df.columns:
        df = df.rename(columns={'totalLiquidityUSD': 'tvl'})
    elif 'tvl' not in df.columns:
        raise RuntimeError("No TVL field found in history (expected 'totalLiquidityUSD' or 'tvl')")

    df = df.set_index('date')[['tvl']]
    return df


def adf_test(series):
    result = adfuller(series, autolag='AIC')
    return result[1] < 0.05  # Stationary if p-value < 0.05


def kpss_test(series):
    statistic, p_value, _, _ = kpss(series, regression='c', nlags='auto')
    return p_value >= 0.05  # Stationary if p-value >= 0.05


def main():
    # Fetch and align data
    df_eig = fetch_tvl("eigenlayer")
    df_sym = fetch_tvl("symbiotic")

    df = pd.concat([
        df_eig.rename(columns={'tvl': 'eig_tvl'}),
        df_sym.rename(columns={'tvl': 'sym_tvl'})
    ], axis=1).dropna()

    df['log_eig'] = np.log(df['eig_tvl'])
    df['log_sym'] = np.log(df['sym_tvl'])

    # Difference logs for stationarity testing
    df['dlog_eig'] = df['log_eig'].diff()
    df['dlog_sym'] = df['log_sym'].diff()

    print("=== Stationarity of Differenced Log Series ===")
    print(f"EigenLayer ADF: {'Stationary' if adf_test(df['dlog_eig'].dropna()) else 'Non-Stationary'}")
    print(f"EigenLayer KPSS: {'Stationary' if kpss_test(df['dlog_eig'].dropna()) else 'Non-Stationary'}")
    print(f"Symbiotic ADF: {'Stationary' if adf_test(df['dlog_sym'].dropna()) else 'Non-Stationary'}")
    print(f"Symbiotic KPSS: {'Stationary' if kpss_test(df['dlog_sym'].dropna()) else 'Non-Stationary'}")

    # Cointegration tests
    eg_pval = coint(df['log_eig'], df['log_sym'])[1]
    print(f"\nEngle-Granger cointegration p-value: {eg_pval:.4f} --> {'Cointegrated' if eg_pval < 0.05 else 'Not Cointegrated'}")

    johansen_res = coint_johansen(df[['log_eig', 'log_sym']], det_order=0, k_ar_diff=1)
    print("\nJohansen Test Results:")
    print(f"Trace stat r=0: {johansen_res.lr1[0]:.4f} vs crit 5%: {johansen_res.cvt[0, 1]} --> {'Reject H0' if johansen_res.lr1[0] > johansen_res.cvt[0, 1] else 'Fail to Reject H0'}")
    print(f"MaxEig stat r=0 vs 1: {johansen_res.lr2[0]:.4f} vs crit 5%: {johansen_res.cvm[0, 1]} --> {'Reject H0' if johansen_res.lr2[0] > johansen_res.cvm[0, 1] else 'Fail to Reject H0'}")

    # Switch to VECM if cointegrated
    vecm_data = df[['log_eig', 'log_sym']].dropna()
    vecm_model = VECM(vecm_data, k_ar_diff=1, coint_rank=1, deterministic='ci')
    vecm_res = vecm_model.fit()

    print("\n=== VECM Summary ===")
    print(vecm_res.summary())


if __name__ == "__main__":
    main()
