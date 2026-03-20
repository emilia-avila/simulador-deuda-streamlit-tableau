import streamlit as st

from utils.layout import firma_sidebar

# Firma en la barra lateral
firma_sidebar()


def format_es(n: float, decimals: int = 2) -> str:
    """Formato 1.234.567,89 para la interfaz."""
    s = f"{n:,.{decimals}f}"
    s = s.replace(",", "X")
    s = s.replace(".", ",")
    s = s.replace("X", ".")
    return s


def _pmt(principal: float, r_m: float, n: int) -> float:
    """Cuota financiera (capital + interés) en sistema francés."""
    if n <= 0:
        return 0.0
    if r_m == 0:
        return principal / n
    return principal * (r_m / (1.0 - (1.0 + r_m) ** (-n)))


def solve_rate_french(principal: float, cuota_financiera: float, n: int) -> float:
    """
    Encuentra la tasa mensual que cumple:
    PMT(principal, r, n) = cuota_financiera.
    """
    if principal <= 0 or n <= 0 or cuota_financiera <= 0:
        return 0.0

    min_cuota = principal / n
    if cuota_financiera < min_cuota:
        raise ValueError(
            f"La cuota es demasiado baja. Mínimo teórico (sin interés) = {min_cuota:.6f}"
        )

    low = 0.0
    high = 1.0

    for _ in range(60):
        if _pmt(principal, high, n) >= cuota_financiera:
            break
        high *= 2
        if high > 10:
            break

    for _ in range(80):
        mid = (low + high) / 2.0
        p = _pmt(principal, mid, n)
        if p < cuota_financiera:
            low = mid
        else:
            high = mid

    return (low + high) / 2.0


st.title("Calcular - Tasa de Interés")
st.caption(
    "Esta herramienta calcula la **tasa nominal** cuando se conoce el capital, el plazo y la cuota financiera del primer mes"
)
st.info("Configura los valores y haz clic en **Calcular Tasa** para obtener el resultado")

st.divider()

sistema = st.selectbox(
    "Tipo de tabla",
    ["Sistema Francés (cuota fija)", "Sistema Alemán (capital fijo, cuota decreciente)"],
)

col1, col2 = st.columns(2)

with col1:
    principal = st.number_input(
        "Capital solicitado",
        min_value=0.0,
        value=100000.0,
        step=100.0,
    )
    n_months = st.number_input(
        "Plazo (meses)",
        min_value=1,
        value=120,
        step=1,
    )

with col2:
    cuota_mes1 = st.number_input(
        "Cuota financiera del mes 1",
        min_value=0.0,
        value=1322.0,
        step=1.0,
        help="**Solo capital + interés** \n\n"\
        "No se incluye seguros (desgravamen/incendios) ni cargos administrativos",
    )

st.info(
    "✅ En el **Sistema Alemán**, la tasa nominal se calcula con la cuota financiera del **mes 1**\n\n"
    "✅ En el **Sistema Francés**, la cuota financiera es fija, por lo que puede tomarse de cualquier mes"
)

st.divider()

if st.button("Calcular Tasa"):
    try:
        principal = float(principal)
        n = int(n_months)
        cuota = float(cuota_mes1)

        if principal <= 0 or n <= 0 or cuota <= 0:
            st.error("Revisa los valores: capital, plazo y cuota deben ser mayores a 0.")
            st.stop()

        if sistema.startswith("Sistema Alemán"):
            # Sistema alemán: calcula la tasa a partir de la cuota del primer mes
            abono_capital = principal / n
            r_m = (cuota - abono_capital) / principal

            if r_m < 0:
                st.error(
                    "Con esos datos, la tasa resultaría negativa. "
                    "La cuota del mes 1 debe ser al menos (capital / plazo)."
                )
                st.stop()

        else:
            # Sistema francés: resuelve la tasa que reproduce la cuota
            r_m = solve_rate_french(principal, cuota, n)

        tasa_mensual_pct = r_m * 100.0
        tasa_nominal_anual_pct = tasa_mensual_pct * 12.0

        st.subheader("Resultado")

        c1, c2 = st.columns(2)
        c1.metric("Tasa nominal mensual", f"{format_es(tasa_mensual_pct, 4)} %")
        c2.metric("Tasa nominal anual", f"{format_es(tasa_nominal_anual_pct, 4)} %")

        st.caption("Tasa nominal anual = tasa nominal mensual × 12")

    except ValueError as e:
        st.error(f"No se pudo calcular la tasa: {e}")
