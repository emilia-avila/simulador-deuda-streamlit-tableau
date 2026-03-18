import datetime as dt

import pandas as pd
import streamlit as st

from utils.amort_alemana import generate_german_schedule
from utils.amort_francesa import generate_french_schedule
from utils.exports import df_to_excel_bytes
from utils.layout import firma_sidebar

# Firma en la barra lateral
firma_sidebar()

# Estado de los escenarios generados
if "df_comp_a" not in st.session_state:
    st.session_state.df_comp_a = None
if "df_comp_b" not in st.session_state:
    st.session_state.df_comp_b = None

# Parámetros usados para generar cada escenario
if "params_comp_a" not in st.session_state:
    st.session_state.params_comp_a = None
if "params_comp_b" not in st.session_state:
    st.session_state.params_comp_b = None


def format_es(n: float, decimals: int = 2) -> str:
    """Formato 1.234.567,89 para la interfaz."""
    s = f"{n:,.{decimals}f}"
    s = s.replace(",", "X")
    s = s.replace(".", ",")
    s = s.replace("X", ".")
    return s


def schedule_for(
    system_key: str,
    principal: float,
    annual_rate_percent: float,
    n_months: int,
    first_payment_date: dt.date,
    fixed_monthly_charges: float,
    cutoff_date: dt.date,
):
    if system_key.startswith("Sistema Francés"):
        return generate_french_schedule(
            principal=principal,
            annual_rate_percent=annual_rate_percent,
            n_months=n_months,
            first_payment_date=first_payment_date,
            fixed_monthly_charges=fixed_monthly_charges,
            cutoff_date=cutoff_date,
        )

    return generate_german_schedule(
        principal=principal,
        annual_rate_percent=annual_rate_percent,
        n_months=n_months,
        first_payment_date=first_payment_date,
        fixed_monthly_charges=fixed_monthly_charges,
        cutoff_date=cutoff_date,
    )


def cuota_value(df: pd.DataFrame, system_key: str) -> float:
    """En francés la cuota es fija; en alemán se toma la cuota máxima."""
    if df is None or len(df) == 0:
        return 0.0

    if system_key.startswith("Sistema Francés"):
        return float(df.loc[0, "cuota_total"])

    return float(df["cuota_total"].max())


def compute_kpis(df: pd.DataFrame, principal: float, system_key: str) -> dict:
    total_intereses = float(df["pago_interes"].sum())
    total_cargos_fijos = float(df["pago_cargos_fijos"].sum())

    deuda_total = float(principal) + total_intereses + total_cargos_fijos
    intereses_y_cargos = total_intereses + total_cargos_fijos

    total_pagado = float(df.loc[df["estado"] == "CANCELADO", "cuota_total"].sum())
    capital_pagado = float(df.loc[df["estado"] == "CANCELADO", "pago_capital"].sum())

    falta_por_pagar = float(df.loc[df["estado"] == "POR VENCER", "cuota_total"].sum())

    meses_restantes = int((df["estado"] == "POR VENCER").sum())
    tiempo_restante_short = f"{meses_restantes // 12} a {meses_restantes % 12} m"

    cuota_val = cuota_value(df, system_key)

    return {
        "deuda_total": deuda_total,
        "capital": float(principal),
        "intereses_y_cargos": intereses_y_cargos,
        "cuota_val": cuota_val,
        "total_pagado": total_pagado,
        "capital_pagado": capital_pagado,
        "falta_por_pagar": falta_por_pagar,
        "tiempo_restante": tiempo_restante_short,
        "total_intereses": total_intereses,
        "total_cargos_fijos": total_cargos_fijos,
        "meses_restantes": meses_restantes,
    }


def money_ui(x: float) -> str:
    return f"$ {format_es(float(x), 0)}"


def text_ui(x) -> str:
    return str(x)


st.title("Escenarios")
st.info("Compara dos escenarios (A vs B) cambiando cualquier input")
st.divider()

# Inputs de cada escenario
cA, cB = st.columns(2)

with cA:
    st.subheader("Escenario A")
    a_system = st.selectbox(
        "Tipo de tabla (A)",
        ["Sistema Francés", "Sistema Alemán"],
        key="a_system",
    )
    a_capital = st.number_input(
        "Capital solicitado (A)",
        min_value=0.0,
        value=100000.0,
        step=100.0,
        key="a_capital",
    )
    a_plazo = st.number_input(
        "Plazo (meses) (A)",
        min_value=1,
        value=120,
        step=1,
        key="a_plazo",
    )
    a_tasa = st.number_input(
        "Tasa nominal anual (%) (A)",
        min_value=0.0,
        value=10.0,
        step=0.1,
        key="a_tasa",
    )
    a_cargos = st.number_input(
        "Cargos fijos mensuales (A)",
        min_value=0.0,
        value=0.0,
        step=1.0,
        help="Seguro de desgravamen, seguro de incendios u otros cargos fijos (no afectan el saldo del préstamo)",
        key="a_cargos",
    )
    a_fecha_1 = st.date_input(
        "Fecha del primer pago (A)",
        value=dt.date.today(),
        key="a_fecha_1",
    )
    a_corte = st.date_input(
        "Fecha de corte (A)",
        value=dt.date.today(),
        key="a_corte",
    )

with cB:
    st.subheader("Escenario B")
    b_system = st.selectbox(
        "Tipo de tabla (B)",
        ["Sistema Francés", "Sistema Alemán"],
        key="b_system",
    )
    b_capital = st.number_input(
        "Capital solicitado (B)",
        min_value=0.0,
        value=100000.0,
        step=100.0,
        key="b_capital",
    )
    b_plazo = st.number_input(
        "Plazo (meses) (B)",
        min_value=1,
        value=120,
        step=1,
        key="b_plazo",
    )
    b_tasa = st.number_input(
        "Tasa nominal anual (%) (B)",
        min_value=0.0,
        value=12.0,
        step=0.1,
        key="b_tasa",
    )
    b_cargos = st.number_input(
        "Cargos fijos mensuales (B)",
        min_value=0.0,
        value=0.0,
        step=1.0,
        help="Seguro de desgravamen, seguro de incendios u otros cargos fijos (no afectan el saldo del préstamo)",
        key="b_cargos",
    )
    b_fecha_1 = st.date_input(
        "Fecha del primer pago (B)",
        value=dt.date.today(),
        key="b_fecha_1",
    )
    b_corte = st.date_input(
        "Fecha de corte (B)",
        value=dt.date.today(),
        key="b_corte",
    )

# Parámetros actuales
params_a = (
    a_system,
    float(a_capital),
    int(a_plazo),
    float(a_tasa),
    float(a_cargos),
    str(a_fecha_1),
    str(a_corte),
)
params_b = (
    b_system,
    float(b_capital),
    int(b_plazo),
    float(b_tasa),
    float(b_cargos),
    str(b_fecha_1),
    str(b_corte),
)

# Reinicia el resultado si cambian los inputs
if st.session_state.params_comp_a is not None and params_a != st.session_state.params_comp_a:
    st.session_state.df_comp_a = None

if st.session_state.params_comp_b is not None and params_b != st.session_state.params_comp_b:
    st.session_state.df_comp_b = None

st.divider()

compare_direction = st.radio("Comparación", ["A - B", "B - A"], horizontal=True)

btn = st.button("Generar resultados", use_container_width=True)

if btn:
    st.session_state.params_comp_a = params_a
    st.session_state.params_comp_b = params_b

    st.session_state.df_comp_a = schedule_for(
        system_key=a_system,
        principal=a_capital,
        annual_rate_percent=a_tasa,
        n_months=a_plazo,
        first_payment_date=a_fecha_1,
        fixed_monthly_charges=a_cargos,
        cutoff_date=a_corte,
    )

    st.session_state.df_comp_b = schedule_for(
        system_key=b_system,
        principal=b_capital,
        annual_rate_percent=b_tasa,
        n_months=b_plazo,
        first_payment_date=b_fecha_1,
        fixed_monthly_charges=b_cargos,
        cutoff_date=b_corte,
    )

df_a = st.session_state.df_comp_a
df_b = st.session_state.df_comp_b

if df_a is None or df_b is None:
    st.info("Genera los resultados para ver el **resumen comparativo**")
    st.stop()

# KPIs de cada escenario
kpi_a = compute_kpis(df_a, a_capital, a_system)
kpi_b = compute_kpis(df_b, b_capital, b_system)

# Dirección del delta
if compare_direction == "B - A":
    delta_sign = 1
else:
    delta_sign = -1

# Delta de tiempo restante en meses
delta_meses = (kpi_b["meses_restantes"] - kpi_a["meses_restantes"]) * delta_sign
abs_m = abs(int(delta_meses))
delta_time_str = f"{abs_m // 12} a {abs_m % 12} m"

if delta_meses > 0:
    delta_time_str = f"+{delta_time_str}"
elif delta_meses < 0:
    delta_time_str = f"-{delta_time_str}"
else:
    delta_time_str = "0 a 0 m"

rows = [
    ("Tipo de Tabla", a_system, b_system, ""),
    (
        "Deuda Total",
        kpi_a["deuda_total"],
        kpi_b["deuda_total"],
        (kpi_b["deuda_total"] - kpi_a["deuda_total"]) * delta_sign,
    ),
    (
        "Capital Solicitado",
        kpi_a["capital"],
        kpi_b["capital"],
        (kpi_b["capital"] - kpi_a["capital"]) * delta_sign,
    ),
    (
        "Intereses y Cargos Fijos",
        kpi_a["intereses_y_cargos"],
        kpi_b["intereses_y_cargos"],
        (kpi_b["intereses_y_cargos"] - kpi_a["intereses_y_cargos"]) * delta_sign,
    ),
    (
        "Cuota Total",
        kpi_a["cuota_val"],
        kpi_b["cuota_val"],
        (kpi_b["cuota_val"] - kpi_a["cuota_val"]) * delta_sign,
    ),
    (
        "Total Pagado",
        kpi_a["total_pagado"],
        kpi_b["total_pagado"],
        (kpi_b["total_pagado"] - kpi_a["total_pagado"]) * delta_sign,
    ),
    (
        "Capital Pagado",
        kpi_a["capital_pagado"],
        kpi_b["capital_pagado"],
        (kpi_b["capital_pagado"] - kpi_a["capital_pagado"]) * delta_sign,
    ),
    (
        "Falta por Pagar",
        kpi_a["falta_por_pagar"],
        kpi_b["falta_por_pagar"],
        (kpi_b["falta_por_pagar"] - kpi_a["falta_por_pagar"]) * delta_sign,
    ),
    ("Tiempo Restante", kpi_a["tiempo_restante"], kpi_b["tiempo_restante"], delta_time_str),
]

delta_col = f"Δ ({compare_direction})"
df_summary_raw = pd.DataFrame(
    rows,
    columns=["Métrica", "Escenario A", "Escenario B", delta_col],
)

# Tabla formateada para pantalla
df_summary_display = df_summary_raw.copy()

for col in ["Escenario A", "Escenario B", delta_col]:
    df_summary_display[col] = df_summary_display.apply(
        lambda r: (
            money_ui(r[col])
            if r["Métrica"] not in ["Tipo de Tabla", "Tiempo Restante"] and r[col] != ""
            else text_ui(r[col])
        ),
        axis=1,
    )

st.subheader("Resumen Comparativo")
st.dataframe(df_summary_display, use_container_width=True, hide_index=True)

st.caption(
    "**Nota:** en el sistema francés la cuota es fija; en el sistema alemán se muestra la cuota máxima (la más alta)"
)

st.download_button(
    "Exportar Excel",
    data=df_to_excel_bytes(df_summary_raw, sheet_name="resumen_escenarios"),
    file_name="resumen_escenarios.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
