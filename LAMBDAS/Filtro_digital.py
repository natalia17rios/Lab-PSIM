import math
import numpy as np
import matplotlib.pyplot as plt


def filtro_fir_pbajas(signal, fs, fc, L=101):
    n = np.arange(L)
    h_ideal = np.sinc(2 * fc / fs * (n - (L - 1) / 2))
    w = 0.54 - 0.46 * np.cos(2 * np.pi * n / (L - 1))
    h = h_ideal * w
    h /= np.sum(h)
    y = np.convolve(signal, h, mode="same")
    return y, h

def filtro_fir_paltas(signal, fs, fc, L=101):
    n = np.arange(L)
    h_lp = np.sinc(2 * fc / fs * (n - (L - 1) / 2))
    w = 0.54 - 0.46 * np.cos(2 * np.pi * n / (L - 1))
    h_lp *= w
    h_lp /= np.sum(h_lp)
    delta = np.zeros(L)
    delta[(L - 1) // 2] = 1
    h_hp = delta - h_lp
    y = np.convolve(signal, h_hp, mode="same")
    return y, h_hp

def filtro_fir_pbanda(signal, fs, f_low, f_high, L=101):
    _, h_high = filtro_fir_pbajas(np.zeros_like(signal), fs, f_high, L)
    _, h_low = filtro_fir_pbajas(np.zeros_like(signal), fs, f_low, L)
    h_bp = h_high - h_low
    y = np.convolve(signal, h_bp, mode="same")
    return y, h_bp

def filtro_fir_rbanda(signal, fs, f_low, f_high, L=101):
    _, h_lp = filtro_fir_pbajas(np.zeros_like(signal), fs, f_low, L)
    _, h_hp = filtro_fir_paltas(np.zeros_like(signal), fs, f_high, L)
    h_rb = h_lp + h_hp
    y = np.convolve(signal, h_rb, mode="same")
    return y, h_rb

def generar_senal(fs, T, f1, f2, A1, A2):
    N = int(fs * T)
    signal = [A1 * math.sin(2 * math.pi * f1 * t / fs) + A2 * math.sin(2 * math.pi * f2 * t / fs) for t in range(N)]
    return signal

# PARÁMETROS:

fs = 500      # Frecuencia de muestreo en Hz
T = 0.5       # Duración de la señal 
f1 = 10       # Frecuencia 1 
f2 = 50       # Frecuencia 2 
A1 = 1        # Amplitud 1
A2 = 0.5      # Amplitud 2

f_corte = 30  # Frecuencia de corte (pasa bajas/altas)
f_low_ = 40 #Límite inferior (pasa/rechaza banda)
f_high_ = 60 #Límite superior (pasa/rechaza banda)
L = 101       # Número de coeficientes del filtro
tipo_filtro = "bandstop"  # "lowpass", "highpass", "bandpass", "bandstop"


signal = generar_senal(fs, T, f1, f2, A1, A2)

if tipo_filtro == "lowpass":
    signal_filtrada, h = filtro_fir_pbajas(signal, fs, f_corte, L)
elif tipo_filtro == "highpass":
    signal_filtrada, h = filtro_fir_paltas(signal, fs, f_corte, L)
elif tipo_filtro == "bandpass":
    signal_filtrada, h = filtro_fir_pbanda(signal, fs, f_low_, f_high_, L)
elif tipo_filtro == "bandstop":
    signal_filtrada, h = filtro_fir_rbanda(signal, fs, f_low_, f_high_, L)
else:
    raise ValueError("Tipo de filtro no reconocido.")


plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(signal, label="Señal Original")
plt.legend()
plt.title("Señal Original")

plt.subplot(2, 1, 2)
plt.plot(signal_filtrada, label=f"Señal Filtrada FIR ({tipo_filtro})", color="red")
plt.legend()
plt.title("Señal Filtrada")

plt.tight_layout()
plt.show()