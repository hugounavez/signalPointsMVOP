# -*- coding: utf-8 -*-
__author__ = 'hugo'

# Importing modules to process double probe measurements:
import doubleProbe

# Imporing modules to process single proble measurements
import singleProbe


# filename = "Database/DoubleProbe"
#
# # From double probe were reading the data:
# archivos = doubleProbe.leerRutasArhivosPierna(filename)
#
# # Lectura del reporte:
# reporte = doubleProbe.lecturaReporte(archivos['hugoEnrique']['reporte'][0])
#
# # Lectura de las señales almacenadas:
# mediciones = doubleProbe.lectura(archivos['hugoEnrique']['pierna'][0])
#


#process  = doubleProbe.processDoubleProbe(mediciones['Tiempo Ecg'], mediciones['Ecg'],
#                                          mediciones['Tiempo Pulso 2'], mediciones['Pulso 2'],
#                                          mediciones['Tiempo Pulso 1'], mediciones['Pulso 1'],
#                                          float(reporte['distancia']))


# Using the maximun point idenfitication
#process.maxAlgorithm()
#process.plotResults()
#print(process.vop)

#process.tanAlgorithm()
#rint(process.vop)
#process.plotResults()

#process.segDerivAlgorithm()
#print(process.vop)
#process.plotResults()










import numpy as np
## Geting folders at path specified:
#path = "/media/" + getpass.getuser() + "/2959-94B8/valores"
path = "Database/SingleProbe"

# Read files and make a dictionary with the following structure:
"""
{pacientName:
            {'reporte': ['report.txt'],
             'carotida: ['file.csv','file2.csv'],
             'femoral': ['file.csv', 'file2.csv']
            }
}
"""
# Calculate singleProbe
archivos = singleProbe.leerRutasArhivos(path)

# Calculate ECG-Arterial Pulse Wave carotida delay:
resultsCarotida = singleProbe.singleProbeFunc(archivos['hugo'], 'carotida', 0, umbEcg=0.5)
# Calculate ECG-Arterial Pulse Wave femoral delay:
resultsFemoral = singleProbe.singleProbeFunc(archivos['hugo'], 'femoral', index=0, umbEcg=0.5)
# Report:
reporte = singleProbe.lecturaReporte(archivos['hugo']['reporte'][0])

# VOP calculation
vopMedicion = float(reporte['distancia']) / (np.median(resultsFemoral) - np.median(resultsCarotida))

print(vopMedicion)