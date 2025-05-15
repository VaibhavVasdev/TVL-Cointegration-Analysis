# TVL Cointegration Analysis

This framework helps determine whether two DeFi protocols exhibit a long-term equilibrium relationship despite short-term volatility. If cointegration is found, a VECM can effectively model both short-run deviations and long-run corrections, making it a powerful tool for DeFi protocol interdependence analysis. It analyzes the Total Value Locked (TVL) time series data for two DeFi protocols — **EigenLayer** and **Symbiotic**, using time series econometric techniques including stationarity testing, cointegration testing, and the Vector Error Correction Model (VECM).

---

## Overview

The script performs the following:

- Fetches historical TVL data using the [DefiLlama API](https://defillama.com/).
- Applies log transformation and differencing.
- Tests for stationarity using:
  - Augmented Dickey-Fuller (ADF)
  - Kwiatkowski–Phillips–Schmidt–Shin (KPSS)
- Tests for cointegration using:
  - Engle-Granger method
  - Johansen test
- If cointegration is found, fits a Vector Error Correction Model (VECM).

---

## Time Series Analysis Interpretation Table

| Step | Test / Component             | Null Hypothesis (H₀)                                              | Significance Level | Decision Criteria                          | Outcome Options                        | Conclusion                                                                 |
|------|------------------------------|-------------------------------------------------------------------|---------------------|---------------------------------------------|----------------------------------------|----------------------------------------------------------------------------|
| 1    | ADF Test                     | Series has a unit root (non-stationary)                          | 0.05                | p-value < 0.05 → Reject H₀                  | Stationary / Non-Stationary           | If p < 0.05, series is **stationary**; differencing may not be needed.     |
| 1    | KPSS Test                    | Series is stationary                                              | 0.05                | p-value ≥ 0.05 → Fail to reject H₀          | Stationary / Non-Stationary           | If p ≥ 0.05, series is **stationary**; supports stationarity.              |
| 2    | Engle-Granger Cointegration | Series are not cointegrated                                      | 0.05                | p-value < 0.05 → Reject H₀                  | Cointegrated / Not Cointegrated       | If p < 0.05, the two series have a **long-run equilibrium relationship**.  |
| 2    | Johansen Test – Trace Stat  | r ≤ number of cointegration vectors                              | 5% Critical Value   | Stat > critical value → Reject H₀           | At least one cointegrating vector     | Suggests presence of cointegration if stat > critical value.               |
| 2    | Johansen Test – MaxEig Stat | No cointegration vs r = 1                                        | 5% Critical Value   | Stat > critical value → Reject H₀           | Cointegrated / Not Cointegrated       | Confirms cointegration based on eigenvalue of cointegrating relations.     |
| 3    | VECM – ECT Coefficient       | No adjustment to long-run equilibrium (no error correction)       | 0.05                | p-value < 0.05 → Reject H₀                  | Significant / Not Significant         | If significant & negative, variable **adjusts toward equilibrium**.        |
| 3    | VECM – Short-run Lags        | Lagged values have no effect on current value                    | 0.05                | p-value < 0.05 → Reject H₀                  | Predictive / Non-predictive           | If significant, past values influence current changes (**short-run impact**)|
| 3    | Cointegrating Vector (β)     | No long-run equilibrium relationship                              | 0.05                | p-value < 0.05 → Reject H₀                  | Valid / Invalid Relationship          | Defines **equilibrium relation** between the two series (e.g., log_eig ~ log_sym). |



