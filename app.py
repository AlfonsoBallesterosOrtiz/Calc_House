import streamlit as st
import pandas as pd
from datetime import datetime, date
import urllib.parse

# --- Configuración de página ---
st.set_page_config(
    page_title="Calculadora de ISR | Venta de Inmueble",
    page_icon="🏠",
    layout="centered"
)

# --- Constantes y Enlaces ---
URL_IPC_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQE6aYmYLBOGcSWvgBy8g62seNRKLYZ1zuy_xG53lwZxjhvBX_AEUonbBEJG03vYJSA1uVGwah7lT_Y/pub?gid=0&single=true&output=csv"
URL_UDI_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQItR8J8hKtqMQsOnars1F-JYlOCrHg-8B4QY-ydFW3is4ce1sKY-ESwl4zR62o3u72XPkvQ9anDT3F/pub?gid=0&single=true&output=csv"

WHATSAPP_NUM = "525527602188"
TASA_ESTIMADA = 0.25
UDIS_EXENTAS_CASA_HABITACION = 700000

# --- Carga y Normalización de Datos con Caché ---
@st.cache_data(ttl=3600)
def cargar_tablas_fiscales(url_ipc: str, url_udi: str):
    # Carga de IPC / INPC
    df_ipc = pd.read_csv(url_ipc)
    df_ipc.columns = [c.strip() for c in df_ipc.columns]
    col_fecha_ipc = df_ipc.columns[0]
    col_valor_ipc = df_ipc.columns[1]
    
    df_ipc['Fecha_dt'] = pd.to_datetime(df_ipc[col_fecha_ipc], errors='coerce')
    df_ipc['Valor_INPC'] = pd.to_numeric(df_ipc[col_valor_ipc].astype(str).str.replace(',', ''), errors='coerce')
    df_ipc = df_ipc.dropna(subset=['Fecha_dt', 'Valor_INPC']).sort_values('Fecha_dt').reset_index(drop=True)

    # Carga de UDI
    df_udi = pd.read_csv(url_udi)
    df_udi.columns = [c.strip() for c in df_udi.columns]
    col_fecha_udi = df_udi.columns[0]
    col_valor_udi = df_udi.columns[1]
    
    df_udi['Fecha_dt'] = pd.to_datetime(df_udi[col_fecha_udi], errors='coerce')
    df_udi['Valor_UDI'] = pd.to_numeric(df_udi[col_valor_udi].astype(str).str.replace(',', ''), errors='coerce')
    df_udi = df_udi.dropna(subset=['Fecha_dt', 'Valor_UDI']).sort_values('Fecha_dt').reset_index(drop=True)

    return df_ipc, df_udi

# --- Motor de Cálculo Fiscal (Lógica pura desacoplada) ---
def calcular_isr_inmueble(
    precio_venta: float,
    fecha_adquisicion: date,
    costo_historico: float,
    gastos_venta: float,
    es_casa_habitacion: bool,
    es_residente_mx: bool,
    df_ipc: pd.DataFrame,
    df_udi: pd.DataFrame
) -> dict:
    
    # 1. Caso Residente en el Extranjero (Título V)
    if not es_residente_mx:
        monto_retencion = precio_venta * TASA_ESTIMADA
        return {
            "caso": "extranjero",
            "isr_estimado": monto_retencion,
            "ganancia": None,
            "costo_actualizado": None,
            "factor_actualizacion": None,
            "exento": False,
            "limite_exento": None
        }

    # 2. Obtención de índices INPC
    # INPC de venta: el más reciente disponible
    inpc_venta_row = df_ipc.iloc[-1]
    inpc_fecha_venta = inpc_venta_row['Valor_INPC']
    
    # INPC de adquisición: fila con la fecha más cercana a la compra
    fecha_adq_dt = pd.to_datetime(fecha_adquisicion)
    idx_mas_cercano = (df_ipc['Fecha_dt'] - fecha_adq_dt).abs().idxmin()
    inpc_fecha_adquisicion = df_ipc.loc[idx_mas_cercano, 'Valor_INPC']
    
    # Factor de actualización (mínimo 1.0)
    factor_actualizacion = max(1.0, float(inpc_fecha_venta / inpc_fecha_adquisicion))
    costo_actualizado = costo_historico * factor_actualizacion
    
    # Ganancia bruta antes de exenciones
    ganancia = max(0.0, precio_venta - costo_actualizado - gastos_venta)

    # 3. Tratamiento Casa Habitación
    if es_casa_habitacion:
        # Último valor UDI disponible en la tabla
        valor_udi_reciente = float(df_udi.iloc[-1]['Valor_UDI'])
        limite_exento = UDIS_EXENTAS_CASA_HABITACION * valor_udi_reciente
        
        if precio_venta <= limite_exento:
            return {
                "caso": "casa_habitacion_exenta",
                "isr_estimado": 0.0,
                "ganancia": ganancia,
                "costo_actualizado": costo_actualizado,
                "factor_actualizacion": factor_actualizacion,
                "exento": True,
                "limite_exento": limite_exento
            }
        else:
            proporcion_gravable = (precio_venta - limite_exento) / precio_venta
            ganancia_gravable = ganancia * proporcion_gravable
            isr_estimado = ganancia_gravable * TASA_ESTIMADA
            return {
                "caso": "casa_habitacion_mixta",
                "isr_estimado": isr_estimado,
                "ganancia": ganancia,
                "costo_actualizado": costo_actualizado,
                "factor_actualizacion": factor_actualizacion,
                "exento": False,
                "limite_exento": limite_exento
            }
    else:
        # Inmueble que no es casa habitación
        isr_estimado = ganancia * TASA_ESTIMADA
        return {
            "caso": "general",
            "isr_estimado": isr_estimado,
            "ganancia": ganancia,
            "costo_actualizado": costo_actualizado,
            "factor_actualizacion": factor_actualizacion,
            "exento": False,
            "limite_exento": 0.0
        }

# --- Generador de URL WhatsApp ---
def crear_enlace_whatsapp(texto: str) -> str:
    base = f"https://wa.me/{WHATSAPP_NUM}?text="
    return base + urllib.parse.quote(texto)

# --- Interfaz de Usuario ---
st.title("Calculadora de ISR Estimado por Venta de Inmuebles")
st.markdown("Calcula en 1 minuto un estimado preliminar del impuesto aplicable a la venta de tu casa, departamento o terreno en México.")

# Intentar carga de datos
try:
    df_ipc, df_udi = cargar_tablas_fiscales(URL_IPC_CSV, URL_UDI_CSV)
    datos_cargados = True
except Exception as e:
    st.error(f"Error al conectar con las tablas del SAT/Banxico. Verifique la conexión: {e}")
    datos_cargados = False

if datos_cargados:
    with st.form("form_calculadora"):
        st.subheader("Datos de la Operación")
        
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            precio_venta = st.number_input("Precio de venta pactado (MXN)", min_value=1.0, value=3500000.0, step=50000.0)
            fecha_adq = st.date_input("Fecha original de adquisición", min_value=date(1970, 1, 1), max_value=date.today(), value=date(2015, 6, 15))
            costo_adq = st.number_input("Costo de adquisición en escrituras (MXN)", min_value=0.0, value=1800000.0, step=50000.0)

        with col_form2:
            gastos_venta = st.number_input("Gastos notariales / comisiones deducibles (MXN)", min_value=0.0, value=0.0, step=10000.0)
            tipo_adquisicion = st.selectbox("¿Cómo adquiriste el inmueble?", ["Compraventa", "Herencia o Donación"])
            es_casa = st.selectbox("¿Es tu casa habitación (donde vives actualmente)?", ["Sí", "No"])
            reside_mx = st.selectbox("¿Resides fiscalmente en México?", ["Sí", "No"])

        submit_btn = st.form_submit_button("Calcular ISR Estimado")

    if submit_btn:
        st.markdown("---")
        
        # Filtro de descarte: Herencia / Donación
        if tipo_adquisicion == "Herencia o Donación":
            st.warning("⚠️ Operación sujeta a cálculo especializado")
            st.info("Las adquisiciones por herencia o donación tienen reglas especiales sobre costo fiscal y exenciones que no entran en este cotizador genérico.")
            
            msg_herencia = "Hola, tengo un inmueble adquirido por herencia/donación y busco una consulta personalizada para calcular mi ISR."
            st.markdown(f'''
                <a href="{crear_enlace_whatsapp(msg_herencia)}" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; font-weight:bold; border-radius:5px; cursor:pointer;">
                        💬 Agendar Asesoría Personalizada vía WhatsApp
                    </button>
                </a>
            ''', unsafe_allow_html=True)

        else:
            # Ejecución del cálculo
            resultado = calcular_isr_inmueble(
                precio_venta=precio_venta,
                fecha_adquisicion=fecha_adq,
                costo_historico=costo_adq,
                gastos_venta=gastos_venta,
                es_casa_habitacion=(es_casa == "Sí"),
                es_residente_mx=(reside_mx == "Sí"),
                df_ipc=df_ipc,
                df_udi=df_udi
            )

            # Caso Extranjero
            if resultado["caso"] == "extranjero":
                st.subheader("Resultado Preliminar: Residente en el Extranjero")
                st.metric("Retención estándar directa (25%)", f"${resultado['isr_estimado']:,.2f} MXN")
                
                st.info(
                    "💡 **Atención:** Por regla general del Título V, la ley prevé una retención del 25% sobre el precio de venta total. "
                    "Sin embargo, si te acercas a nosotros te podemos decir el paso a paso para que este monto goce de los beneficios "
                    "que te da la ley y el monto que pagues se reduzca sustancialmente si cumples con lo que revisaremos en una consulta personalizada."
                )
                
                msg_extranjero = f"Hola, resido fuera de México. Vendí/venderé un inmueble en ${precio_venta:,.2f} y busco la estrategia para optimizar la retención de ISR."
                st.markdown(f'''
                    <a href="{crear_enlace_whatsapp(msg_extranjero)}" target="_blank" style="text-decoration:none;">
                        <button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; font-weight:bold; border-radius:5px; cursor:pointer;">
                            💬 Reducir mi Pago de ISR (Agendar WhatsApp)
                        </button>
                    </a>
                ''', unsafe_allow_html=True)

            # Caso Casa Habitación 100% Exenta
            elif resultado["caso"] == "casa_habitacion_exenta":
                st.subheader("Resultado Preliminar")
                st.success("🎉 Tu operación podría estar 100% exenta de ISR.")
                st.metric("ISR Estimado a Pagar", "$0.00 MXN")
                st.markdown(f"""
                * **Límite exento de Ley (700,000 UDIs):** ~${resultado['limite_exento']:,.2f} MXN  
                * **Precio de Venta:** ${precio_venta:,.2f} MXN  
                * Este es un estimado preliminar que debe confirmarse comprobando requisitos formales (comprobantes de domicilio fiscales, periodicidad de 3 años, etc.).
                """)
                
                msg_exento = f"Hola, hice el cálculo estimado de ISR para mi casa habitación (${precio_venta:,.2f}) y califico para exención. Quiero confirmar los requisitos en una asesoría."
                st.markdown(f'''
                    <a href="{crear_enlace_whatsapp(msg_exento)}" target="_blank" style="text-decoration:none;">
                        <button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; font-weight:bold; border-radius:5px; cursor:pointer;">
                            💬 Confirmar Exención vía WhatsApp
                        </button>
                    </a>
                ''', unsafe_allow_html=True)

            # Caso Casa Habitación Mixta o Régimen General
            else:
                st.subheader("Resultado del Cálculo Preliminar")
                
                c1, c2 = st.columns(2)
                c1.metric("ISR Estimado Preliminar", f"${resultado['isr_estimado']:,.2f} MXN")
                c2.metric("Ganancia Estimada", f"${resultado['ganancia']:,.2f} MXN")

                with st.expander("Ver desglose del cálculo estimado"):
                    st.write(f"- **Factor de actualización aplicado (INPC):** {resultado['factor_actualizacion']:.4f}")
                    st.write(f"- **Costo de adquisición actualizado:** ${resultado['costo_actualizado']:,.2f} MXN")
                    if resultado["caso"] == "casa_habitacion_mixta":
                        st.write(f"- **Límite exento aplicado:** ${resultado['limite_exento']:,.2f} MXN")
                        st.write("- El cálculo gravó únicamente el excedente del precio respecto a las 700,000 UDIs.")

                st.warning("⚠️ **Aviso Legal:** Esta cifra es una aproximación paramétrica con fines orientativos y no constituye una declaración formal ni sustituye el cálculo notarial definitivo.")

                msg_general = f"Hola, coticé un ISR estimado de ${resultado['isr_estimado']:,.2f} para la venta de un inmueble (${precio_venta:,.2f}) y quiero agendar una asesoría para revisar deducciones y estrategia."
                st.markdown(f'''
                    <a href="{crear_enlace_whatsapp(msg_general)}" target="_blank" style="text-decoration:none;">
                        <button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; font-weight:bold; border-radius:5px; cursor:pointer;">
                            💬 Agendar Asesoría Fiscal vía WhatsApp
                        </button>
                    </a>
                ''', unsafe_allow_html=True)
