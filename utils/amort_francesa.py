from __future__ import annotations

import datetime as dt
import pandas as pd


def _pmt(principal: float, r_m: float, n: int) -> float:
    """Cuota financiera (capital + interés) en sistema francés."""
    if n <= 0:
        return 0.0
    if r_m == 0:
        return principal / n
    return principal * (r_m / (1.0 - (1.0 + r_m) ** (-n)))


def _add_months(d: dt.date, months: int) -> dt.date:
    return (pd.Timestamp(d) + pd.DateOffset(months=months)).date()


def generate_french_schedule(
    principal: float,
    annual_rate_percent: float,
    n_months: int,
    first_payment_date: dt.date,
    fixed_monthly_charges: float,
    cutoff_date: dt.date,
) -> pd.DataFrame:
    """
    Genera la tabla de amortización del sistema francés con cargos fijos
    y estado de la cuota según la fecha de corte.
    """
    principal = float(principal)
    fixed_monthly_charges = float(fixed_monthly_charges)
    n_months = int(n_months)

    annual_rate = float(annual_rate_percent) / 100.0
    r_m = annual_rate / 12.0

    cuota_financiera = _pmt(principal, r_m, n_months)

    rows = []
    saldo = principal

    for k in range(1, n_months + 1):
        fecha_pago = _add_months(first_payment_date, k - 1)

        capital_inicial = saldo
        pago_interes = capital_inicial * r_m
        pago_capital = cuota_financiera - pago_interes

        # Ajusta el último periodo para cerrar el saldo en cero
        if k == n_months:
            pago_capital = capital_inicial
            cuota_financiera = pago_interes + pago_capital

        capital_reducido = capital_inicial - pago_capital
        estado = "CANCELADO" if fecha_pago <= cutoff_date else "POR VENCER"

        pago_cargos_fijos = fixed_monthly_charges
        cuota_total = cuota_financiera + pago_cargos_fijos

        rows.append(
            {
                "cuota": k,
                "fecha_pago": fecha_pago,
                "capital_inicial": capital_inicial,
                "pago_capital": pago_capital,
                "pago_interes": pago_interes,
                "cuota_financiera": cuota_financiera,
                "capital_reducido": capital_reducido,
                "pago_cargos_fijos": pago_cargos_fijos,
                "cuota_total": cuota_total,
                "estado": estado,
            }
        )

        saldo = capital_reducido

    df = pd.DataFrame(rows)

    # Mantiene columnas numéricas para exportación y análisis
    money_cols = [
        "capital_inicial",
        "pago_capital",
        "pago_interes",
        "cuota_financiera",
        "capital_reducido",
        "pago_cargos_fijos",
        "cuota_total",
    ]
    df[money_cols] = df[money_cols].astype(float)
    df["cuota"] = df["cuota"].astype(int)
    df["fecha_pago"] = pd.to_datetime(df["fecha_pago"]).dt.date

    return df
