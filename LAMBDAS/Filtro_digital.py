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

def filtro_iir_pbajas(signal, fs, fc):
    # F.T Butterworth de orden 2 : H(s) = 1 / (s^2 + √2 s + 1)
    wc = 2 * np.pi * fc / fs  # Frecuencia angular normalizada
    Omega_c = np.tan(wc / 2)  # Escalado de frecuencia 

    # Transformada bilineal--> s = (1 - z^-1)/(1 + z^-1)
    K = Omega_c
    a = K ** 2
    b = np.sqrt(2) * K
    c = 1

    # Coeficientes digitales normalizados
    B0 = a
    B1 = 2 * a
    B2 = a
    A0 = a + b + c
    A1 = 2 * (a - c)
    A2 = a - b + c

    b = np.array([B0, B1, B2]) / A0   # normalización
    a = np.array([1, A1 / A0, A2 / A0])  # a0 se normaliza a 1

    y = np.zeros_like(signal)
    for n in range(len(signal)):
        y[n] = (
            b[0] * signal[n] +
            (b[1] * signal[n - 1] if n - 1 >= 0 else 0) +
            (b[2] * signal[n - 2] if n - 2 >= 0 else 0) -
            (a[1] * y[n - 1] if n - 1 >= 0 else 0) -
            (a[2] * y[n - 2] if n - 2 >= 0 else 0)
        )

    return y, b, a

def filtro_iir_paltas(signal, fs, fc):
    wc = 2 * np.pi * fc / fs
    Omega_c = np.tan(wc / 2)

    K = Omega_c
    a = K ** 2
    b = np.sqrt(2) * K
    c = 1

    # Numerador de pasa altas: s² --> transformada bilineal en discreto: (1 - 2z⁻¹ + z⁻²)
    B0 = 1
    B1 = -2
    B2 = 1
    #denominador
    A0 = a + b + c
    A1 = 2 * (a - c)
    A2 = a - b + c

    #normalizacion
    b = np.array([B0, B1, B2]) / A0
    a = np.array([1, A1 / A0, A2 / A0])  # a0 normalizado a 1

    y = np.zeros_like(signal)
    for n in range(len(signal)):
        y[n] = (
            b[0] * signal[n] +
            (b[1] * signal[n - 1] if n - 1 >= 0 else 0) +
            (b[2] * signal[n - 2] if n - 2 >= 0 else 0) -
            (a[1] * y[n - 1] if n - 1 >= 0 else 0) -
            (a[2] * y[n - 2] if n - 2 >= 0 else 0)
        )

    return y, b, a

def filtro_iir_pbanda(signal, fs, f_low, f_high):
    f0 = np.sqrt(f_low * f_high)     # Frecuencia central geométrica
    bw = f_high - f_low              # Ancho de banda

    # Parámetros normalizados:
    wc = 2 * np.pi * f0 / fs
    bw_norm = 2 * np.pi * bw / fs

    Omega_0 = np.tan(wc / 2)
    BW = np.tan(bw_norm / 2)

    Q = Omega_0 / BW  # Factor de calidad

    # Coeficientes analógicos transformados con bilineal
    K = Omega_0
    a0 = 1 + BW + K**2
    b0 = BW
    b1 = 0
    b2 = -BW
    a1 = 2 * (K**2 - 1)
    a2 = 1 - BW + K**2
    #normalización
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1, a1 / a0, a2 / a0])

    y = np.zeros_like(signal)
    for n in range(len(signal)):
        y[n] = (
            b[0] * signal[n] +
            (b[1] * signal[n - 1] if n - 1 >= 0 else 0) +
            (b[2] * signal[n - 2] if n - 2 >= 0 else 0) -
            (a[1] * y[n - 1] if n - 1 >= 0 else 0) -
            (a[2] * y[n - 2] if n - 2 >= 0 else 0)
        )

    return y, b, a

def filtro_iir_rbanda(signal, fs, f_low, f_high):
    f0 = np.sqrt(f_low * f_high)  
    bw = f_high - f_low           

    # normalizar a radianes
    wc = 2 * np.pi * f0 / fs
    bw_norm = 2 * np.pi * bw / fs

    Omega_0 = np.tan(wc / 2)       # Transformación de frecuencia central
    BW = np.tan(bw_norm / 2)       # Transformación de ancho de banda

    Q = Omega_0 / BW               

    #coeficientes con transformada bilineal 
    K = Omega_0
    a0 = 1 + BW + K**2
    b0 = 1 + K**2
    b1 = 2 * (K**2 - 1)
    b2 = 1 + K**2
    a1 = 2 * (K**2 - 1)
    a2 = 1 - BW + K**2

    b = np.array([b0, b1, b2]) / a0
    a = np.array([1, a1 / a0, a2 / a0])  # a0 se normaliza a 1

    y = np.zeros_like(signal)
    for n in range(len(signal)):
        y[n] = (
            b[0] * signal[n] +
            (b[1] * signal[n - 1] if n - 1 >= 0 else 0) +
            (b[2] * signal[n - 2] if n - 2 >= 0 else 0) -
            (a[1] * y[n - 1] if n - 1 >= 0 else 0) -
            (a[2] * y[n - 2] if n - 2 >= 0 else 0)
        )

    return y, b, a

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
tipo_filtro = "bandstop_iir"  # "lowpass", "highpass", "bandpass", "bandstop"


signal = generar_senal(fs, T, f1, f2, A1, A2)

if tipo_filtro == "lowpass_fir":
    signal_filtrada, h = filtro_fir_pbajas(signal, fs, f_corte, L)
elif tipo_filtro == "highpass_fir":
    signal_filtrada, h = filtro_fir_paltas(signal, fs, f_corte, L)
elif tipo_filtro == "bandpass_fir":
    signal_filtrada, h = filtro_fir_pbanda(signal, fs, f_low_, f_high_, L)
elif tipo_filtro == "bandstop_fir":
    signal_filtrada, h = filtro_fir_rbanda(signal, fs, f_low_, f_high_, L)
elif tipo_filtro == "lowpass_iir":
    signal_filtrada, h, _ = filtro_iir_pbajas(signal, fs, f_corte)
elif tipo_filtro == "highpass_iir":
    signal_filtrada, h , _= filtro_iir_paltas(signal, fs, f_corte)
elif tipo_filtro == "bandpass_iir":
    signal_filtrada, h , _= filtro_iir_pbanda(signal, fs, f_low_, f_high_)
elif tipo_filtro == "bandstop_iir":
    signal_filtrada, h, _ = filtro_iir_rbanda(signal, fs, f_low_, f_high_)
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