import io
import re
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from utils.layout import firma_sidebar

# Firma en la barra lateral
firma_sidebar()

st.title("Visualiza los Resultados")
st.caption(
    "Esta guía te permitirá conectar tu **tabla de amortización final** —generada en el "
    "'Simulador : Sistema Francés' o 'Simulador : Sistema Alemán' del menú lateral— "
    "a un dashboard en Tableau de forma **gratuita**."
)
st.caption(
    "Este dashboard —o tablero dinámico— te muestra la evolución del saldo, la distribución "
    "entre capital e intereses, y los principales indicadores para hacer el **seguimiento "
    "de tu deuda**. Con esta información, podrás tomar decisiones para optimizar tu "
    "financiamiento como **modificar el plazo, pagar menos intereses, adelantar capital y otros.**"
)

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

st.markdown("##### 📊 Vista Previa del Dashboard en Tableau")

st.markdown(
    """
    <style>
    [data-testid="stImage"] img {
        border: 1px solid #D9D9D9;
        border-radius: 10px;
        background-color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.image(
    "assets/dashboard_preview.png",
    caption="Imagen referencial del dashboard conectado a la tabla de amortización",
    use_container_width=True,
)

st.divider()

# Pasos de la guía
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
            "Descarga la plantilla .twbx que encontrarás al final de esta sección.\n\n"
            "Esta plantilla de Tableau ya contiene el diseño del dashboard y está lista para conectarse a tu tabla de amortización del paso 1."
        ),
    },
    {
        "Paso": "3) Regístrate, descarga e instala Tableau Public (es la versión gratuita para escritorio)",
        "Detalle": (
            'Ingresa a <a href="https://www.tableau.com/products/public/download" target="_blank" '
            'style="color:#4EA1FF; text-decoration:none;">Descargar Tableau Public</a> '
            "y descarga e instala la aplicación en tu computador."
        ),
    },
    {
        "Paso": "4) Abre la plantilla (.twbx) en Tableau Public (Desktop app)",
        "Detalle": (
            "Abre la aplicación de Tableau Public en tu computador.\n\n"
            "En la esquina superior izquierda, ve a '<b>Archivo</b>' > '<b>Abrir</b>' "
            "y selecciona la plantilla que descargaste en el paso 2 (Seguimiento_Deuda.twbx)."
        ),
    },
    {
        "Paso": "5) Actualiza la fuente de datos con tu tabla de amortización",
        "Detalle": (
            "En la pestaña <b>Seguimiento Deuda</b>, realiza los siguientes pasos: \n\n"
            ".\n\n"
            "1) Ve a '<b>Datos</b>' > '<b>Tabla de Amortización</b>' > '<b>Editar fuente de datos...</b>' "
            "y selecciona la tabla de amortización del paso 1.\n\n"
            "2) Ve a '<b>Datos</b>' > '<b>Pie chart</b>' > '<b>Editar fuente de datos...</b>' "
            "y selecciona la tabla de amortización del paso 1.\n\n"
            "3) Guarda los cambios en '<b>Archivo</b>' > '<b>Guardar</b>'.\n\n"
            "Utiliza el modo presentación (🖥️) para ver el tablero en pantalla completa."
        ),
    },
    {
        "Paso": "Nota:",
        "Detalle": (
            "El dashboard se encuentra actualizado y está listo para utilizar.\n\n "
            "Si tu deuda cambia, solo genera una nueva tabla en el simulador y actualiza el archivo las veces que necesites: \n\n"
            "Ve a la pestaña '<b>Fuente de Datos</b>' y para cada fuente ('Tabla de Amortización' y 'Pie Chart') despliega el menú de "
            "opciones en la sección '<b>Conexiones</b>', da clic en '<b>Editar Conexión</b>' y selecciona la nueva tabla "
            "de amortización."
        ),
    },
]


# Convierte enlaces HTML a formato compatible con ReportLab
def html_to_pdf_text(texto: str) -> str:
    texto = re.sub(
        r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>',
        r'<link href="\1"><u><font color="blue">\2</font></u></link>',
        texto,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return texto


# Genera el PDF de la guía
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
        name="TituloPersonalizado",
        parent=styles["Title"],
        fontSize=14,
        spaceAfter=0,
    )

    elements = [
        Paragraph("Guía – Conectar la Tabla de Amortización a Tableau", title_style),
        Spacer(1, 12),
        Paragraph(
            'Elaborado por: '
            '<link href="https://www.linkedin.com/in/emilia-avila-vasconez">'
            '<u><font color="blue">Emilia Ávila</font></u>'
            "</link>",
            styles["Normal"],
        ),
        Spacer(1, 30),
    ]

    for item in GUIA_TABLEAU:
        elements.append(Paragraph(f"<b>{item['Paso']}</b>", styles["Normal"]))
        elements.append(Spacer(1, 4))

        detalle = item["Detalle"].replace("**", "")
        detalle = html_to_pdf_text(detalle)
        elements.append(Paragraph(detalle, styles["Normal"]))
        elements.append(Spacer(1, 12))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()

#st.markdown("##### 📘 Conexión en 5 pasos")

st.markdown(
    """
    <div style="font-size: 20px; font-weight: 600; margin-bottom: 28px;">
        📘 Conexión en 5 pasos
    </div>
    """,
    unsafe_allow_html=True,
)

# Guía en pantalla
for item in GUIA_TABLEAU:
    st.markdown(
        f"""
        <div style="margin-bottom: 0px;">
            <div style="font-size: 14px; font-weight: 500; margin-bottom: 3px;">
                {item['Paso']}
            </div>
            <div style="font-size: 14px; line-height: 1.7; margin-bottom: 25px; color: #8A8A8A;">
                {item['Detalle']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# Descarga de la plantilla de Tableau
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

# Descarga de la guía en PDF
pdf_bytes = build_pdf()

st.download_button(
    "Descargar guía en PDF",
    data=pdf_bytes,
    file_name="Guía - Conectar a Tableau (Simulador de Deuda).pdf",
    mime="application/pdf",
    use_container_width=True,
)
