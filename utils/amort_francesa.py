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
    Genera tabla francesa con:
    - tasa mensual = (tasa anual nominal) / 12
    - cargos fijos mensuales (no afectan saldo)
    - estado según fecha de corte
    Columnas base para BI: incluye fecha_pago como Date.
    """
    principal = float(principal)
    fixed_monthly_charges = float(fixed_monthly_charges)
    n_months = int(n_months)

    annual_rate = float(annual_rate_percent) / 100.0
    r_m = annual_rate / 12.0  # Siempre nominal ÷ 12

    cuota_financiera = _pmt(principal, r_m, n_months)

    rows = []
    saldo = principal

    for k in range(1, n_months + 1):
        fecha_pago = _add_months(first_payment_date, k - 1)

        capital_inicial = saldo
        pago_interes = capital_inicial * r_m
        pago_capital = cuota_financiera - pago_interes

        # Ajuste por redondeo en el último periodo: cerrar el saldo a 0 exacto
        if k == n_months:
            pago_capital = capital_inicial
            cuota_financiera = pago_interes + pago_capital

        capital_reducido = capital_inicial - pago_capital

        # Estado según fecha de corte (más robusto que anio/mes/aniomes)
        estado = "CANCELADO" if fecha_pago <= cutoff_date else "POR VENCER"

        pago_cargos_fijos = fixed_monthly_charges
        cuota_total = cuota_financiera + pago_cargos_fijos

        rows.append(
            {
                "cuota": k,
                "fecha_pago": fecha_pago,  # ✅ columna Date para Tableau
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

    # Mantener numérico para exportación / BI (sin formatear como texto)
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

    # Asegurar que fecha_pago sea Date (no string)
    df["fecha_pago"] = pd.to_datetime(df["fecha_pago"]).dt.date

    return df