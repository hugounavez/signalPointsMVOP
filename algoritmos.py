# -*- coding: utf-8 -*-
__author__ = 'hugo'

# Módulo creado para leer y escribir las señales en archivos.csv
#import FilesCsv
# Módulo de entorno gráfico:
import matplotlib.pylab as plt
# Módulo numérico de Python:
import numpy as np
# Módulo científico de python, importando signal
from scipy import signal
# Módulo creado para el filtrado por ventana deslizante (FIR).
import window_filtering
# Módulo para la identificación de puntos:



def maximos_ecg(original, umb = 0.89):
    # Asignando el promedio de la señal como el valor del umbral:
    umbral = umb * max(original)

    # Asginación y ejecución del umbral:
    sUmb = original >= umbral
    sUmb  = boolToInt(sUmb) # Variable en int
    #plt.plot(sUmb * max(original - dc) + dc)

    # Se deriva a señal umbralizada:
    sDeriv = np.diff(sUmb)
    #plt.plot(sDeriv * max(original - dc) + dc)

    # Obteniendo los indices de la señal de subida o bajada:
    subs = indices(sDeriv, lambda x: x ==1)
    bajs = indices(sDeriv, lambda x: x ==-1)

    # Transformando las variables de listas a arreglos:
    subs = np.array(subs)
    bajs = np.array(bajs)

    #print "subidas", subs
    #print "bajadas",bajs

    ##############################################################################
    # En caso que haya diferente número de subidas y bajadas
    if len(subs) !=len(bajs):
        if  len(subs)> len(bajs):
            # Tomar todas las subidas menos la última:
            subs=subs[0:(len(subs)-1)]
        else:
            # Tomar todas las bajadas menos la primera:
            bajs=bajs[1:(len(bajs))]

    areas = np.array([])


    # Determinación de áreas:
    for x in range(len(subs)):
        try: # Intente evaluar la resta de los puntos:
            resta = (bajs[x] - subs[x])
        except IndexError: # Error de índice, por diferencia de tamaño en los vectores
            subs = np.delete(subs, x)
            break

        # Si el valor de resta se obtiene, entonces se verifica:
        if (resta >= 0): # Si es positivo:
            # Almacene el dato en áreas:
            areas = np.concatenate((areas, np.array([resta])), axis=0)
        else: # Si es negativo:
            # Elimine el dato que no corresponde
            bajs = np.delete(bajs, x)
            resta = (bajs[x] - subs[x])
            areas = np.concatenate((areas, np.array([resta])), axis=0)

        ###############################################################################

    # Validación de las areas:
    anchValida = np.median(areas) * 0.5
    # Se buscan las areas con anchura inválida para eliminarlas:
    eliminarAreas = indices(areas, lambda x: x <= anchValida)
    areas = np.delete(areas, eliminarAreas)
    #stem(areas)

    # Eliminando las subidas y bajadas correspondientes:
    subs=np.delete(subs,eliminarAreas)
    bajs=np.delete(bajs,eliminarAreas)
    #stem(subs, sDeriv[subs])
    #stem(bajs, sDeriv[bajs]* - 1, 'r')


    # Declarando variables de posicion y de los puntos:
    posMax = np.zeros(len(areas), dtype = int)  # Variable de posiciones de puntos
    puntosMax = np.zeros(len(areas), dtype = float) # Amplitud de los puntos

    for x in range(len(areas)):
        puntosMax[x]= max(original[subs[x]:bajs[x]])
        #Posición del punto máximo local, si consigue dos, toma el primero.
        posicion = indices(original[subs[x]:bajs[x]], lambda y: y == puntosMax[x])
        # Si hay varios puntos que tienen el mismo valor:
        if len(posicion) > 1:
            posMax[x] = posicion[int(len(posicion) / 2) - 1]
        else:
            posMax[x] = posicion[0]

    # Se le suma la posición de subida correspondiente:
    posPuntosMax = posMax + subs


    rangTol = 0.3
    valMin = np.median(puntosMax) * (1 - rangTol)
    valMax = np.median(puntosMax) * (rangTol + 1)
    # Ubicando los puntos que no están en el rango de tolerancia:
    eliPuntos = np.where( (puntosMax <= valMin) | (puntosMax >= valMax) )
    # Eliminando puntos y sus posiciones fuera del rango:
    puntosMax = np.delete(puntosMax, eliPuntos)
    posPuntosMax = np.delete(posPuntosMax, eliPuntos)

    return posPuntosMax


def maximos_num(tiempo_original, original, tiempos_puntos_ecg):  
    puntos = tiempos_puntos_ecg
    #if len(tiempos_puntos_ecg)% 2:
    #   tiempos_puntos_ecg = tiempos_puntos_ecg[0:len(tiempos_puntos_ecg) - 1]
    x = 0

    for punto in puntos:
        tiempos = indices(tiempo_original, lambda y: y < punto)
        tiempos_puntos_ecg[x] = tiempos[len(tiempos)-1]
        #tiempos_puntos_ecg[x] = np.where(tiempo_original < punto)[0]
        x += 1


    ##############################################################
    # Declarando variables de posicion y de los puntos:
    posMax = np.zeros(len(tiempos_puntos_ecg) - 1, dtype = int)  # Variable de posiciones de puntos
    puntosMax = np.zeros(len(tiempos_puntos_ecg) -1, dtype = float) # Amplitud de los puntos


    for x in range(len(tiempos_puntos_ecg)):
        if not x == len(tiempos_puntos_ecg) - 1:
            puntosMax[x]= max(original[tiempos_puntos_ecg[x]: tiempos_puntos_ecg[x + 1]])
            #Posición del punto máximo local, si consigue dos, toma el primero.
            #posicion = indices(original[tiempos_puntos_ecg[x]: tiempos_puntos_ecg[x + 1]], lambda y: y == puntosMax[x])

            posicion = np.where(original[tiempos_puntos_ecg[x]: tiempos_puntos_ecg[x + 1]] == puntosMax[x])
            posicion = np.array(posicion[0])
        else:
            break
    #        puntosMax[x]= max(original[tiempos_puntos_ecg[x]: len(original) - 1])
    #       posicion = indices(original[tiempos_puntos_ecg[x]: len(original) - 1], lambda y: y == puntosMax[x])

        # Si hay varios puntos que tienen el mismo valor:
        if len(list(posicion)) > 1:
            posMax[x] = posicion[int(len(posicion) / 2) - 1]
        else:

            posMax[x] = posicion[0]

    ## Se le suma la posición de subida correspondiente:
    posPuntosMax = posMax + tiempos_puntos_ecg[0: len(tiempos_puntos_ecg) -1]
    #
    rangTol = 0.7
    valMin = np.median(puntosMax) * (1 - rangTol)
    valMax = np.median(puntosMax) * (rangTol + 1)
    # Ubicando los puntos que no están en el rango de tolerancia:
    eliPuntos = np.where( (puntosMax <= valMin) | (puntosMax >= valMax) )
    # Eliminando puntos y sus posiciones fuera del rango:
    puntosMax = np.delete(puntosMax, eliPuntos)
    posPuntosMax = np.delete(posPuntosMax, eliPuntos)

    intPosPuntosMax = []

    for x in posPuntosMax:
        intPosPuntosMax.append(int(x))

    return intPosPuntosMax


def tangente_maxima(tiempos_original, original, tiempos_ecg):
    # Procesando la señal de pulso a una frecuencia de 20 Hz
    coef_num = 15
    f_cut = 0.0111
    delay = (coef_num - 1)/2
    deriv_p = signal.firwin(coef_num, f_cut, window='hamming',nyq=1800)
    f_orig = window_filtering.Filter(original, coef_num, deriv_p);

    #~~~~~~~~~~~~~~~~~~~~~Primera derivada~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Se deriva la señal para obtener la primera derivada:
    pri_deriv = np.diff(original)
    pri_deriv = pri_deriv
    coef_num = 21
    f_cut = 0.1
    deriv_p = signal.firwin(coef_num, f_cut, window='hamming',nyq=800)
    f_pri_deriv = window_filtering.Filter(pri_deriv, coef_num, deriv_p);

    ## Identificación de los puntos de la onda de pulso2:
    posPuntMaxP1 = maximos_num(tiempos_original, f_pri_deriv, tiempos_ecg)


    puntMaxP1 = f_pri_deriv[posPuntMaxP1]
    rangTol = 0.3
    valMin = np.median(puntMaxP1) * (1 - rangTol)
    valMax = np.median(puntMaxP1) * (rangTol + 1)
    # Ubicando los puntos que no están en el rango de tolerancia:
    eliPuntos = np.where( (puntMaxP1 <= valMin) | (puntMaxP1 >= valMax) )
    # Eliminando puntos y sus posiciones fuera del rango:
    puntMaxP1 = np.delete(puntMaxP1, eliPuntos)
    posPuntMaxP1 = np.delete(posPuntMaxP1, eliPuntos)
    
    intPosPuntosMax = []

    for x in posPuntMaxP1:
        intPosPuntosMax.append(int(x))

    return intPosPuntosMax

def seg_derivada_maxima(tiempos_original, original, tiempos_ecg):
    # Procesando la señal de pulso a una frecuencia de 20 Hz
    coef_num = 15
    f_cut = 0.0111
    delay = (coef_num - 1)/2
    deriv_p = signal.firwin(coef_num, f_cut, window='hamming',nyq=1800)
    f_orig = window_filtering.Filter(original, coef_num, deriv_p);

    #~~~~~~~~~~~~~~~~~~~~~Primera derivada~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Se deriva la señal para obtener la primera derivada:
    pri_deriv = np.diff(original)
    coef_num = 21
    f_cut = 0.1
    deriv_p = signal.firwin(coef_num, f_cut, window='hamming',nyq=800)
    f_pri_deriv = window_filtering.Filter(pri_deriv, coef_num, deriv_p);

    #~~~~~~~~~~~~~~~~~~~~~Segunda derivada~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    seg_deriv = np.diff(f_pri_deriv)
    f_seg_deriv = window_filtering.Filter(seg_deriv, coef_num, deriv_p);

    ## Identificación de los puntos de la onda de pulso2:
    posPuntMaxP1 = maximos_num(tiempos_original, f_seg_deriv, tiempos_ecg)

    #return posPuntMaxP1, puntMaxP1, f_orig, pri_deriv, f_pri_deriv

    puntMaxP1 = f_seg_deriv[posPuntMaxP1]

    rangTol = 0.3
    valMin = np.median(puntMaxP1) * (1 - rangTol)
    valMax = np.median(puntMaxP1) * (rangTol + 1)
    # Ubicando los puntos que no están en el rango de tolerancia:
    eliPuntos = np.where( (puntMaxP1 <= valMin) | (puntMaxP1 >= valMax) )
    # Eliminando puntos y sus posiciones fuera del rango:
    puntMaxP1 = np.delete(puntMaxP1, eliPuntos)
    posPuntMaxP1 = np.delete(posPuntMaxP1, eliPuntos)

    intPosPuntosMax = []

    for x in posPuntMaxP1:
        intPosPuntosMax.append(int(x))

    return intPosPuntosMax

def poly_aproximation(interval_temp, interval_amp):
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Intérvalo de búsqueda~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Intérvalo amplitud:
    #interval_amp = f_orig_pulso1[616:853]
    # Intérvalo tiempo:
    #interval_temp = signals.vecTimePulso1[616:853]
    # Dividir el tramo de la señal de pulso en otros diez:
    len_tramo = len(interval_amp) / 10

    interval_temp = interval_temp[0:len_tramo * 10]
    interval_amp = interval_amp[0:len_tramo * 10]
    # Definir la mitad de los tramos:
    mitad_tramo = len_tramo/2
    # Vector de tramos o divisines del intérvalo:
    vector = np.arange(0, len(interval_amp) + len_tramo, len_tramo)

    # Declarando variables de lista:
    tramos_amp = []  # Variable que almacena los intervalos originales (amplitud)
    tramos_temp = [] # Variable que almacena los intervalos originales (tiempo)
    lines_ms = [] # Variable que almacena las líneas de mínimos cuadrados de cada tramo
    puntos_lms = [] # Variable que almacena los puntos medios de las líneas LMS (amplitud)
    puntos_lms_temp = [] # Variable que almacena los puntos medios de las líneas LMS (tiempo)

    for x in range(0, 10):
        if x < 10:
            intervalo  = vector[x:x + 2]
            # Guardando los intérvalos originales:
            tramos_amp.append(interval_amp[intervalo[0]: intervalo[1]])
            tramos_temp.append(interval_temp[intervalo[0]: intervalo[1]])
            # Graficando los intérvalos:
            #plt.plot(tramos_temp[x], tramos_amp[x], linewidth=3)
            # Buscando las líneas por mínimos cuadrados de los intervalos:
            poli_fit = np.polyfit(tramos_temp[x], tramos_amp[x], 1) # LMS grado 1
            # Anexando las líneas de mínimos cuadrados:
            lines_ms.append(np.polyval(poli_fit, tramos_temp[x]))
            # Graficando las líneas de mínimos cuadrados:
            #plt.plot(tramos_temp[x], lines_ms[x], 'k')
            #Puntos medios de lineas LMS:
            puntos_lms.append(lines_ms[x][mitad_tramo])
            puntos_lms_temp.append(tramos_temp[x][mitad_tramo])
            # Graficando puntos medios de lineas LMS:
            #plt.plot( puntos_lms_temp[x], puntos_lms[x], 'o', linewidth=5, markersize=8, color = 'r')
            # Activando grilla:
            #plt.grid(True)

    poli_fit = np.polyfit(puntos_lms_temp, puntos_lms, 3) # LMS grado 1
    #curva_lms = np.polyval(poli_fit, interval_amp) / 50000000
    curva_lms = np.polyval(poli_fit, interval_temp) / 1e1
    pos_min = indices(curva_lms, lambda y: y == min(curva_lms))

    return pos_min



 # Función equivalente a "find" en Matlab:
def indices(a, func):
    return [i for (i, val) in enumerate(a) if func(val)]


#Función para transformar un array boolean a entero:
def boolToInt(booleanos):
    enteros = np.zeros(len(booleanos),dtype=int)
    for x in range (len(booleanos)):
        enteros[x]=int(booleanos[x])
    return enteros

# Determinando los tiempos de los puntos de medición:
def transit_time(tiemposPuntosEcg, tiemposPuntP1, tiemposPuntP2):
    contPulso = 0
    tt = list()
    for x in range(len(tiemposPuntosEcg) -1):
            # Antes de realizar la resta de los tiempos,
            # Se verifica que existan los puntos de medición necesarios
            # en las señales de pulsos entre el intervalor RR
            puntDispP1 = np.where((tiemposPuntP1 >= tiemposPuntosEcg[x]) & (tiemposPuntP1 < tiemposPuntosEcg[x + 1]))

            try:
                puntDispP1 = int(puntDispP1[0])
            except:
                puntDispP1 = []


            # Revisando disponibilidad de puntos de medición en el intervalo RR
            puntDispP2 = np.where((tiemposPuntP2 >= tiemposPuntosEcg[x]) & (tiemposPuntP2 < tiemposPuntosEcg[x + 1]))

            try:
                puntDispP2 = int(puntDispP2[0])
            except:
                puntDispP2 = []

            # intpuntDispP2 = []
            #
            # for x in puntDispP2:
            #     intpuntDispP2.append(int(x))
            # Si se de
            if ((puntDispP1 ==[])  | (puntDispP2 == [])):
                check = False
            else:
                check = True
                #check = puntDispP1 && puntDispP2

            # Si el check es falso:
            if not check:
                #print x
                pass # No se hace la resta
            else:
                #tt.append(abs(tiemposPuntP1[contPulso] - tiemposPuntP2[contPulso]))
                tt.append((tiemposPuntP1[puntDispP1]- tiemposPuntP2[puntDispP2]))
                #contPulso += 1
    tt = np.array(tt)
    return tt

def graficas(tiempo_ecg, ecg, tiempo_pulso1, pulso1, tiempo_pulso2, pulso2, 
             pos_ecg, pos_pulso1, pos_pulso2):
    # ~~~~~~~~~~~~~Puntos máximos de las señales de pulso~~~~~~~~
    # Two subplots, the axes array is 1-d
    f1, grafica1 = plt.subplots(3, sharex=True)
    # Gráfica de la señal ECG:
    grafica1[0].plot(tiempo_ecg, ecg)
    grafica1[0].hold(True)
    # Puntos máximos de la señal ECG:
    markerline, stemlines, baseline = grafica1[0].stem(tiempo_ecg[pos_ecg], ecg[pos_ecg],'r', linewidth=4.0)
    plt.setp(stemlines, linestyle= '--', color = 'r')
    plt.setp(markerline, markersize=8, color = 'r')
    grafica1[0].axis([min(tiempo_ecg), max(tiempo_ecg), 200, 1200])
    grafica1[0].set_title('Puntos máximos de señal ECG'.decode('utf-8'))
    grafica1[0].grid(True)
    
    # Señal de pulso 1:
    grafica1[1].plot(tiempo_pulso1, pulso1)
    grafica1[1].axis([min(tiempo_ecg), max(tiempo_ecg), 50, 800])
    grafica1[1].hold(True)
    markerline, stemlines, baseline = grafica1[1].stem(tiempo_pulso1[pos_pulso1], pulso1[pos_pulso1])
    plt.setp(stemlines, linestyle= '--', color = 'g')
    plt.setp(markerline, markersize=8, color = 'g')
    grafica1[1].set_title('Puntos máximos de señal de pulso 1'.decode('utf-8'))
    grafica1[1].grid(True)
    
    # Puntos del ECG, para demarcar áreas:
    markerline, stemlines, baseline = grafica1[1].stem(tiempo_ecg[pos_ecg], ecg[pos_ecg] * 3,'r', linewidth=4.0)
    plt.setp(stemlines, linestyle= '--', color = 'r')
    plt.setp(markerline, markersize=8, color = 'r')
    # Señal de pulso 2:
    # Identificación de los puntos de la onda de pulso2:
    
    grafica1[2].plot(tiempo_pulso2, pulso2)
    grafica1[2].axis([min(tiempo_ecg), max(tiempo_ecg), 50, 800])
    grafica1[2].hold(True)
    markerline, stemlines, baseline = grafica1[2].stem(tiempo_pulso2[pos_pulso2], pulso2[pos_pulso2])
    plt.setp(stemlines, linestyle= '--', color = 'g')
    plt.setp(markerline, markersize=8, color = 'g')
    grafica1[2].set_title('Puntos máximos de señal de pulso 2'.decode('utf-8'))
    grafica1[2].grid(True)
    # Puntos del ECG, para demarcar áreas:
    markerline, stemlines, baseline = grafica1[2].stem(tiempo_ecg[pos_ecg], ecg[pos_ecg] * 3,'r', linewidth=4.0)
    plt.setp(stemlines, linestyle= '--', color = 'r')
    plt.setp(markerline, markersize=8, color = 'r')
    plt.xlabel('Segundos')



######################## Procedimientos de VOP########################################################

def vop_maximos(tiempo_ecg, ecg, tiempo_pulso1, pulso1, tiempo_pulso2, pulso2, distancia):
    #~~~~~~~~~~~~~~~~~~~~~~~~~Senales ECG ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    coef_num = 51
    f_cut = 0.034 #  Frecuencia de corte 60 Hz
    coef = signal.firwin(coef_num, f_cut, window='hamming',nyq=1800)
    f_ecg = window_filtering.Filter(ecg, coef_num, coef);

    # Identificación de puntos de la Onda ECG:
    pos_ecg = maximos_ecg(f_ecg)

    #~~~~~~~~~~~~~~~~~~~~Senal de pulso 1 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    coef_num = 15
    f_cut = 0.01875
    coef = signal.firwin(coef_num, f_cut, window='hamming',nyq=800)
    f_pulso1 = window_filtering.Filter(pulso1, coef_num, coef);
    # Identificación de los puntos de la onda de pulso1
    pos_pulso1 = maximos_num(tiempo_pulso1, f_pulso1, tiempo_ecg[pos_ecg])

    #~~~~~~~~~~~~~~~~~~~~Senal de pulso 2 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    f_pulso2 = window_filtering.Filter(pulso2, coef_num, coef);
    # Identificación de los puntos de la onda de pulso1
    pos_pulso2 = maximos_num(tiempo_pulso2, f_pulso2, tiempo_ecg[pos_ecg])

    # Cálculo del tiempo de tránsito:
    tt = transit_time(tiempo_ecg[pos_ecg], tiempo_pulso1[pos_pulso1], tiempo_pulso2[pos_pulso2])

    vop = []
    for k in tt:
        vop.append(distancia / k)

    vop = np.array(vop)
    return f_ecg, f_pulso1, f_pulso2, pos_ecg, pos_pulso1, pos_pulso2, vop


def vop_tangente(tiempo_ecg, ecg, tiempo_pulso1, pulso1, tiempo_pulso2, pulso2, distancia):
    #~~~~~~~~~~~~~~~~~~~~~~~~~Senales ECG ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    coef_num = 51
    f_cut = 0.034 #  Frecuencia de corte 60 Hz
    coef = signal.firwin(coef_num, f_cut, window='hamming',nyq=1800)
    f_ecg = window_filtering.Filter(ecg, coef_num, coef);

    # Identificación de puntos de la Onda ECG:
    pos_ecg = maximos_ecg(f_ecg)

    #~~~~~~~~~~~~~~~~~~~~Senal de pulso 1 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    coef_num = 15
    f_cut = 0.01875
    coef = signal.firwin(coef_num, f_cut, window='hamming',nyq=800)
    f_pulso1 = window_filtering.Filter(pulso1, coef_num, coef);
    # Identificación de los puntos de la onda de pulso1
    pos_pulso1 = tangente_maxima(tiempo_pulso1, f_pulso1, tiempo_ecg[pos_ecg])

    #~~~~~~~~~~~~~~~~~~~~Senal de pulso 2 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    f_pulso2 = window_filtering.Filter(pulso2, coef_num, coef);
    # Identificación de los puntos de la onda de pulso1
    pos_pulso2 = tangente_maxima(tiempo_pulso2, f_pulso2, tiempo_ecg[pos_ecg])

    # Cálculo del tiempo de tránsito:
    tt = transit_time(tiempo_ecg[pos_ecg], tiempo_pulso1[pos_pulso1], tiempo_pulso2[pos_pulso2])

    vop = []
    for k in tt:
        vop.append(distancia / k)
    vop = np.array(vop)
    return f_ecg, f_pulso1, f_pulso2, pos_ecg, pos_pulso1, pos_pulso2, vop

def vop_seg_derivada(tiempo_ecg, ecg, tiempo_pulso1, pulso1, tiempo_pulso2, pulso2, distancia):
    #~~~~~~~~~~~~~~~~~~~~~~~~~Senales ECG ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    coef_num = 51
    f_cut = 0.034 #  Frecuencia de corte 60 Hz
    coef = signal.firwin(coef_num, f_cut, window='hamming',nyq=1800)
    f_ecg = window_filtering.Filter(ecg, coef_num, coef);

    # Identificación de puntos de la Onda ECG:
    pos_ecg = maximos_ecg(f_ecg)

    #~~~~~~~~~~~~~~~~~~~~Senal de pulso 1 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    coef_num = 15
    f_cut = 0.01875
    coef = signal.firwin(coef_num, f_cut, window='hamming',nyq=900)
    f_pulso1 = window_filtering.Filter(pulso1, coef_num, coef);
    # Identificación de los puntos de la onda de pulso1
    pos_pulso1 = seg_derivada_maxima(tiempo_pulso1, f_pulso1, tiempo_ecg[pos_ecg])

    #~~~~~~~~~~~~~~~~~~~~Senal de pulso 2 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    f_pulso2 = window_filtering.Filter(pulso2, coef_num, coef);
    # Identificación de los puntos de la onda de pulso1
    pos_pulso2 = seg_derivada_maxima(tiempo_pulso2, f_pulso2, tiempo_ecg[pos_ecg])

    # Cálculo del tiempo de tránsito:
    tt = transit_time(tiempo_ecg[pos_ecg], tiempo_pulso1[pos_pulso1], tiempo_pulso2[pos_pulso2])


    vop = []
    for k in tt:
        vop.append(distancia / k)
    vop = np.array(vop)
    return f_ecg, f_pulso1, f_pulso2, pos_ecg, pos_pulso1, pos_pulso2, vop
