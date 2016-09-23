# -*- coding: utf-8 -*-
__author__ = 'hugo'

import signals

import doubleProbe



filename = "/media/hugo/2959-94B8/Pierna/"
archivos = doubleProbe.leerRutasArhivosPierna(filename)

print(archivos)

# Lectura del reporte:
reporte = doubleProbe.lecturaReporte(archivos['hugoEnrique']['reporte'][0])

# Iniciando variables:
maxAlg = []
tanAlg = []
segAlg = []

# Lectura de las señales almacenadas:
mediciones = doubleProbe.lectura(archivos['hugoEnrique']['pierna'][0])

process  = doubleProbe.processDoubleProbe(mediciones['Tiempo Ecg'], mediciones['Ecg'], mediciones['Tiempo Pulso 2'],
                              mediciones['Pulso 2'], mediciones['Tiempo Pulso 1'], mediciones['Pulso 1'],
                                          float(reporte['distancia']))
process.maxAlgorithm()
process.plotResults()