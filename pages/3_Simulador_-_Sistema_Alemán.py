import datetime as dt
import streamlit as st

from utils.amort_alemana import generate_german_schedule
from utils.exports import df_to_csv_bytes, df_to_excel_bytes
from utils.layout import firma_sidebar

# Firma global en sidebar
firma_sidebar()

# Persistencia para que no se "reinicie" la vista al exportar
if "df_alemana" not in st.session_state:
    st.session_state.df_alemana = None

# Guardar parámetros usados para generar la tabla (para resetear si cambian inputs)
if "params_alemana" not in st.session_state:
    st.session_state.params_alemana = None


def format_es(n: float, decimals: int = 2) -> str:
    """Formato 1.234.567,89 para UI."""
    s = f"{n:,.{decimals}f}"      # 1,234,567.89
    s = s.replace(",", "X")       # 1X234X567.89
    s = s.replace(".", ",")       # 1X234X567,89
    s = s.replace("X", ".")       # 1.234.567,89
    return s


st.title("Generar - Tabla Alemana")
st.caption("**Sistema Alemán:** el abono al capital es fijo y la cuota total disminuye con el tiempo")
st.info("Configura los valores y haz clic en **Generar tabla** para ver el resumen y la tabla de amortización")

st.divider()

col1, col2 = st.columns(2)
with col1:
    monto = st.number_input("Capital solicitado", min_value=0.0, value=100000.0, step=100.0)
    plazo = st.number_input("Plazo (meses)", min_value=1, value=120, step=1)
    fecha_primer_pago = st.date_input("Fecha del primer pago", value=dt.date.today())

with col2:
    tasa_anual = st.number_input("Tasa nominal anual (%)", min_value=0.0, value=10.0, step=0.1)
    cargos_fijos = st.number_input(
        "Cargos fijos mensuales",
        min_value=0.0,
        value=0.0,
        step=1.0,
        help="Ejemplo: seguro de desgravamen, seguro de incendios u otros cargos fijos. No afectan el saldo del préstamo.",
    )
    fecha_corte = st.date_input("Fecha de corte", value=dt.date.today())

# Snapshot de inputs actuales
current_params = (
    float(monto),
    int(plazo),
    float(tasa_anual),
    float(cargos_fijos),
    str(fecha_primer_pago),
    str(fecha_corte),
)

# Si cambian inputs después de haber generado tabla, resetea (pero exportar no cambia inputs)
if st.session_state.params_alemana is not None and current_params != st.session_state.params_alemana:
    st.session_state.df_alemana = None

st.divider()

if st.button("Generar tabla"):
    st.session_state.params_alemana = current_params
    st.session_state.df_alemana = generate_german_schedule(
        principal=monto,
        annual_rate_percent=tasa_anual,
        n_months=plazo,
        first_payment_date=fecha_primer_pago,
        fixed_monthly_charges=cargos_fijos,
        cutoff_date=fecha_corte,
    )

df = st.session_state.df_alemana

if df is not None:
    # --- Resumen dinámico según fecha de corte ---
    total_intereses = float(df["pago_interes"].sum())  # proyectado total
    total_cargos_fijos = float(df["pago_cargos_fijos"].sum())

    deuda_total = float(monto) + total_intereses + total_cargos_fijos
    intereses_y_cargos = total_intereses + total_cargos_fijos

    # En alemán la cuota total puede variar por mes: mostramos la primera como referencia
    cuota_mensual_total = float(df.loc[0, "cuota_total"]) if len(df) else 0.0

    total_pagado = float(df.loc[df["estado"] == "CANCELADO", "cuota_total"].sum())
    capital_pagado = float(df.loc[df["estado"] == "CANCELADO", "pago_capital"].sum())

    falta_por_pagar = float(df.loc[df["estado"] == "POR VENCER", "cuota_total"].sum())
    meses_restantes = int((df["estado"] == "POR VENCER").sum())

    st.subheader("Resumen")

    # Versión corta para que no se corte en metric
    tiempo_restante_short = f"{meses_restantes // 12} a {meses_restantes % 12} m"

    # Fila 1 (4 columnas)
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    r1c1.metric("Deuda Total", f"$ {format_es(deuda_total, 0)}")
    r1c2.metric("Capital Solicitado", f"$ {format_es(monto, 0)}")
    r1c3.metric("Intereses y Cargos Fijos", f"$ {format_es(intereses_y_cargos, 0)}")
    r1c4.metric("Cuota Máxima", f"$ {format_es(cuota_mensual_total, 0)}")

    # Fila 2 (4 columnas)
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    r2c1.metric("*Total Pagado", f"$ {format_es(total_pagado, 0)}")
    r2c2.metric("*Capital Pagado", f"$ {format_es(capital_pagado, 0)}")
    r2c3.metric("*Falta por Pagar", f"$ {format_es(falta_por_pagar, 0)}")
    r2c4.metric("*Tiempo Restante", tiempo_restante_short)

    st.caption("**Cuota Máxima:** en la tabla Alemana, la cuota mensual disminuye con el tiempo.")
    st.caption("*Se calcula hasta la fecha de corte seleccionada.")

    st.divider()

    # --- Tabla: mostrar con formato latino en pantalla (pero exportar numérico limpio) ---
    st.subheader("Tabla de amortización (Alemana)")

    # ✅ BASE: misma estructura para UI y export (numérico + fecha real)
    df_base = df.copy()

    # Asegurar que fecha_pago sea tipo date (por seguridad)
    df_base["fecha_pago"] = df_base["fecha_pago"].apply(
        lambda x: x.date() if isinstance(x, dt.datetime) else x
    )

    # Reordenar para que 'fecha_pago' vaya justo después de 'cuota'
    cols = list(df_base.columns)
    if "cuota" in cols and "fecha_pago" in cols:
        cols.remove("fecha_pago")
        idx = cols.index("cuota") + 1
        cols.insert(idx, "fecha_pago")
        df_base = df_base[cols]

    # UI: formatear solo para pantalla
    df_display = df_base.copy()
    df_display["fecha_pago"] = df_display["fecha_pago"].astype(str)

    for c in [
        "saldo_inicial",
        "pago_capital",
        "pago_interes",
        "cuota_financiera",
        "saldo_final",
        "pago_cargos_fijos",
        "cuota_total",
    ]:
        df_display[c] = df_display[c].apply(lambda x: format_es(float(x), 2))

    st.dataframe(df_display, use_container_width=True)

    st.download_button(
        "Exportar Excel",
        data=df_to_excel_bytes(df_base, sheet_name="alemana"),
        file_name="tabla_alemana.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

else:
    st.info("Genera la tabla para ver el resumen y la tabla de amortización.")