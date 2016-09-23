import numpy as np

def Filter(original, ven_size, win_vector):
    # Revisando si la longitud del vector es par o impar:
    if ven_size % 2 == 0: # Si es par:
        # Se inicia en:
        ini = int(ven_size / 2)
        # Variable de conteo:
        contador = 0 
        # Variable del vector resultante:
        filt = np.zeros(len(original), type(float))
        # Las mestras que no se procesan se almacenan en el vector resultante:
        # Para las muestras del inicio:
        filt[0:ini] = original[0:ini]    
        # Para las muestras del final:
        filt[len(original) - ini: len(original)] = original[len(original) - ini : len(original)]
        
        # Procesamiento:
        for x in range (ini, len(original)- ini + 1):
            #filt[x] = np.mean(original[x - ini: x + ini])
            filt[x] = sum((original[x - ini: x + ini]) * (win_vector))
        print ("Par")
        #print filt
        
    else: # Si es impar:
        # Se inicia en:
        ini = int((ven_size - 1) / 2)
        # Variable de conteo:
        conteo = 0
        # Variable del vector resultante:
        filt = np.zeros(len(original), type(float))        
        # Las mestras que no se procesan se almacenan en el vector resultante:
        # Para las muestras del inicio:
        filt[0:ini] = original[0:ini]    
        # Para las muestras del final:
        filt[len(original) - ini: len(original)] = original[len(original) - ini : len(original)]
        # Procesamiento:
        for x in range (ini, len(original)- ini ):
            filt[x] = sum((original[x - ini: x + ini + 1 ]) * (win_vector))
            #print original[x - ini: x + ini + 1]
        
        #group_delay = (ven_size - 1)/2
        #filt[group_delay * 2: len(filt) -1]  = filt[group_delay: len(filt) -1 - group_delay]
        #filt[0:group_delay * 2 -1] = original[0:group_delay * 2 -1] 
        
    #filt[0:ven_size + 1] = 0
    #filt[len(filt) - ven_size - 1: len(filt)] = 0
    return filt
    
