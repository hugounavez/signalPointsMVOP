# -*- coding: utf-8 -*-
__author__ = 'hugo'

""" Importing modules """
# Importing numpy module
import numpy as np
# Importing module for signal processing.
from scipy import signal
# Module of a sliding window filter
import window_filtering


class EcgProcessing():
    """EcgProcessing is a class that contains a Ecg signal and some functions to reduce its noise, reduce its
    baseline and also to identify reference points.

    :param  time    Time in seconds in which each sample was sampled.
    :param  ecg     Ecg samples (ecg signal).

    """
    def __init__(self, time, ecg):
        # Ecg signal
        self.ecg = ecg
        # Time values:
        self.time = time

        self.pos_ecg_max = []
        
    def firFilter(self, cutoff=50, numtaps=31, pass_zero=True, fs=1800):
        """"This module process the signal with a low pass fir filter (hamming window).

        :param  cutoff      Cut off frequency in Hz.
        :param  numtaps     Number of coeficients of the fir filter
        :param  pass_zero   Should be always True for being a low pass filter
        :param  fs          Sampling frecuency in Hz.

        """

        # Calculating nyquist frequency, also know as folding frequency:
        nyq = int(fs / 2 )

        # Scaling the cutoff frequency to the nyquist frequency:
        if type(cutoff) == type([]):
            cutoff = [(float(c) / nyq) for c in cutoff]
        else:
            cutoff = cutoff / float(nyq)

        # Fir coeficient generation:
        ventana = signal.firwin(numtaps=numtaps, cutoff=cutoff, pass_zero=pass_zero, nyq=1)

        # Sinal filtering:
        self.ecg = window_filtering.Filter(self.ecg, numtaps, ventana)
        return self


        
    def removeBaseline(self, polyGrade=15):
        """This function reduce baseline in the ECG signal. It generates a polynomium that describes the
         general behavior of the Ecg signal and then, generates a signal that is substracted to the original one.

         :param polyGrade   polynomium grade to generate from the linear regression"""

        self.ecg = self.ecg - np.polyval(np.polyfit(self.time, self.ecg, polyGrade), self.time)
        return self

    def searchPoints(self, umb=0.5, numtaps=31):
        """This function search over the ECG signal the local maxima points.

        :param  umb         Threshold
        :param  numtaps     Number of coeficients for the internal fir filter processing"""


        def rangos(lista):
            """Esta función define los intervalos de búsqueda de los valores máximos locales. Sólo
            está pensada para la señal ecg. La idea es que el punto inicial del rango corresponda 
            al punto con la derivada máxima del periodo, que respecta al inicio del complejo QRS.
            El numero 270 es que se está considerando un máximo de 150 ms despues de ese punto 
            para buscar al punto máximo local. Los 150 ms se consideraron como la duración máxima
            de un complejo QRS"""
            l = [l + 270 for l in lista]
            l[-1] = -1
            return list(zip(lista, l))

        dervEcg = np.diff(self.ecg)
        dervEcg[0: numtaps] = 0
        dervEcg[-numtaps:] = 0
        
        # Se obtienen los puntos máximos de la segunda derivada. 
        # Estos puntos deben corresponder con el inicio del complejo QRS
        points = self.maximos_ecg(dervEcg, umb)
        
        # Retirando puntos identificados que no tengan una diferencia mayor a 432 muestras.
        # Lo que equivale a 0.24 segundos, suponiendo una frecuencia cardíaca de 250 bpm y
        # conociendo que la frecuencia de muestreo es de aproximadamente 1800 hz para la onda
        # ecg
        points = [points[index] for index in range(len(points) - 1) if np.diff(points[index: index + 2]) >= 432]
        

        self.pos_ecg_max = []
        for rango in rangos(points):
            # Se busca el punto máximo en cada intervalo, el intervalo comprende un punto de la subida
            # del complejo QRS hasta 150 ms después.
            maxPoint = (indices(
                    self.ecg[rango[0]:rango[1]], lambda x: x == max(self.ecg[rango[0]:rango[1]])))
            if len(maxPoint) > 1: maxPoint = [maxPoint[int(len(maxPoint) / 2) - 1]]
            
            self.pos_ecg_max.append(maxPoint[0] + rango[0])
        return self.pos_ecg_max
     
    def process(self, umb=0.5):
        """This function remove automatically the baseline of the signal, filters the 
        signal with FIR filter and then apply the searchPoints method in order to 
        get reference points of the signal"""
        self.firFilter()
        self.removeBaseline()
        
        
        return self.searchPoints(umb)
    
    def processMaximus(self, umb=0.5):
        """This function remove automatically the baseline of the signal, filters the 
        signal with FIR filter and then apply the searchPoints method in order to 
        get reference points of the signal"""
        self.firFilter()
        self.removeBaseline()
        
        #return self.maximos_ecg(self.ecg, umb)
        self.pos_ecg_max = self.maximos_ecg(self.ecg, umb)

     
    
    def maximos_ecg(self, original, umb = 0.3):
        sUmb = [1 if value == True else 0 for value in (original >=  (umb * max(original)))]

        # Se deriva a señal umbralizada:
        sDeriv = np.diff(sUmb)

        # Obteniendo los indices de la señal de subida o bajada:
        subs = indices(sDeriv, lambda x: x ==1)
        bajs = indices(sDeriv, lambda x: x ==-1)

        # En caso que haya diferente número de subidas y bajadas
        if len(subs) !=len(bajs):
            if  len(subs) > len(bajs): 
                subs=subs[0:(len(subs)-1)]
            else:
                bajs=bajs[1:(len(bajs))]

        areas = [] 
        # Determinación de áreas:
        for x in range(len(subs)):
            try: # Intente evaluar la resta de los puntos:
                resta = (bajs[x] - subs[x])
            except IndexError: # Error de índice, por diferencia de tamaño en los vectores
                #print "Error de Índice", x
                subs = np.delete(subs, x)
                break
            # Si el valor de resta se obtiene, entonces se verifica:
            if (resta >= 0): # Si es positivo:
                # Almacene el dato en áreas:
                areas.append(resta)
            else: # Si es negativo:
                del bajs[x]
                areas.append(bajs[x] - subs[x])


        anchValida = np.median(areas) * 0.6
        # Se buscan las areas con anchura inválida para eliminarlas:
        eliminarAreas = indices(areas, lambda x: x <= anchValida)

        areas = np.delete(areas, eliminarAreas)
        # Eliminando las subidas y bajadas correspondientes:
        subs=np.delete(subs,eliminarAreas)
        bajs=np.delete(bajs,eliminarAreas)

        # Se buscan las areas con anchura inválida para eliminarlas (por duración minima) :
        eliminarAreas = indices(areas, lambda x: x <= 15)

        areas = np.delete(areas, eliminarAreas)
        # Eliminando las subidas y bajadas correspondientes:
        subs=np.delete(subs,eliminarAreas)
        bajs=np.delete(bajs,eliminarAreas)

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

        return posPuntosMax


class PulseProcessing():
    """This class contains a arterial pulse signal and several methods for its processing. Between them, some functions
    for searching reference points for each period are include.

    :param      time        Time in seconds in which each sample was sampled.
    :param      pulso       Arterial pulse wave signal (samples)"""


    def __init__(self, time, pulso):
        self.time = time
        self.pulso = pulso
        self.posMax = []
        
    def firFilter(self, fs=800, cutoff=30, numtaps=51, pass_zero=True):
        """"This module process the signal with a low pass fir filter (hamming window).

        :param  cutoff      Cut off frequency in Hz.
        :param  numtaps     Number of coeficients of the fir filter
        :param  pass_zero   Should be always True for being a low pass filter
        :param  fs          Sampling frecuency in Hz.

        """
        nyq = int(fs / 2 )

        if type(cutoff) == type([]):
            cutoff = [(float(c) / nyq) for c in cutoff]
        else:
            cutoff = cutoff / float(nyq)

        self.pulso = self.__firFilter(self.pulso, numtaps, cutoff, pass_zero, 1)
    
    def __firFilter(self, signal1, numtaps, cutoff, pass_zero, nyq):
        ventana = signal.firwin(numtaps=numtaps, cutoff=cutoff, pass_zero=pass_zero, nyq=nyq)
        return window_filtering.Filter(signal1, numtaps, ventana)
    
    def derivate(self, signal1, fs=800):
        """Esta función realiza la diferenciación de la señal.
        x(n) = x(n) - x(n - 1). La señal posteriormente es filtrada
        con un filtro FIR."""
        
        cutoff = 10 
        
        nyq = int(fs / 2 )
        
        if type(cutoff) == type([]):
            cutoff = [(float(c) / nyq) for c in cutoff]
        else:
            cutoff = cutoff / float(nyq)
        
        numtaps = 251
        # Procesando la señal de pulso a una frecuencia de 15 Hz
        derivada =  self.__firFilter(
            #signal1=np.diff(signal1), numtaps=numtaps, cutoff=10, pass_zero=True, nyq=1)
            signal1=np.diff(signal1), numtaps=numtaps, cutoff=cutoff, pass_zero=True, nyq=1)
        
        derivada[0:numtaps] = 0
        derivada[- numtaps:] = 0
        
        return derivada

    def maxNum(self, pulso, ecgTimeMax, simplePuntosMax=False):
        if simplePuntosMax:
            rangos = lambda lista: \
                    [(lista[index], lista[index + 1]) \
                     for index in range(0, len(lista) - 1)]
        else:
            rangos = lambda lista: \
                    [(lista[index], np.mean([lista[index], lista[index + 1]])) \
                     for index in range(0, len(lista) - 1)]
        maxPoints = []
        for rango in rangos(ecgTimeMax):
            pmin = indices(self.time, lambda x: x > rango[0])[0]
            pmax = indices(self.time, lambda x: x < rango[1])[-1]

            maxPoint = indices(pulso[pmin:pmax], lambda x: x == max(pulso[pmin:pmax]))
            
            if len(maxPoint) > 1: maxPoint = [maxPoint[int(len(maxPoint) / 2) - 1]]
            
            maxPoints.append(maxPoint[0] + pmin)

        umbral = np.median(pulso[maxPoints])

        locations = list(zip(pulso[maxPoints], maxPoints))
        
        maxPoints = list(point[1] for point in filter(lambda x: (x[0] < umbral * 1.3) and (x[0] >= umbral * 0.3), locations))
        
        #return maxPoints    
        self.posMax = maxPoints
    
    
# Función equivalente a "find" en Matlab:
def indices(a, func):
    """This function is an equivalent to find function in Matlab. 
    a is de array to introduce and func is a function or a lambda function."""
    return [i for (i, val) in enumerate(a) if func(val)]


