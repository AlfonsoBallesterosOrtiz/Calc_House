"""Motor de cálculo determinista para estimar el ISR por enajenación de inmuebles en México."""

from dataclasses import dataclass
from datetime import date
from typing import Optional
import pandas as pd


@dataclass(frozen=True)
class ResultadoInmueble:
    """Estructura inmutable con los resultados del cálculo preliminar de ISR."""
    caso: str
    isr_estimado: float
    ganancia: Optional[float]
    costo_actualizado: Optional[float]
    factor_actualizacion: Optional[float]
    exento: bool
    limite_exento: Optional[float]


def calcular_isr_inmueble(
    precio_venta: float,
    fecha_adquisicion: date,
    costo_historico: float,
    gastos_venta: float,
    tipo_adquisicion: str,
    es_casa_habitacion: bool,
    es_residente_mx: bool,
    df_ipc: pd.DataFrame,
    df_udi: pd.DataFrame,
    config: dict
) -> ResultadoInmueble:
    """Calcula el ISR estimado leyendo exclusivamente las tasas y topes desde el JSON de configuración."""
    params = config["parametros_fiscales"]

    # 1. Filtro de caso especial: Herencia o Donación (subrogación de costo fiscal)
    if tipo_adquisicion == "Herencia o Donación":
        return ResultadoInmueble(
            caso="herencia_donacion",
            isr_estimado=0.0,
            ganancia=None,
            costo_actualizado=None,
            factor_actualizacion=None,
            exento=False,
            limite_exento=None
        )

    # 2. Caso Residente en el Extranjero (Título V LISR)
    if not es_residente_mx:
        tasa_ext = float(params["tasa_retencion_extranjero_bruta"])
        monto_retencion = round(precio_venta * tasa_ext, 2)
        return ResultadoInmueble(
            caso="extranjero",
            isr_estimado=monto_retencion,
            ganancia=None,
            costo_actualizado=None,
            factor_actualizacion=None,
            exento=False,
            limite_exento=None
        )

    # 3. Obtención de índices INPC y factor de actualización
    inpc_fecha_venta = float(df_ipc.iloc[-1]["Valor_INPC"])
    fecha_adq_dt = pd.to_datetime(fecha_adquisicion)
    idx_mas_cercano = (df_ipc["Fecha_dt"] - fecha_adq_dt).abs().idxmin()
    inpc_fecha_adquisicion = float(df_ipc.loc[idx_mas_cercano, "Valor_INPC"])

    piso_factor = float(params["factor_actualizacion_minimo"])
    factor_actualizacion = max(piso_factor, inpc_fecha_venta / inpc_fecha_adquisicion)
    costo_actualizado = round(costo_historico * factor_actualizacion, 2)

    # Ganancia bruta antes de exenciones
    ganancia = round(max(0.0, precio_venta - costo_actualizado - gastos_venta), 2)
    tasa_preliminar = float(params["tasa_estimada_preliminar"])

    # 4. Tratamiento Casa Habitación (Art. 93, Fracc. XIX, inciso a LISR)
    if es_casa_habitacion:
        valor_udi_reciente = float(df_udi.iloc[-1]["Valor_UDI"])
        udis_exentas = float(params["udis_exentas_casa_habitacion"])
        limite_exento = round(udis_exentas * valor_udi_reciente, 2)

        if precio_venta <= limite_exento:
            return ResultadoInmueble(
                caso="casa_habitacion_exenta",
                isr_estimado=0.0,
                ganancia=ganancia,
                costo_actualizado=costo_actualizado,
                factor_actualizacion=factor_actualizacion,
                exento=True,
                limite_exento=limite_exento
            )

        proporcion_gravable = (precio_venta - limite_exento) / precio_venta
        ganancia_gravable = ganancia * proporcion_gravable
        isr_estimado = round(ganancia_gravable * tasa_preliminar, 2)
        return ResultadoInmueble(
            caso="casa_habitacion_mixta",
            isr_estimado=isr_estimado,
            ganancia=ganancia,
            costo_actualizado=costo_actualizado,
            factor_actualizacion=factor_actualizacion,
            exento=False,
            limite_exento=limite_exento
        )

    # 5. Inmueble que no es casa habitación (Régimen General)
    isr_estimado = round(ganancia * tasa_preliminar, 2)
    return ResultadoInmueble(
        caso="general",
        isr_estimado=isr_estimado,
        ganancia=ganancia,
        costo_actualizado=costo_actualizado,
        factor_actualizacion=factor_actualizacion,
        exento=False,
        limite_exento=0.0
    )