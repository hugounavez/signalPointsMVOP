# -*- coding: utf-8 -*-
__author__ = 'hugo'

# Módulo para el ploteo de los datos:
import matplotlib.pylab as plt
# Importando módulo para leer rutas de archivos
import glob
# Importando el módulo de las clases Pulso y Ecg
from signals import *
# Importando herramientas de procesamiento
from processingTools import *
# Módulo para funciones del systema:
import sys    
# Modificando el estilo de los plots:
plt.style.use('ggplot')

def runAllDoubleProbe(archivos, names):
    vopPacientes = {}
    for name in names:
        # Lectura del reporte:
        reporte = lecturaReporte(archivos[name]['reporte'][0])
        # Iniciando variables:
        maxAlg = []
        tanAlg = []
        segAlg = []

        for index in range(len(archivos[name]['pierna'])):
            # Lectura de las señales almacenadas:
            mediciones = lectura(archivos[name]['pierna'][index])
            # Tangente derivada:
            process  = processDoubleProbe(mediciones['Tiempo Ecg'], mediciones['Ecg'], mediciones['Tiempo Pulso 2'], 
                              mediciones['Pulso 2'], mediciones['Tiempo Pulso 1'], mediciones['Pulso 1'], 
                                          float(reporte['distancia']))
            process.maxAlgorithm()
            process.plotResults()
            #plt.plot(process.vop, 'o', color='m')
            #plt.axis([0, 20, 0, 30])
            print ("Puntos maximos", np.median(process.vop))
            maxAlg.append(process.vop)

            # Tangente derivada:
            process  = processDoubleProbe(mediciones['Tiempo Ecg'], mediciones['Ecg'], mediciones['Tiempo Pulso 2'], 
                              mediciones['Pulso 2'], mediciones['Tiempo Pulso 1'], mediciones['Pulso 1'], 
                                          float(reporte['distancia']))
            process.tanAlgorithm()
            process.plotResults()
            #plt.plot(process.vop, 'o', color='c')
            #plt.axis([0, 20, 0, 30])
            print ("Tangente maxima VOP", np.median(process.vop))
            tanAlg.append(process.vop)

            # Segunda derivada:
            process  = processDoubleProbe(mediciones['Tiempo Ecg'], mediciones['Ecg'], mediciones['Tiempo Pulso 2'], 
                              mediciones['Pulso 2'], mediciones['Tiempo Pulso 1'], mediciones['Pulso 1'], 
                                          float(reporte['distancia']))
            process.segDerivAlgorithm()
            #process.plotResults()
            #plt.plot(process.vop, 'o', color='r')
            #plt.axis([0, 20, 0, 30])
            print ("Segunda derivada VOP", np.median(process.vop))
            segAlg.append(process.vop)

        vopPacientes[name] = {"maximos": maxAlg, "tangente": tanAlg, "segundaDerivada": segAlg}
    return vopPacientes


class processDoubleProbe():
    def __init__(self, tiempoEcg, ecg, tiempoPulso1, pulso1, tiempoPulso2, pulso2, distancia):
        # Objeto ECG instanciado:
        self.ecg = EcgProcessing(tiempoEcg, ecg)
        # Objecto Pulso1:
        self.pulso1 = PulseProcessing(tiempoPulso1, pulso1)
        # Objecto Pulso2:
        self.pulso2 = PulseProcessing(tiempoPulso2, pulso2)
        # VOP:
        self.vop = 0
        self.distancia = distancia
        
        self.preProcessing()
        
    def preProcessing(self):
        """Filtrado con filtro FIR"""
        self.pulso1.firFilter()
        self.pulso2.firFilter()
    
    def plotResults(self):
        plotDoubleProbe(self.pulso1.time, self.pulso1.pulso, self.pulso1.posMax,
               self.pulso2.time, self.pulso2.pulso, self.pulso2.posMax,
               self.ecg.time, self.ecg.ecg + 400, self.ecg.pos_ecg_max)
    
    def maxAlgorithm(self):
        """Algoritmo de puntos máximos"""
        self.ecg.processMaximus()
        
        self.pulso1.maxNum(self.pulso1.pulso, 
                           self.ecg.time[self.ecg.pos_ecg_max], 
                           True)
        
        self.pulso2.maxNum(self.pulso2.pulso, 
                   self.ecg.time[self.ecg.pos_ecg_max], 
                   True)
        
        self.__vopCalculation(self.ecg.time[self.ecg.pos_ecg_max], self.pulso1.time[self.pulso1.posMax],
                self.pulso2.time[self.pulso2.posMax])
        
    def tanAlgorithm(self):
        """Algoritmo de tangente máxima"""
        self.ecg.processMaximus()
        
        priDeriv1 = self.pulso1.derivate(self.pulso1.pulso)
        self.pulso1.maxNum(priDeriv1, 
                           self.ecg.time[self.ecg.pos_ecg_max])
        
        priDeriv2 = self.pulso2.derivate(self.pulso2.pulso)
        self.pulso2.maxNum(priDeriv2, 
                           self.ecg.time[self.ecg.pos_ecg_max])

        self.__vopCalculation(self.ecg.time[self.ecg.pos_ecg_max], self.pulso1.time[self.pulso1.posMax],
                self.pulso2.time[self.pulso2.posMax])
        
    def segDerivAlgorithm(self):
        """Algoritmo de tangente máxima"""
        self.ecg.processMaximus()
        
        segDeriv1 = self.pulso1.derivate(self.pulso1.derivate(self.pulso1.pulso))
        self.pulso1.maxNum(segDeriv1, 
                           self.ecg.time[self.ecg.pos_ecg_max])
        
        segDeriv2 = self.pulso2.derivate(self.pulso2.derivate(self.pulso2.pulso))
        
        self.pulso2.maxNum(segDeriv2, 
                           self.ecg.time[self.ecg.pos_ecg_max])
        
        self.__vopCalculation(self.ecg.time[self.ecg.pos_ecg_max], self.pulso1.time[self.pulso1.posMax],
                        self.pulso2.time[self.pulso2.posMax])
        
    def __vopCalculation(self, t_ecg, t_pulso1, t_pulso2):
        rangos = lambda lista : [(lista[x], lista[x + 1]) for x in range(0, len(lista) -1)] 

        tt = []
        for rango in rangos(t_ecg):
            # Check if there is a point of pulse between:
            p1  = list(filter(lambda t: (t > rango[0]) and (t < rango[1]), t_pulso1))
            p2  = list(filter(lambda t: (t > rango[0]) and (t < rango[1]), t_pulso2))
            if (p1 != []) and (p2 != []):
                tt.append(p2[0]-p1[0])

        
        tt = removeOutliers(self.distancia / np.array(tt), umbral=23)
        tt = list(filter(lambda x: (x > 0) and (x < 50), tt))
        self.vop = tt
        
def leerRutasArhivosPierna(path):
    carpetas = glob.glob(path +  "/*")
    pacientes = {}
    for carpeta in carpetas:
        nombre = glob.glob(carpeta)[0]
        reporte = glob.glob(nombre + "/*.txt") 

        pierna = glob.glob(nombre + "/Pierna/*.csv")
        pacientes[[nombre.split("/")[-1]][0]] = {'pierna': pierna, 'reporte': reporte}
        
    return pacientes

def decodeStr(word):
    if (sys.version_info.major >= 3):
        # For python 3.5:
        return word
    else:
        # For python 2.7:
        return word.decode('utf-8')


def plotDoubleProbe(tiempoSignal1, signal1, pos_signal1, tiempoSignal2, signal2, pos_signal2, tiempoEcg, ecg, pos_ecg_max):
    #~~~~~~~~~~~~~Puntos máximos de las señales de pulso~~~~~~~~
    # Two subplots, the axes array is 1-d
    f1, grafica1 = plt.subplots(3, sharex=True, figsize=(15,5))
    # Gráfica de la señal ECG:
    grafica1[0].plot(tiempoEcg, ecg)
    grafica1[0].hold(True)
    # Puntos máximos de la señal ECG:
    markerline, stemlines, baseline = grafica1[0].stem(tiempoEcg[pos_ecg_max], ecg[pos_ecg_max],'r', linewidth=4.0)
    plt.setp(stemlines, linestyle= '--', color = 'r')
    plt.setp(markerline, markersize=8, color = 'r')
    grafica1[0].axis([min(tiempoEcg), max(tiempoEcg),  min(ecg) * 0.8, max(ecg) * 1.1])
    grafica1[0].set_title(decodeStr('Puntos máximos de señal ECG'))
    grafica1[0].grid(True)

    # Señal de pulso 1:
    grafica1[1].plot(tiempoSignal1, signal1)
    grafica1[1].axis([min(tiempoSignal1), max(tiempoSignal1), min(signal1) * 0.8, max(signal1) * 1.1])
    grafica1[1].hold(True)
    markerline, stemlines, baseline = grafica1[1].stem(tiempoSignal1[pos_signal1], signal1[pos_signal1])
    plt.setp(stemlines, linestyle= '--', color = 'g')
    plt.setp(markerline, markersize=8, color = 'g')
    grafica1[1].set_title(decodeStr('Puntos máximos de señal de pulso 1'))
    grafica1[1].grid(True)

    # Puntos del ECG, para demarcar áreas:
    markerline, stemlines, baseline = grafica1[1].stem(tiempoEcg[pos_ecg_max], ecg[pos_ecg_max] * 2,'r', linewidth=4.0)
    plt.setp(stemlines, linestyle= '--', color = 'r')
    plt.setp(markerline, markersize=8, color = 'r')
                      
    # Señal de pulso 2:
    grafica1[2].plot(tiempoSignal2, signal2)
    grafica1[2].axis([min(tiempoSignal2), max(tiempoSignal2), min(signal2) * 0.8, max(signal2) * 1.1])
    grafica1[2].hold(True)
    markerline, stemlines, baseline = grafica1[2].stem(tiempoSignal2[pos_signal2], signal2[pos_signal2])
    plt.setp(stemlines, linestyle= '--', color = 'g')
    plt.setp(markerline, markersize=8, color = 'g')
    grafica1[2].set_title(decodeStr('Puntos máximos de señal de pulso 2'))
    grafica1[2].grid(True)
    # Puntos del ECG, para demarcar áreas:
    markerline, stemlines, baseline = grafica1[2].stem(tiempoEcg[pos_ecg_max], ecg[pos_ecg_max] * 2,'r', linewidth=4.0)
    plt.setp(stemlines, linestyle= '--', color = 'g')
    plt.setp(markerline, markersize=8, color = 'g')
    plt.xlabel('Segundos')
    plt.show()
