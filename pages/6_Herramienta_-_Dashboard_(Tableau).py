import io
import streamlit as st
from utils.layout import firma_sidebar

# Firma global en sidebar
firma_sidebar()

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.title("Visualiza los Resultados")
st.caption("Esta guía te permitirá conectar tu **tabla de amortización final** — generada en el 'Simulador : Sistema Francés' " \
"o 'Simulador : Sistema Alemán' del menú lateral — a un dashboard en Tableau de forma **gratuita**.")
st.caption("Este dashboard —o tablero dinámico— te muestra la evolución del saldo, la distribución entre capital e intereses, y " \
"los principales indicadores para hacer el **seguimiento de tu deuda**. Con esta información, podrás tomar decisiones para optimizar " \
"tu financiamiento como **modificar el plazo, pagar menos intereses, adelantar capital y otros.**")

st.markdown(
    "<div style='margin-top: 20px;'></div>",
    unsafe_allow_html=True
)

st.markdown("##### 📊 Vista Previa del Dashboard en Tableau")

st.image(
    "assets/dashboard_preview.png",
    caption="Imagen referencial del dashboard conectado a la tabla de amortización",
    use_container_width=True
)


# ---------------- SINGLE SOURCE OF TRUTH ----------------
GUIA_TABLEAU = [
    {
        "Paso": "1) Genera y descarga tu tabla de amortización",
        "Detalle": (
            "Utiliza el 'Simulador : Sistema Francés' o 'Simulador : Sistema Alemán' "
            "de este aplicativo para generar la tabla de amortización y descarga el excel. "
            "Este archivo es la fuente de datos que conectarás a Tableau, no modifiques sus columnas o estructura."
        ),
    },
    {
        "Paso": "2) Descarga la plantilla de Tableau (.twbx)",
        "Detalle": (
            "Descarga la plantilla .twbx que encontrarás al final de esta sección. "
            "Esta plantilla de Tableau ya contiene el diseño del dashboard y está lista para conectarse a tu tabla de amortización del paso 1."
        ),
    },
    {
        "Paso": "3) Regístrate gratuitamente en Tableau Public",
        "Detalle": (
            'Ingresa a <a href="https://public.tableau.com" target="_blank" '
            'style="color:#4EA1FF; text-decoration:none;">Tableau Public</a> '
            "y crea una cuenta gratuita."
        ),
    },
    {
        "Paso": "4) Descarga e instala Tableau Public (Desktop app)",
        "Detalle": (
            'Ingresa a <a href="https://www.tableau.com/products/public/download" target="_blank" '
            'style="color:#4EA1FF; text-decoration:none;">Descargar Tableau Public</a> '
            "y descarga e instala la aplicación en tu computador."
        ),
    },
    {
        "Paso": "5) Abre la plantilla (.twbx) en Tableau Public (Desktop app)",
        "Detalle": (
            "Abre la aplicación de Tableau Public en tu computador, ve a 'Archivo' > 'Abrir' y selecciona la plantilla que descargaste en el paso 2."
        ),
    },
    {
        "Paso": "6) Reemplaza la fuente de datos por tu tabla de amortización",
        "Detalle": (
            "Ve a la pestaña 'Data Source' en la esquina inferior izquierda. "
            "En la sección 'Conexiones', despliega el menú de opciones del archivo conectado, da clic en 'Editar Conexión' "
            "y selecciona la tabla de amortización que descargaste en el paso 1. Guarda los cambios en 'Archivo' > 'Guardar'."
        ),
    },
    {
        "Paso": "7) Seguimiento deuda",
        "Detalle": (
            "El dashboard se encuentra actualizado y está listo para hacer el seguimiento "
            "de tu deuda hasta el final del periodo. Si tu deuda cambia, solo genera una nueva tabla en el simulador y "
            "actualiza el archivo las veces que necesites. Utiliza el modo presentación en la pestaña 'Seguimiento Deuda' "
            "para ver el tablero en pantalla completa."
        ),
    },
]

import re

def html_to_pdf_text(s: str) -> str:
    # Convierte <a href="URL" ...>Texto</a> en un link de ReportLab con estilo visible
    s = re.sub(
        r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>',
        r'<link href="\1"><u><font color="blue">\2</font></u></link>',
        s,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return s

def build_pdf() -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Guía - Conectar a Tableau (Simulador de Deuda)",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="CustomTitle",
        parent=styles["Title"],
        fontSize=14,
        spaceAfter=0,
    )

    elements = []
    elements.append(Paragraph("Guía – Conectar la Tabla de Amortización a Tableau", title_style))
    elements.append(Spacer(1, 12))
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

    for item in GUIA_TABLEAU:
        elements.append(Paragraph(f"<b>{item['Paso']}</b>", styles["Normal"]))
        elements.append(Spacer(1, 4))

        # En PDF, mejor sin markdown ** **
        detalle = item["Detalle"].replace("**", "")
        detalle = html_to_pdf_text(detalle)
        elements.append(Paragraph(detalle, styles["Normal"]))
        elements.append(Spacer(1, 12))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


# ---------------- UI ----------------
st.markdown(
    "<div style='margin-top: 10px;'></div>",
    unsafe_allow_html=True
)

st.markdown("##### 📘 Conexión en 7 Pasos")

# 🔹 GUIA EN TEXTO (mismo estilo del glosario)
for item in GUIA_TABLEAU:
    st.markdown(
        f"""
        <p style="margin-bottom:20px;">
            <span style="font-size:14px; font-weight:400; color:white;">
                {item['Paso']}
            </span><br>
            <span style="color:#A6A6A6; font-size:14px;">
                {item['Detalle']}
            </span>
        </p>
        """,
        unsafe_allow_html=True
    )

st.divider()

#Descarga plantilla Tableau
try:
    with open("assets/Seguimiento_Deuda.twbx", "rb") as f:
        st.download_button(
            "Descargar plantilla de Tableau (.twbx)",
            data=f.read(),
            file_name="Seguimiento_Deuda.twbx",
            mime="application/octet-stream",
            use_container_width=True,
        )
except FileNotFoundError:
    st.info(
        "Si quieres habilitar la descarga de la plantilla, guarda tu archivo .twbx en "
        "`assets/Seguimiento_Deuda.twbx`."
    )

# PDF
pdf_bytes = build_pdf()
st.download_button(
    "Descargar guía en PDF",
    data=pdf_bytes,
    file_name="Guía - Conectar a Tableau (Simulador de Deuda).pdf",
    mime="application/pdf",
    use_container_width=True,
)