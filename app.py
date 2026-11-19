"""Interfaz gráfica en Streamlit para la Calculadora de ISR por Venta de Inmuebles."""

import json
from pathlib import Path
from datetime import date
import urllib.parse
import pandas as pd
import streamlit as st
import calc_inmuebles


def aplicar_estilos() -> None:
    """Inyecta CSS personalizado inspirado en los componentes SaaS Fintech (Tailwind / Shadcn)."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;600&display=swap');

        :root {
            /* Paleta Tailwind Slate & Emerald */
            --slate-950: #020617;
            --slate-900: #0f172a;
            --slate-800: #1e293b;
            --slate-700: #334155;
            --slate-600: #475569;
            --slate-500: #64748b;
            --slate-400: #94a3b8;
            --slate-200: #e2e8f0;
            --slate-100: #f1f5f9;
            --slate-50: #f8fafc;

            --emerald-600: #059669;
            --emerald-500: #10b981;
            --emerald-400: #34d399;
            --emerald-50: #ecfdf5;
            --teal-500: #14b8a6;

            --white: #ffffff;
            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;

            --radius-card: 24px;
            --radius-input: 16px;
            --radius-btn: 16px;
        }

        /* 1. Lienzo principal y tipografía base */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background-color: var(--slate-50) !important;
            color: var(--slate-900) !important;
            font-family: var(--font-sans) !important;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 960px !important;
            padding-top: 1.5rem !important;
            padding-bottom: 4rem !important;
        }

        /* 2. Limpieza de interfaz nativa de Streamlit */
        #MainMenu, footer {
            display: none !important;
        }
        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* 3. Barra superior estilo Navbar.tsx */
        .saas-navbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(255, 255, 255, 0.88);
            backdrop-filter: blur(12px);
            border: 1px solid var(--slate-200);
            border-radius: 18px;
            padding: 12px 20px;
            margin-bottom: 1.75rem;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04);
        }
        .saas-brand {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .saas-brand-icon {
            background: linear-gradient(135deg, var(--emerald-600), var(--teal-500));
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 11px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
        }
        .saas-brand-title {
            font-weight: 900;
            font-size: 1.05rem;
            color: var(--slate-900);
            letter-spacing: -0.02em;
        }
        .saas-brand-badge {
            font-size: 0.72rem;
            font-weight: 700;
            color: var(--emerald-600);
            background: var(--emerald-50);
            border: 1px solid #a7f3d0;
            padding: 2px 10px;
            border-radius: 9999px;
        }
        .saas-nav-cta {
            background: var(--emerald-600);
            color: white !important;
            text-decoration: none !important;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 8px 16px;
            border-radius: 12px;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(5, 150, 105, 0.25);
        }
        .saas-nav-cta:hover {
            background: var(--emerald-500);
            transform: translateY(-1px);
        }

        /* 4. Encabezados (Hero) */
        h1 {
            font-family: var(--font-sans) !important;
            font-weight: 900 !important;
            color: var(--slate-900) !important;
            letter-spacing: -0.03em !important;
            line-height: 1.12 !important;
            font-size: 2.3rem !important;
            margin-bottom: 0.4rem !important;
        }

        h2, h3 {
            font-family: var(--font-sans) !important;
            font-weight: 800 !important;
            color: var(--slate-900) !important;
            letter-spacing: -0.02em !important;
        }

        p, span, label, div, li {
            font-family: var(--font-sans) !important;
        }

        /* 5. Tarjeta de Formulario (IsrCalculatorForm.tsx) */
        [data-testid="stForm"] {
            background-color: var(--white) !important;
            border: 1px solid var(--slate-200) !important;
            border-radius: var(--radius-card) !important;
            padding: 2rem !important;
            box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.08) !important;
        }

        /* 6. Inputs, Number Inputs, Date Input y Selectbox (Alto contraste garantizado) */
        [data-testid="stNumberInput"] div[data-baseweb="input"],
        [data-testid="stDateInput"] div[data-baseweb="input"],
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        div[data-baseweb="input"],
        div[data-baseweb="base-input"],
        div[data-baseweb="base-input"] > div {
            background-color: var(--slate-50) !important;
            color: var(--slate-900) !important;
            border-radius: var(--radius-input) !important;
        }

        div[data-baseweb="input"],
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border: 1.5px solid var(--slate-200) !important;
            transition: all 0.18s ease !important;
        }

        div[data-baseweb="input"]:focus-within,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
            background-color: var(--white) !important;
            border-color: var(--emerald-500) !important;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.16) !important;
        }

        input,
        [data-testid="stSelectbox"] div[data-baseweb="select"] span {
            background-color: transparent !important;
            color: var(--slate-900) !important;
            -webkit-text-fill-color: var(--slate-900) !important;
            caret-color: var(--emerald-600) !important;
            font-weight: 600 !important;
            font-size: 15.5px !important;
        }

        /* Botones + / - de number_input */
        [data-testid="stNumberInput"] button {
            background-color: var(--slate-100) !important;
            color: var(--slate-700) !important;
            border-radius: 10px !important;
        }
        [data-testid="stNumberInput"] button:hover {
            background-color: var(--emerald-50) !important;
            color: var(--emerald-600) !important;
        }

        label[data-testid="stWidgetLabel"] p {
            color: var(--slate-700) !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            margin-bottom: 4px !important;
        }

        /* 7. Botón Submit Principal (Gradiente Emerald -> Teal) */
        [data-testid="stFormSubmitButton"] > button,
        .stButton > button {
            width: 100% !important;
            background: linear-gradient(90deg, var(--emerald-600), var(--teal-500)) !important;
            color: var(--white) !important;
            border: none !important;
            border-radius: var(--radius-btn) !important;
            padding: 0.85rem 1.5rem !important;
            font-weight: 800 !important;
            font-size: 16px !important;
            letter-spacing: -0.01em !important;
            box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.35) !important;
            transition: all 0.22s ease !important;
            margin-top: 0.75rem !important;
        }

        [data-testid="stFormSubmitButton"] > button:hover,
        .stButton > button:hover {
            background: linear-gradient(90deg, var(--emerald-500), var(--emerald-400)) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 14px 28px -5px rgba(16, 185, 129, 0.45) !important;
        }

        [data-testid="stFormSubmitButton"] > button p,
        .stButton > button p {
            color: var(--white) !important;
            font-weight: 800 !important;
        }

        /* 8. Tarjetas de Métricas (Estilo Dark Slate-900 como IsrResultCard.tsx) */
        div[data-testid="stMetric"] {
            background-color: var(--slate-900) !important;
            border: 1px solid var(--slate-800) !important;
            border-radius: 20px !important;
            padding: 1.35rem 1.5rem !important;
            box-shadow: 0 15px 30px -10px rgba(2, 6, 23, 0.25) !important;
        }

        div[data-testid="stMetricLabel"] p {
            color: var(--slate-400) !important;
            font-size: 12.5px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }

        div[data-testid="stMetricValue"] div {
            color: var(--white) !important;
            font-weight: 900 !important;
            font-size: 2.1rem !important;
            letter-spacing: -0.03em !important;
        }

        /* 9. Alertas con alto contraste */
        div[data-testid="stAlert"],
        div[data-testid="stAlertContainer"] {
            border-radius: 16px !important;
            padding: 1rem 1.25rem !important;
            border-width: 1px !important;
            border-left-width: 5px !important;
        }

        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] span,
        div[data-testid="stAlert"] strong {
            color: var(--slate-900) !important;
            opacity: 1 !important;
            font-size: 14.5px !important;
            line-height: 1.55 !important;
        }

        div[data-testid="stAlert"]:has(div[data-testid="stAlertContentSuccess"]) {
            background-color: var(--emerald-50) !important;
            border-color: #a7f3d0 !important;
            border-left-color: var(--emerald-600) !important;
        }

        div[data-testid="stAlert"]:has(div[data-testid="stAlertContentWarning"]) {
            background-color: #fffbeb !important;
            border-color: #fde68a !important;
            border-left-color: #d97706 !important;
        }

        div[data-testid="stAlert"]:has(div[data-testid="stAlertContentInfo"]) {
            background-color: #eff6ff !important;
            border-color: #bfdbfe !important;
            border-left-color: #2563eb !important;
        }

        div[data-testid="stAlert"]:has(div[data-testid="stAlertContentError"]) {
            background-color: #fef2f2 !important;
            border-color: #fecaca !important;
            border-left-color: #dc2626 !important;
        }

        /* 10. Expander (Desglose del cálculo) */
        [data-testid="stExpander"] {
            background-color: var(--white) !important;
            border: 1px solid var(--slate-200) !important;
            border-radius: 16px !important;
            overflow: hidden !important;
            margin-top: 0.75rem !important;
        }
        [data-testid="stExpander"] summary p {
            font-weight: 700 !important;
            color: var(--slate-800) !important;
        }

        /* 11. Botón WhatsApp High-Conversion CTA */
        .wa-cta-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            background: linear-gradient(90deg, var(--emerald-500), var(--teal-500));
            color: var(--slate-950) !important;
            text-decoration: none !important;
            font-weight: 800;
            font-size: 16px;
            padding: 16px 24px;
            border-radius: 16px;
            margin-top: 1rem;
            box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.35);
            transition: all 0.25s ease;
        }
        .wa-cta-btn:hover {
            background: linear-gradient(90deg, var(--emerald-400), #2dd4bf);
            transform: scale(1.01);
            box-shadow: 0 14px 30px -5px rgba(16, 185, 129, 0.45);
        }
        .wa-trust-note {
            text-align: center;
            font-size: 12px;
            color: var(--slate-500);
            margin-top: 8px;
            margin-bottom: 1.5rem;
        }

        /* 12. Footer institucional estilo Footer.tsx */
        .saas-footer {
            background-color: var(--slate-950);
            color: var(--slate-400);
            border-radius: 20px;
            padding: 24px 28px;
            margin-top: 3rem;
            font-size: 12px;
            line-height: 1.6;
        }
        .saas-footer strong {
            color: var(--white);
        }
        .saas-footer-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            padding-bottom: 14px;
            margin-bottom: 14px;
            border-bottom: 1px solid var(--slate-800);
        }
        .saas-footer-brand {
            color: var(--white);
            font-weight: 800;
            font-size: 14px;
        }
        .saas-footer-badges {
            color: var(--emerald-400);
            font-weight: 600;
            font-size: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def cargar_configuracion() -> dict:
    """Lee el archivo JSON con las reglas fiscales, enlaces y textos de la interfaz."""
    ruta_cfg = Path(__file__).parent / "config_inmuebles.json"
    with open(ruta_cfg, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=3600)
def cargar_tablas_fiscales(url_ipc: str, url_udi: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Descarga y normaliza las series históricas de INPC y UDI desde Google Sheets."""
    df_ipc = pd.read_csv(url_ipc)
    df_ipc.columns = [c.strip() for c in df_ipc.columns]
    df_ipc["Fecha_dt"] = pd.to_datetime(df_ipc[df_ipc.columns[0]], errors="coerce")
    df_ipc["Valor_INPC"] = pd.to_numeric(
        df_ipc[df_ipc.columns[1]].astype(str).str.replace(",", ""), errors="coerce"
    )
    df_ipc = df_ipc.dropna(subset=["Fecha_dt", "Valor_INPC"]).sort_values("Fecha_dt").reset_index(drop=True)

    df_udi = pd.read_csv(url_udi)
    df_udi.columns = [c.strip() for c in df_udi.columns]
    df_udi["Fecha_dt"] = pd.to_datetime(df_udi[df_udi.columns[0]], errors="coerce")
    df_udi["Valor_UDI"] = pd.to_numeric(
        df_udi[df_udi.columns[1]].astype(str).str.replace(",", ""), errors="coerce"
    )
    df_udi = df_udi.dropna(subset=["Fecha_dt", "Valor_UDI"]).sort_values("Fecha_dt").reset_index(drop=True)

    return df_ipc, df_udi


def crear_enlace_whatsapp(numero: str, texto: str) -> str:
    """Construye la URL codificada para iniciar conversación en WhatsApp."""
    return f"https://wa.me/{numero}?text={urllib.parse.quote(texto)}"


def renderizar_boton_whatsapp(numero: str, mensaje: str, etiqueta: str) -> None:
    """Dibuja un botón estilizado de alta conversión con enlace directo a WhatsApp."""
    url = crear_enlace_whatsapp(numero, mensaje)
    st.markdown(
        f"""
        <a href="{url}" target="_blank" rel="noopener noreferrer" class="wa-cta-btn">
            <span>{etiqueta}</span>
            <span>→</span>
        </a>
        <div class="wa-trust-note">
            🛡️ Consulta confidencial con fiscalistas inmobiliarios certificados.
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- Configuración inicial ---
st.set_page_config(page_title="Calculadora de ISR | Venta de Inmueble", page_icon="🏠", layout="centered")
aplicar_estilos()

config = cargar_configuracion()
textos = config["textos_interfaz"]
contacto = config["contacto"]
fuentes = config["fuentes_datos"]

# Barra superior estilo Navbar.tsx
nav_wa_url = crear_enlace_whatsapp(
    contacto["whatsapp_numero"],
    "Hola, busco asesoría para el cálculo y exención de ISR por venta de inmueble.",
)
st.markdown(
    f"""
    <div class="saas-navbar">
        <div class="saas-brand">
            <div class="saas-brand-icon">🏠</div>
            <span class="saas-brand-title">ISR Inmuebles</span>
            <span class="saas-brand-badge">México 2026</span>
        </div>
        <a href="{nav_wa_url}" target="_blank" rel="noopener noreferrer" class="saas-nav-cta">
            💬 Consulta WhatsApp
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.title(textos["titulo"])
st.markdown(textos["subtitulo"])

try:
    df_ipc, df_udi = cargar_tablas_fiscales(fuentes["url_ipc_csv"], fuentes["url_udi_csv"])
    datos_cargados = True
except Exception as e:
    st.error(f"Error al conectar con las tablas de INPC/UDI. Verifique su conexión: {e}")
    datos_cargados = False

if datos_cargados:
    with st.form("form_calculadora"):
        st.subheader("Datos de la Operación")

        col_form1, col_form2 = st.columns(2)
        with col_form1:
            precio_venta = st.number_input("Precio de venta pactado (MXN)", min_value=1.0, value=3500000.0, step=50000.0)
            fecha_adq = st.date_input(
                "Fecha original de adquisición",
                min_value=date(1970, 1, 1),
                max_value=date.today(),
                value=date(2015, 6, 15),
            )
            costo_adq = st.number_input("Costo de adquisición en escrituras (MXN)", min_value=0.0, value=1800000.0, step=50000.0)

        with col_form2:
            gastos_venta = st.number_input("Gastos notariales / comisiones deducibles (MXN)", min_value=0.0, value=0.0, step=10000.0)
            tipo_adquisicion = st.selectbox("¿Cómo adquiriste el inmueble?", ["Compraventa", "Herencia o Donación"])
            es_casa = st.selectbox("¿Es tu casa habitación (donde vives actualmente)?", ["Sí", "No"])
            reside_mx = st.selectbox("¿Resides fiscalmente en México?", ["Sí", "No"])

        submit_btn = st.form_submit_button("Calcular ISR Estimado", use_container_width=True)

    if submit_btn:
        st.markdown("---")
        resultado = calc_inmuebles.calcular_isr_inmueble(
            precio_venta=precio_venta,
            fecha_adquisicion=fecha_adq,
            costo_historico=costo_adq,
            gastos_venta=gastos_venta,
            tipo_adquisicion=tipo_adquisicion,
            es_casa_habitacion=(es_casa == "Sí"),
            es_residente_mx=(reside_mx == "Sí"),
            df_ipc=df_ipc,
            df_udi=df_udi,
            config=config,
        )

        wa_num = contacto["whatsapp_numero"]
        plantillas = contacto["mensajes_whatsapp"]
        precio_fmt = f"${precio_venta:,.2f}"

        # 1. Caso Herencia o Donación
        if resultado.caso == "herencia_donacion":
            st.warning("⚠️ Operación sujeta a cálculo especializado")
            st.info(textos["aviso_herencia"])
            renderizar_boton_whatsapp(
                wa_num,
                plantillas["herencia_donacion"],
                "💬 Agendar Asesoría Personalizada vía WhatsApp",
            )

        # 2. Caso Residente en el Extranjero
        elif resultado.caso == "extranjero":
            tasa_pct = int(config["parametros_fiscales"]["tasa_retencion_extranjero_bruta"] * 100)
            st.subheader("Resultado Preliminar: Residente en el Extranjero")
            st.metric(f"Retención estándar directa ({tasa_pct}%)", f"${resultado.isr_estimado:,.2f} MXN")
            st.info(f"💡 **Atención:** {textos['aviso_extranjero']}")
            renderizar_boton_whatsapp(
                wa_num,
                plantillas["extranjero"].format(precio_fmt=precio_fmt),
                "💬 Reducir mi Pago de ISR (Agendar WhatsApp)",
            )

        # 3. Caso Casa Habitación 100% Exenta
        elif resultado.caso == "casa_habitacion_exenta":
            udis_fmt = f"{config['parametros_fiscales']['udis_exentas_casa_habitacion']:,.0f}"
            st.subheader("Resultado Preliminar")
            st.success("🎉 Tu operación podría estar 100% exenta de ISR.")
            st.metric("ISR Estimado a Pagar", "$0.00 MXN")
            st.markdown(
                f"* **Límite exento de Ley ({udis_fmt} UDIs):** ~${resultado.limite_exento:,.2f} MXN\n"
                f"* **Precio de Venta:** {precio_fmt} MXN\n"
                f"* {textos['aviso_exencion_casa']}"
            )
            renderizar_boton_whatsapp(
                wa_num,
                plantillas["casa_exenta"].format(precio_fmt=precio_fmt),
                "💬 Confirmar Exención vía WhatsApp",
            )

        # 4. Caso Casa Habitación Mixta o Régimen General
        else:
            st.subheader("Resultado del Cálculo Preliminar")
            c1, c2 = st.columns(2)
            c1.metric("ISR Estimado Preliminar", f"${resultado.isr_estimado:,.2f} MXN")
            c2.metric("Ganancia Estimada", f"${resultado.ganancia:,.2f} MXN")

            with st.expander("Ver desglose del cálculo estimado"):
                st.write(f"- **Factor de actualización aplicado (INPC):** {resultado.factor_actualizacion:.4f}")
                st.write(f"- **Costo de adquisición actualizado:** ${resultado.costo_actualizado:,.2f} MXN")
                if resultado.caso == "casa_habitacion_mixta":
                    udis_fmt = f"{config['parametros_fiscales']['udis_exentas_casa_habitacion']:,.0f}"
                    st.write(f"- **Límite exento aplicado:** ${resultado.limite_exento:,.2f} MXN")
                    st.write(f"- El cálculo gravó únicamente el excedente respecto a las {udis_fmt} UDIs.")

            st.warning(f"⚠️ **Aviso Legal:** {textos['aviso_general']}")
            isr_fmt = f"${resultado.isr_estimado:,.2f}"
            renderizar_boton_whatsapp(
                wa_num,
                plantillas["general"].format(isr_fmt=isr_fmt, precio_fmt=precio_fmt),
                "💬 Agendar Asesoría Fiscal vía WhatsApp",
            )

# Pie de página institucional estilo Footer.tsx
st.markdown(
    """
    <div class="saas-footer">
        <div class="saas-footer-top">
            <span class="saas-footer-brand">🧮 Calculadora ISR Inmuebles México</span>
            <span class="saas-footer-badges">🔒 Datos Seguros &nbsp;•&nbsp; 🛡️ Asesoría Profesional</span>
        </div>
        <p style="margin-bottom: 8px;">
            <strong>Descargo de responsabilidad:</strong> Esta calculadora es una herramienta digital de acceso gratuito orientada a proporcionar estimaciones aproximadas del Impuesto Sobre la Renta (ISR) por enajenación de bienes inmuebles en México conforme al Título IV y Título V de la LISR. Las cifras mostradas son de carácter meramente informativo y pedagógico.
        </p>
        <p style="margin: 0;">
            No constituyen asesoría legal, contable ni dictamen tributario definitivo. Toda operación inmobiliaria debe ser dictaminada y calculada formalmente por el Notario Público autorizante previo a la firma de la escritura.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)