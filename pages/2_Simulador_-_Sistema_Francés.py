import datetime as dt
import streamlit as st

from utils.amort_francesa import generate_french_schedule
from utils.exports import df_to_excel_bytes
from utils.layout import firma_sidebar

# Firma en la barra lateral
firma_sidebar()

# Estado de la tabla generada
if "df_francesa" not in st.session_state:
    st.session_state.df_francesa = None

# Parámetros usados para generar la tabla
if "params_francesa" not in st.session_state:
    st.session_state.params_francesa = None


def format_es(n: float, decimals: int = 2) -> str:
    """Formato 1.234.567,89 para la interfaz."""
    s = f"{n:,.{decimals}f}"
    s = s.replace(",", "X")
    s = s.replace(".", ",")
    s = s.replace("X", ".")
    return s


st.title("Generar - Tabla Francesa")
st.caption("**Sistema Francés:** las cuotas son fijas")

st.info(
    "Configura los valores y haz clic en **Generar tabla** para ver el resumen y la tabla de amortización"
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    monto = st.number_input(
        "Capital solicitado",
        min_value=0.0,
        value=100000.0,
        step=100.0,
    )
    plazo = st.number_input(
        "Plazo (meses)",
        min_value=1,
        value=120,
        step=1,
    )
    fecha_primer_pago = st.date_input(
        "Fecha del primer pago",
        value=dt.date.today(),
    )

with col2:
    tasa_anual = st.number_input(
        "Tasa nominal anual (%)",
        min_value=0.0,
        value=10.0,
        step=0.1,
    )
    cargos_fijos = st.number_input(
        "Cargos fijos mensuales",
        min_value=0.0,
        value=0.0,
        step=1.0,
        help="Ejemplo: seguro de desgravamen, seguro de incendios u otros cargos fijos. No afectan el saldo del préstamo.",
    )
    fecha_corte = st.date_input(
        "Fecha de corte",
        value=dt.date.today(),
    )

# Parámetros actuales
current_params = (
    float(monto),
    int(plazo),
    float(tasa_anual),
    float(cargos_fijos),
    str(fecha_primer_pago),
    str(fecha_corte),
)

# Reinicia la tabla si cambian los inputs
if (
    st.session_state.params_francesa is not None
    and current_params != st.session_state.params_francesa
):
    st.session_state.df_francesa = None

st.divider()

if st.button("Generar tabla"):
    st.session_state.params_francesa = current_params
    st.session_state.df_francesa = generate_french_schedule(
        principal=monto,
        annual_rate_percent=tasa_anual,
        n_months=plazo,
        first_payment_date=fecha_primer_pago,
        fixed_monthly_charges=cargos_fijos,
        cutoff_date=fecha_corte,
    )

df = st.session_state.df_francesa

if df is not None:
    # Resumen según la fecha de corte
    total_intereses = float(df["pago_interes"].sum())
    total_cargos_fijos = float(df["pago_cargos_fijos"].sum())

    deuda_total = float(monto) + total_intereses + total_cargos_fijos
    intereses_y_cargos = total_intereses + total_cargos_fijos

    cuota_mensual_total = float(df.loc[0, "cuota_total"]) if len(df) else 0.0

    total_pagado = float(df.loc[df["estado"] == "CANCELADO", "cuota_total"].sum())
    capital_pagado = float(df.loc[df["estado"] == "CANCELADO", "pago_capital"].sum())

    falta_por_pagar = float(df.loc[df["estado"] == "POR VENCER", "cuota_total"].sum())
    meses_restantes = int((df["estado"] == "POR VENCER").sum())

    st.subheader("Resumen")

    tiempo_restante_short = f"{meses_restantes // 12} a {meses_restantes % 12} m"

    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    r1c1.metric("Deuda Total", f"$ {format_es(deuda_total, 0)}")
    r1c2.metric("Capital Solicitado", f"$ {format_es(monto, 0)}")
    r1c3.metric("Intereses y Cargos Fijos", f"$ {format_es(intereses_y_cargos, 0)}")
    r1c4.metric("Cuota Mensual Total", f"$ {format_es(cuota_mensual_total, 0)}")

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    r2c1.metric("*Total Pagado", f"$ {format_es(total_pagado, 0)}")
    r2c2.metric("*Capital Pagado", f"$ {format_es(capital_pagado, 0)}")
    r2c3.metric("*Falta por Pagar", f"$ {format_es(falta_por_pagar, 0)}")
    r2c4.metric("*Tiempo Restante", tiempo_restante_short)

    st.caption("*Se calcula hasta la fecha de corte seleccionada.")
    st.divider()

    # Tabla de amortización
    st.subheader("Tabla de amortización (Francesa)")

    df_base = df.copy()

    df_base["fecha_pago"] = df_base["fecha_pago"].apply(
        lambda x: x.date() if isinstance(x, dt.datetime) else x
    )

    cols = list(df_base.columns)
    if "cuota" in cols and "fecha_pago" in cols:
        cols.remove("fecha_pago")
        idx = cols.index("cuota") + 1
        cols.insert(idx, "fecha_pago")
        df_base = df_base[cols]

    df_display = df_base.copy()
    df_display["fecha_pago"] = df_display["fecha_pago"].astype(str)

    for c in [
        "capital_inicial",
        "pago_capital",
        "pago_interes",
        "cuota_financiera",
        "capital_reducido",
        "pago_cargos_fijos",
        "cuota_total",
    ]:
        df_display[c] = df_display[c].apply(lambda x: format_es(float(x), 2))

    st.dataframe(df_display, use_container_width=True)

    st.download_button(
        "Exportar Excel",
        data=df_to_excel_bytes(df_base, sheet_name="francesa"),
        file_name="tabla_francesa.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

else:
    st.info("Genera la tabla para ver el resumen y la tabla de amortización")
