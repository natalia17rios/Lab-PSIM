import json
import math

def filtro_pasa_bajas(dft_result, f_corte, fs):
    N = len(dft_result)
    dft_filtrada = []
    for k in range(N):
        frecuencia = dft_result[k]["frecuencia"]  # FRECUENCIA DE LA OTRA FUNCIÓN
        if abs(frecuencia) > f_corte:
            dft_filtrada.append({"real": 0, "imag": 0})
        else:
            dft_filtrada.append(dft_result[k])
    return dft_filtrada

def filtro_pasa_altas(dft_result, f_corte, fs):
    N = len(dft_result)
    dft_filtrada = []
    for k in range(N):
        frecuencia = dft_result[k]["frecuencia"]
        if abs(frecuencia) < f_corte:
            dft_filtrada.append({"real": 0, "imag": 0})
        else:
            dft_filtrada.append(dft_result[k])
    return dft_filtrada

def filtro_pasa_banda(dft_result, f_low, f_high, fs):
    N = len(dft_result)
    dft_filtrada = []
    for k in range(N):
        frecuencia = dft_result[k]["frecuencia"]
        if abs(frecuencia) < f_low or abs(frecuencia) > f_high:
            dft_filtrada.append({"real": 0, "imag": 0})
        else:
            dft_filtrada.append(dft_result[k])
    return dft_filtrada

def filtro_rechaza_banda(dft_result, f_low, f_high, fs):
    N = len(dft_result)
    dft_filtrada = []
    for k in range(N):
        frecuencia = dft_result[k]["frecuencia"]
        if f_low < abs(frecuencia) < f_high:
            dft_filtrada.append({"real": 0, "imag": 0})
        else:
            dft_filtrada.append(dft_result[k])
    return dft_filtrada

def lambda_handler(event, context):
    dft_result = event.get("dft_input", [])
    filter_type = event.get("filter")
    f_low = event.get("f_low")
    f_high = event.get("f_high")
    fs = event.get("fs")

    if not dft_result:
        return {"error": "No se proporcionó la transformada DFT de entrada."}

    if filter_type == "lowpass":
        dft_result = filtro_pasa_bajas(dft_result, f_low, fs)
    elif filter_type == "highpass":
        dft_result = filtro_pasa_altas(dft_result, f_low, fs)
    elif filter_type == "bandpass":
        dft_result = filtro_pasa_banda(dft_result, f_low, f_high, fs)
    elif filter_type == "bandstop":
        dft_result = filtro_rechaza_banda(dft_result, f_low, f_high, fs)
    
    return {"filtered_signal": dft_result}
