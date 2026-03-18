from __future__ import annotations

import datetime as dt
import pandas as pd


def _add_months(d: dt.date, months: int) -> dt.date:
    return (pd.Timestamp(d) + pd.DateOffset(months=months)).date()


def generate_german_schedule(
    principal: float,
    annual_rate_percent: float,
    n_months: int,
    first_payment_date: dt.date,
    fixed_monthly_charges: float,
    cutoff_date: dt.date,
) -> pd.DataFrame:
    """
    Genera la tabla de amortización del sistema alemán con capital fijo,
    cargos fijos y estado de la cuota según la fecha de corte.
    """
    principal = float(principal)
    fixed_monthly_charges = float(fixed_monthly_charges)
    n_months = int(n_months)

    annual_rate = float(annual_rate_percent) / 100.0
    r_m = annual_rate / 12.0

    rows = []
    saldo = principal

    # Capital fijo mensual
    pago_capital_fijo = principal / n_months if n_months > 0 else 0.0

    for k in range(1, n_months + 1):
        fecha_pago = _add_months(first_payment_date, k - 1)

        saldo_inicial = saldo
        pago_interes = saldo_inicial * r_m
        pago_capital = pago_capital_fijo

        # Ajusta el último periodo para cerrar el saldo en cero
        if k == n_months:
            pago_capital = saldo_inicial

        cuota_financiera = pago_capital + pago_interes
        saldo_final = saldo_inicial - pago_capital
        estado = "CANCELADO" if fecha_pago <= cutoff_date else "POR VENCER"

        pago_cargos_fijos = fixed_monthly_charges
        cuota_total = cuota_financiera + pago_cargos_fijos

        rows.append(
            {
                "cuota": k,
                "fecha_pago": fecha_pago,
                "saldo_inicial": saldo_inicial,
                "pago_capital": pago_capital,
                "pago_interes": pago_interes,
                "cuota_financiera": cuota_financiera,
                "saldo_final": saldo_final,
                "pago_cargos_fijos": pago_cargos_fijos,
                "cuota_total": cuota_total,
                "estado": estado,
            }
        )

        saldo = saldo_final

    df = pd.DataFrame(rows)

    # Mantiene columnas numéricas para exportación y análisis
    money_cols = [
        "saldo_inicial",
        "pago_capital",
        "pago_interes",
        "cuota_financiera",
        "saldo_final",
        "pago_cargos_fijos",
        "cuota_total",
    ]
    df[money_cols] = df[money_cols].astype(float)
    df["cuota"] = df["cuota"].astype(int)
    df["fecha_pago"] = pd.to_datetime(df["fecha_pago"]).dt.date

    return df
