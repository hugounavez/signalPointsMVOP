# -*- coding: utf-8 -*-
__author__ = 'hugo'

import doubleProbe

filename = "/media/hugo/2959-94B8/Pierna/"

# From double probe were reading the data:
archivos = doubleProbe.leerRutasArhivosPierna(filename)

# Lectura del reporte:
reporte = doubleProbe.lecturaReporte(archivos['hugoEnrique']['reporte'][0])

# Lectura de las señales almacenadas:
mediciones = doubleProbe.lectura(archivos['hugoEnrique']['pierna'][0])



process  = doubleProbe.processDoubleProbe(mediciones['Tiempo Ecg'], mediciones['Ecg'],
                                          mediciones['Tiempo Pulso 2'], mediciones['Pulso 2'],
                                          mediciones['Tiempo Pulso 1'], mediciones['Pulso 1'],
                                          float(reporte['distancia']))

# Using the maximun point idenfitication
process.maxAlgorithm()
process.plotResults()
print(process.vop)

process.tanAlgorithm()
print(process.vop)
process.plotResults()

process.segDerivAlgorithm()
print(process.vop)
process.plotResults()
