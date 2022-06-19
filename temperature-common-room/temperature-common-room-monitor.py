import time
from MyMQTT import *
import json
import requests 
import datetime

class temperature_patient_room_monitor() :
    def __init__(self) :
        self.conf_file = json.load(open('config.json'))
        r = requests.post(self.conf_file['host']+"/add-service",data =json.dumps ({
            'serviceID' : 4,
            'name' : 'temperature-common-room-monitor'
        }))
        r = requests.get(self.conf_file['host']+"/message-broker")
        mb = r.json()
        self.mqttClient = MyMQTT('temperatrue-common-room-monitor',mb['name'],mb['port'],self)
        r = requests.get(self.conf_file['host']+"/common-room-base-topic")
        t = r.json()
        self.subscribeTopic = t+"+"
        r = requests.get(self.conf_file['host']+"/common-room-hourly-scheduling")
        t = r.json()
        self.hourlyScheduling = t
        r = requests.get(self.conf_file['host']+"/common-room-command-base-topic")
        c = r.json()
        self.commandTopic = c
        self.__baseMessage={"bn" : "temperature-common-room-monitor","bt":0,"r":0,"c" : {"n":"switch","u":"/","v":0}}

        self.mqttClient.start()
        self.mqttClient.mySubscribe(self.subscribeTopic)
        print('starta')

    def updateService(self) :
        while True :
            time.sleep(100)
            r = requests.put(self.conf_file['host']+"/update-service",data = json.dumps({
                'serviceID' : 2,
                'name' : 'temperature-common-room-monitor'
            }))
    

    def getSeason(self) :
        doy = datetime.datetime.today().timetuple().tm_yday
        # "day of year" ranges for the northern hemisphere
        spring = range(80, 172)
        summer = range(172, 264)
        fall = range(264, 355)
        # winter = everything else

        if doy in spring:
            season = 'hot'
        elif doy in summer:
            season = 'hot'
        elif doy in fall:
            season = 'cold'
        else:
            season = 'cold'
        return season

    def defineCommand(self,desiredTemperature,currentTemperature,season) :
        command = 0
        if season == 'hot' and  currentTemperature > desiredTemperature :
                command = 1
        if season == 'cold' and currentTemperature < desiredTemperature : 
                command = 1
        return command

    def expectedPresence(self,currentHour) :
        for rangeHour in self.hourlyScheduling['expected-range-hours'] :
            if currentHour >= rangeHour[0] and currentHour <= rangeHour[1] :
                return True
        return False


    def setTemperature(self,room,presence,currentTemperature) :
        #migliorare questo calcolo
        currentHour =  datetime.datetime.now().hour
        season = self.getSeason()
        r = requests.get(self.conf_file['host']+"/common-room/"+room)
        t = r.json()
        desiredTemperature = t['desired-temperature']
        if  currentHour >= self.hourlyScheduling['night'][0] or currentHour <= self.hourlyScheduling['night'][1] : #night
            if season == 'hot' :
                return self.defineCommand(desiredTemperature+4,currentTemperature,season)
            else :
                return self.defineCommand(desiredTemperature-4,currentTemperature,season)

        else : #not night
            if presence == 1 :
                return self.defineCommand(desiredTemperature,currentTemperature,season)
            else : #not night and not presence 
                expected = self.expectedPresence(currentHour)
                if expected == True and season == 'hot':
                    return self.defineCommand(desiredTemperature+2,currentTemperature,season)
                elif expected == True and season == 'cold':
                    return self.defineCommand(desiredTemperature-2,currentTemperature,season)
                elif expected == False and season == 'hot':
                    return self.defineCommand(desiredTemperature+4,currentTemperature,season)
                elif expected == False and season == 'cold':
                    return self.defineCommand(desiredTemperature-4,currentTemperature,season)
            
    
    def notify(self,topic,payload) :
        message = dict(json.loads(payload))
        

        room = topic.split("/")[-1]
        #fai la richiesta 
        # invoca funzione che ritorna  
        command = self.setTemperature(room,message['e'][1]['v'],message['e'][2]['v'])  
        self.__baseMessage['bt'] = time.time()
        self.__baseMessage['r'] = room
        self.__baseMessage['c']['v'] = command
        self.mqttClient.myPublish(self.commandTopic,self.__baseMessage)     

        print("command "+str({'switch' : command, 'room' : room }))   #rimuoevere
        
if __name__ == "__main__" :
    temperature_patient_room_monitor_istnace = temperature_patient_room_monitor()
    #invocare thread che esegue la registrazione del servizio, che forse è opzionale
    temperature_patient_room_monitor_istnace.updateService()
    #while True :
    #    pass
