import json
import math
import numpy as np
from scipy.signal import butter, lfilter

# ----------------- Generar señal ------------------
def generar_senal(fs, T, f1, f2, A1, A2):
    N = int(fs * T)
    signal = [A1 * math.sin(2 * math.pi * f1 * t / fs) + A2 * math.sin(2 * math.pi * f2 * t / fs) for t in range(N)]
    return signal

# ----------------- Filtros FIR ------------------
def filtro_fir_pbajas(signal, fs, fc, L=101):
    n = np.arange(L)
    h_ideal = np.sinc(2 * fc / fs * (n - (L - 1) / 2))
    w = 0.54 - 0.46 * np.cos(2 * np.pi * n / (L - 1))
    h = h_ideal * w
    h /= np.sum(h)
    return np.convolve(signal, h, mode="same").tolist()

def filtro_fir_paltas(signal, fs, fc, L=101):
    n = np.arange(L)
    h_lp = np.sinc(2 * fc / fs * (n - (L - 1) / 2))
    w = 0.54 - 0.46 * np.cos(2 * np.pi * n / (L - 1))
    h_lp *= w
    h_lp /= np.sum(h_lp)
    delta = np.zeros(L)
    delta[(L - 1) // 2] = 1
    h_hp = delta - h_lp
    return np.convolve(signal, h_hp, mode="same").tolist()

def filtro_fir_pbanda(signal, fs, f_low, f_high, L=101):
    n = np.arange(L)
    h_high = np.sinc(2 * f_high / fs * (n - (L - 1) / 2))
    h_low = np.sinc(2 * f_low / fs * (n - (L - 1) / 2))
    w = 0.54 - 0.46 * np.cos(2 * np.pi * n / (L - 1))
    h_high *= w
    h_low *= w
    h_bp = h_high - h_low
    h_bp /= np.sum(h_bp)
    return np.convolve(signal, h_bp, mode="same").tolist()

def filtro_fir_rbanda(signal, fs, f_low, f_high, L=101):
    n = np.arange(L)
    h_low = np.sinc(2 * f_low / fs * (n - (L - 1) / 2))
    h_high = np.sinc(2 * f_high / fs * (n - (L - 1) / 2))
    w = 0.54 - 0.46 * np.cos(2 * np.pi * n / (L - 1))
    h_low *= w
    h_high *= w
    h_rb = h_low + h_high
    h_rb /= np.sum(h_rb)
    return np.convolve(signal, h_rb, mode="same").tolist()

# ----------------- Filtros IIR ------------------
def filtro_iir_pbajas(signal, fs, fc, order=2):
    b, a = butter(N=order, Wn=fc / (fs / 2), btype='low')
    return lfilter(b, a, signal).tolist()

def filtro_iir_paltas(signal, fs, fc, order=2):
    b, a = butter(N=order, Wn=fc / (fs / 2), btype='high')
    return lfilter(b, a, signal).tolist()

def filtro_iir_pbanda(signal, fs, f_low, f_high, order=2):
    b, a = butter(N=order, Wn=[f_low, f_high], btype='bandpass', fs=fs)
    return lfilter(b, a, signal).tolist()

def filtro_iir_rbanda(signal, fs, f_low, f_high, order=2):
    b, a = butter(N=order, Wn=[f_low, f_high], btype='bandstop', fs=fs)
    return lfilter(b, a, signal).tolist()

# ----------------- Manejador principal ------------------
def handler(event, context):
    print("Evento recibido:", event)

    if isinstance(event['body'], str):
        body = json.loads(event['body'])
    else:
        body = event['body']

    fs = body['fs']
    T = body['T']
    f1 = body['f1']
    f2 = body['f2']
    A1 = body['A1']
    A2 = body['A2']
    filter_type = body.get('filter')
    f_low = body.get('f_low')
    f_high = body.get('f_high')
    fc = body.get('f_corte')

    signal = generar_senal(fs, T, f1, f2, A1, A2)
    signal_np = np.array(signal, dtype=float)

    try:
        if filter_type == "lowpass_fir":
            signal_filtrada = filtro_fir_pbajas(signal_np, fs, fc)
        elif filter_type == "highpass_fir":
            signal_filtrada = filtro_fir_paltas(signal_np, fs, fc)
        elif filter_type == "bandpass_fir":
            signal_filtrada = filtro_fir_pbanda(signal_np, fs, f_low, f_high)
        elif filter_type == "bandstop_fir":
            signal_filtrada = filtro_fir_rbanda(signal_np, fs, f_low, f_high)
        elif filter_type == "lowpass_iir":
            signal_filtrada = filtro_iir_pbajas(signal_np, fs, fc)
        elif filter_type == "highpass_iir":
            signal_filtrada = filtro_iir_paltas(signal_np, fs, fc)
        elif filter_type == "bandpass_iir":
            signal_filtrada = filtro_iir_pbanda(signal_np, fs, f_low, f_high)
        elif filter_type == "bandstop_iir":
            signal_filtrada = filtro_iir_rbanda(signal_np, fs, f_low, f_high)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Filtro no reconocido'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'signal_filtrada': signal_filtrada})
        }

    except Exception as e:
        print("Error en filtrado:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
