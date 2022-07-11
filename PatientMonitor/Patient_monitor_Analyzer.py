import numpy as np

class Patient_Monitor():
    def __init__(self,messagesdict,highBodyTemperature,lowBodyTemperature,wrongBodyTemperature,batteryTheresold,attendabilityTheresold,pulseUpper,pulseLower,saturationTheresold):
        # Estrazione messaggi di allarme
        self.__alarm_Tbattery=messagesdict["alarm_Tbattery"].split("{}")
        self.__alarm_Tplace=messagesdict["alarm_Tplace"].split("{}")
        self.__alarm_Tl=messagesdict["alarm_Tl"].split("{}")
        self.__alarm_Th=messagesdict["alarm_Th"].split("{}")
        self.__alarm_Pbattery=messagesdict["alarm_Pbattery"].split("{}")
        self.__alarm_Pplace=messagesdict["alarm_Pplace"].split("{}")
        self.__alarm_Pl=messagesdict["alarm_Pl"].split("{}")
        self.__alarm_Ph=messagesdict["alarm_Ph"].split("{}")
        self.__alarm_Sl=messagesdict["alarm_Sl"].split("{}")
        self.__highBodyTemperature = highBodyTemperature
        self.__lowBodyTemperature = lowBodyTemperature
        self.__wrongBodyTemperature = wrongBodyTemperature
        self.__batteryTheresold = batteryTheresold
        self.__attendabilityTheresold = attendabilityTheresold 
        self.__pulseUpper = pulseUpper
        self.__pulseLower = pulseLower
        self.__saturationTheresold = saturationTheresold


    def Temperature(self,ID_P,incoming,battery):
        # Suppongo arrivi un valore ogni 1m (1 solo valore, niente lista, quindi niente media)

        # battery è la sola tensione di batteria
        if battery<self.__batteryTheresold: # Per informare che il termometro si sta scaricando (es. suppongo sia scarico a 2.5V)
            alarm=self.__alarm_Tbattery[0]+ID_P+self.__alarm_Tbattery[1]
            #return f"ATTENZIONE, il paziente {ID_P} ha il termometro quasi scarico"
            return alarm

        # incoming è solo il valore di temperatura
        if incoming<=self.__wrongBodyTemperature:# Il sensore è mal posizionato
            alarm=self.__alarm_Tplace[0]+ID_P+self.__alarm_Tplace[1]
            #return f"ATTENZIONE, il paziente {ID_P} ha il termometro mal posizionato"
            return alarm
        if incoming<self.__lowBodyTemperature:
            alarm=self.__alarm_Tl[0]+ID_P+self.__alarm_Tl[1]+str(incoming)+" C"
            #return f"ATTENZIONE, il paziente {ID_P} ha una temperatura bassa, pari a {incoming}"
            return alarm
        if incoming>=self.__highBodyTemperature:
            alarm=self.__alarm_Th[0]+ID_P+self.__alarm_Th[1]+str(incoming)+" C"
            #return f"ATTENZIONE, il paziente {ID_P} ha febbre, con temperatura pari a {incoming}"
            return alarm

    def Pulse(self,ID_P,PI,pulse,sat,battery):
        # Suppongo, per ogni input, arrivi una stringa ogni  10s, con fc=1Hz.
        # Battery, potrebbe essere anche un solo valore ogni 10s(discorso di ridurre i bit mandati)
        alarm=[]
        # battery è la sola tensione di batteria
        if battery<self.__batteryTheresold:# Per informare che il pulsossimetro si sta scaricando (es. suppongo sia scarico a 2.5V)
            alarm.append(self.__alarm_Pbattery[0]+ID_P+self.__alarm_Pbattery[1])
            #return f"ATTENZIONE, il paziente {ID_P} ha il pulsossimetro quasi scarico"
            return alarm

        if max(PI)<self.__attendabilityTheresold: # Cercando su internet, la soglia per una lettura attendibile è al 4%
            # Se nessuna lettura attendibile, inutile proseguire
            alarm.append(self.__alarm_Pplace[0]+ID_P+self.__alarm_Pplace[1])
            #return f"ATTENZIONE, il paziente {ID_P} ha il pulsossimetro mal posizionato o l'ha rimosso"
            return alarm

        to_remove=[]
        for i in range(len(PI)):
            if PI[i]<self.__attendabilityTheresold:
                # Rimuovo dalla stringa eventuali valori non attendibili
                to_remove.append(i)
        to_remove.sort(reverse=True)
        #print(f"Indici rimossi: {to_remove}")
        for rm in to_remove:
            pulse.pop(rm)
            sat.pop(rm)
        #print(f"Lista pulse ottenuta in patient: {pulse}")
        #print(f"Lista sat ottenuta in patient: {sat}")
        
        pulse=np.mean(pulse)
        sat=np.mean(sat)

        if sat<=self.__saturationTheresold:
            alarm.append(self.__alarm_Sl[0]+ID_P+self.__alarm_Sl[1]+str(sat)+" %")
            #alarm=f"ATTENZIONE, il paziente {ID_P} è in ipossia. Saturazione al {sat} % \n"
        if pulse<self.__pulseLower:
            alarm.append(self.__alarm_Pl[0]+ID_P+self.__alarm_Pl[1]+str(pulse)+" bpm")
            #alarm+= f"ATTENZIONE, il paziente {ID_P} ha un battito cardiaco basso: {pulse} bpm"
        elif pulse>self.__pulseUpper:
            alarm.append(self.__alarm_Ph[0]+ID_P+self.__alarm_Ph[1]+str(pulse)+" bpm")
            #alarm+=f"ATTENZIONE, il paziente {ID_P} ha un battito cardiaco alto: {pulse} bpm"
            
        #if len(alarm)>2:
        return alarm