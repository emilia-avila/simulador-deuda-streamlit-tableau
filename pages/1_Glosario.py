import io
import datetime as dt
import pandas as pd
import streamlit as st
from utils.layout import firma_sidebar

# Firma global en sidebar
firma_sidebar()

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


# ---------------- SINGLE SOURCE OF TRUTH ----------------
CONCEPTOS = [
    {
        "Concepto": "Tabla de Amortización",
        "Definición": "Calendario de pagos que muestra cómo se paga una deuda mes a mes, detallando capital, intereses, cargos fijos y saldo pendiente.",
    },
    {
        "Concepto": "Cargos Fijos",
        "Definición": "Valores adicionales que se pagan junto con la cuota del préstamo, como seguros o costos administrativos. No afectan el saldo del préstamo.",
    },
    {
        "Concepto": "Cuota Financiera",
        "Definición": "Es el pago que se realiza en cada periodo y corresponde a la suma del capital + intereses. No incluye cargos fijos.",
    },
    {
        "Concepto": "Cuota Total",
        "Definición": "Es el pago completo de cada periodo: capital + intereses + cargos fijos.",
    },
    {
        "Concepto": "Sistema Francés",
        "Definición": "Un tipo de tabla de amortización con cuota financiera fija. Al inicio se pagan más intereses.",
    },
    {
        "Concepto": "Sistema Alemán",
        "Definición": "Un tipo de tabla de amortización con abono a capital fijo. La cuota total disminuye con el tiempo y genera menos intereses totales.",
    },
    {
        "Concepto": "Tasa Nominal Anual (TNA)",
        "Definición": "Es la tasa de interés anual del crédito, sin considerar capitalización dentro del año.",
    },
    {
        "Concepto": "Fecha de Corte",
        "Definición": "Fecha utilizada para determinar qué cuotas están canceladas y cuáles están por vencer.",
    },
    {
        "Concepto": "Deuda Total",
        "Definición": "Es el monto total que se pagará durante todo el plazo del crédito, compuesto por capital, intereses y cargos fijos.",
    },
    {
        "Concepto": "Dashboard",
        "Definición": "Es una interfaz visual que presenta indicadores clave (KPIs) y métricas relevantes mediante gráficos y tablas, permitiendo monitorear desempeño, analizar tendencias y apoyar la toma de decisiones basada en datos.",
    },
    {
        "Concepto": "Tableau",
        "Definición": "Es una herramienta de visualización y análisis de datos que permite conectar, transformar y analizar información mediante gráficos y dashboards interactivos.",
    },
    {
        "Concepto": "Archivo .twbx (Tableau Packaged Workbook)",
        "Definición": "Es un archivo comprimido que contiene un dashboard de Tableau junto con sus fuentes de datos y recursos asociados.",
    },
]


def conceptos_df():
    return pd.DataFrame(CONCEPTOS, columns=["Concepto", "Definición"])


def build_pdf() -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Glosario - Simulador de Deuda",
    )

    styles = getSampleStyleSheet()

    # ✅ Título más pequeño (SOLO CAMBIO)
    title_style = ParagraphStyle(
        name="CustomTitle",
        parent=styles["Title"],
        fontSize=14,     # antes: styles["Title"] (más grande)
        spaceAfter=0,
    )

    elements = []

    # Título
    elements.append(Paragraph("Glosario – Simulador de Deuda", title_style))
    elements.append(Spacer(1, 12))

    # Nombre
    elements.append(
        Paragraph(
        'Elaborado por: '
        '<link href="https://www.linkedin.com/in/emilia-avila-vasconez">'
        '<u><font color="blue">Emilia Ávila</font></u>'
        '</link>',
        styles["Normal"]
    )
    )
    elements.append(Spacer(1, 30))

    # Glosario en texto
    for item in CONCEPTOS:
        elements.append(Paragraph(f"<b>{item['Concepto']}</b>", styles["Normal"]))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(item["Definición"], styles["Normal"]))
        elements.append(Spacer(1, 14))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


# ---------------- UI ----------------

st.title("Glosario")
st.caption(
    "Definiciones clave utilizadas en el Simulador de Deuda y Dashboard de Seguimiento"
)

st.info("Revisa las definiciones aquí o descargar el glosario en PDF")

st.divider()

# 🔹 GLOSARIO EN TEXTO
for item in CONCEPTOS:
    st.markdown(
        f"""
        <p style="margin-bottom:20px;">
            <span style="font-size:14px; font-weight:400; color:white;">
                {item['Concepto']}
            </span><br>
            <span style="color:#A6A6A6; font-size:14px;">
                {item['Definición']}
            </span>
        </p>
        """,
        unsafe_allow_html=True
    )

st.divider()

pdf_bytes = build_pdf()

st.download_button(
    "Descargar PDF",
    data=pdf_bytes,
    file_name="Glosario - Simulador de Deuda.pdf",
    mime="application/pdf",
    use_container_width=True,
)
