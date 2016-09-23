# -*- coding: utf-8 -*-
__author__ = 'hugo'


""" Importar librerias """
# Cargando el módulo numérico numpy:
import numpy as np
# Módulo para funciones del systema:
import sys
# Importing dumps
from json import dumps, load

def vari_M_pares(vector):
    #M_value = 0
    #M_pairs = math.factorial(len(vector)) / ((2) * (math.factorial(len(vector) - 2)))
    var = [] # Variable donde se almacenarán las distintas varianzas.
    for x in range(0, len(vector), 1):
        # Para cada uno de los pares, realizar:
        for y in range(x + 1, len(vector), 1):
            # Resta punto a punto de los vectores:

            # Se verifica que tengan la misma longitud:
            if len(vector[x]) == len(vector[y]):
                d = vector[x] - vector[y]
                var.append(np.var(d))
            # Si no tienen la misma longitud:
            elif len(vector[x]) >= len(vector[y]):
                d = vector[x][0:len(vector[y])] - vector[y]
                var.append(np.var(d))
            elif len(vector[x]) <= len(vector[y]):
                d = vector[x] - vector[y][0:len(vector[x])]
                var.append(np.var(d))
            # Se obtiene el promedio de las restas,
            # el resultado corresponde al promedio de las mediciones de periodos
            # con los dos vectores.
            #d_mean = np.mean(d)

            #var.append(np.sqrt(np.mean((d - d_mean) ** 2)))

    var = np.mean(var)
    return var

def lectura(path):
	mediciones = {}
	with open(path) as textManager:
	    textRead = [[line[0:len(line) - 1]] for line in textManager]

	for x in range(0, len(textRead) -1):
	    if x % 2 == 0: mediciones[textRead[x][0]] = np.array([float(number) for number in textRead[x + 1][0].split(',')])
	return mediciones

def lecturaJson(path):
    with open(path) as data_file:   
        return load(data_file)  
    
def writeJson(jsonCols, pathToJsonFile):
    assert isinstance(jsonCols, dict), "Error: columnAnalyse must be run before writeJson function."
    jsonCols = dumps(jsonCols)
    with open(pathToJsonFile, 'w') as outfile:
        # outfile.write(str(jsonCols).replace("'", "\""))
        outfile.write(jsonCols)


def processStr(word):
    """This function decode an input string only if the script runs 
    on python 2.x"""
    if (sys.version_info.major < 3):
        return word.decode('utf-8')
    else:
        return word
    
def escribir(path, tiempo, pulso):
    with open(path + ".csv", "w") as out_file:
        
        for i in range(len(tiempo)):
            if i==0:
                out_file.write("tiempo, pulso\n,")
            else:
                out_file.write(str(tiempo[i -1]) + "," +  str(pulso[i - 1]) + "\n")
                
def lecturaReporte(path):
    with open(path) as textManager:
        if (sys.version_info.major >= 3):
            # For python 3.5:
            textRead = [row[:-1] for row in textManager]
        else:
            # For python 2.7:
            textRead = [row[:-1].decode('utf-8') for row in textManager]
        

        values = [textRead[index] for index in range(len(textRead)) if index % 2 != 0]

        def buildingDicc(keys, lista):
            if type(keys) != type([]): keys = [keys]
            if type(lista) != type([]): lista = [lista]

            dicc = {}
            for index in range(0,len(keys)):
                dicc[keys[index]] = lista[index]
            return dicc

        keys = ["fechaHora", "primerApellido", "segundoApellido", "primerNombre", "segundoNombre", "CI", "edad", "peso"
           ,"talla", "presionSistolica", "presionDiastolica", "priRegPulso", "segRegPulso", "distancia", "vop", "bpm", "diagnostico"]

        values = [textRead[index] for index in range(len(textRead)) if index % 2 != 0]

        return buildingDicc(keys, values)

# Función equivalente a "find" en Matlab:
def indices(a, func):
    return [i for (i, val) in enumerate(a) if func(val)]

# Función para separar las señales de pulso por periodo, la separación está regida por los puntos
# máximos de la señal de ECG
def splitPeriods(t_ecg, tiempoPulso, pulso):
    # Para organizar las posiciones de los puntos máximos ecg en rangos:
    rangos = lambda lista : [(lista[x], lista[x + 1]) for x in range(0, len(lista) -1)]

    periodsPulse = []
    periods = []
    for rango in rangos(t_ecg):
        tempTiempo = indices(tiempoPulso, lambda x: (x > rango[0]) and (x < rango[1]))
        periods.append(tiempoPulso[tempTiempo])
        periodsPulse.append(pulso[tempTiempo])

        #plt.plot(femoralPulso[interval])
        #plt.show()

    return periods, periodsPulse

# Función para remover outliers 
def removeOutliers(points, umbral=20):    
    outlierDetection = np.median(abs(points -  np.median(points))) * umbral
    return list(filter(lambda x: x <= outlierDetection, points))

