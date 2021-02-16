from phBot import *
from tkinter import *  
import phBotChat
import QtBind
import json
import threading
import urllib3
import shutil
import os
from random import randint
import pyqrcode
import sys

http = urllib3.PoolManager()
gui = QtBind.init(__name__, 'Silkroad Remote')
String1 = QtBind.createLabel(gui, 'Veri',20, 20)
String2 = QtBind.createLabel(gui, 'text',20, 260)
String3 = QtBind.createLabel(gui, 'text',20, 40)
String4 = QtBind.createLabel(gui, 'text',600, 260)
send = QtBind.createButton(gui, 'createQR', 'Create QR Code', 20, 70)
stop = QtBind.createButton(gui, 'stop', 'Stop', 120, 70)
path="http://www.mechayazilim.com/dataSave.php" 
notificationPath="http://www.mechayazilim.com/notificationIn.php"
bottingDataPath = "http://www.mechayazilim.com/dataReceive.php"
deadCounter = 0
oldReceiveTrainingRadius = "0"
oldReceiveTrainingAreaX = "0"
oldReceiveTrainingAreaY = "0"
oldReceiveStartBot = "0"
oldReceiveStopBot = "0"
oldMessageCount = 0
setState = False
chatSetState = False
connectedState = True
deger = 1
connectedData = 0
delay = 0
partyMessage = {"partyMessage":[]};
guildMessage = {"guildMessage":[]};
qrId = ""
oneClick = True
QtBind.setText(gui,String1, "Welcome to Silkroad Remote plugin. To connect your bot to the mobile app, please click 'Create QR Code' button and scan it with your phone.")
QtBind.setText(gui,String3, "Visit forum.projecthax.com for updates, suggestions, wishes and complaints.")
QtBind.setText(gui,String2, "*If you want to reload  the plugin, it's recommended to stop it first..")
QtBind.setText(gui,String4, "Version 1.00")
#___________________TRAINING___________________# 

def send_message(): 
    global connectedState
    global deger
    global say
    global connectedData
    global delay
    global qrId
    while deger == 1:
        try:
            if deger == 0:
                log('Silkroad Remote plugin has stopped working.')
                break
            data = get_character_data()
            bottingStatus = get_status()
            with open('Plugins/userInfo/'+ data['server'] + '_' + data['name'] +'.json') as f:
                qrId = json.load(f)
            
            #connection status
            if (delay == 1):
                connectedState = not connectedState
                delay = 0
            delay += 1
            
            
            startBot ="0"
            stopBot = "0"
            if bottingStatus == "botting":
                startBot ="1"
                stopBot ="0"
            else:
                startBot ="0"
                stopBot ="1"
            trainingArea = get_training_position()
            
            ekstraData = {"regionPalace":get_zone_name(data['region']),"deadCounter":deadCounter,"actualTrainingAreaX":trainingArea["x"],"actualTrainingAreaY":trainingArea["y"],"actualTrainingRadius":trainingArea["radius"],"pcStartBot":int(startBot),"pcStopBot":int(stopBot),"connectedState":connectedState,"qrId":qrId}
            getData = data.copy()
            getData.update(ekstraData)
            try:
                resp = http.request('GET', path, fields=getData,timeout=5)
            except ValueError:
                
                pass
            
                
              
            botting()
            chatReceive()
            partyInfoSend()
            inventoryInfoSend()

            
            
            
        except NameError:
            log('[%s] Dısconnected' % __name__)
     
myThread = threading.Thread(target = send_message)


def setProfile():

    reload_profile()

def start():
    global myThread
    while True:
        bottingStatus = get_status()
        if bottingStatus == "botting":
            log('Silkroad Remote Plugin is working..')
            myThread.start()
            break
            

myThread2 = threading.Thread(target = start)   
             

if (myThread.is_alive() == False):
    myThread2.start() 

     
def stop():
    global deger
    deger = 0
    QtBind.setText(gui,String2,"disconnected")
    
 #___________________CHAT___________________#     
 
def handle_chat(t, player, msg):
    global partyMessage
    global guildMessage
    sendPath = "http://www.mechayazilim.com/chatReceive.php"
    if t == 4: #Party
        if len(partyMessage["partyMessage"]) == 10:
            partyMessage["partyMessage"].pop(0)
        partyMessage["partyMessage"].append(player + ': ' +msg)
        chatSend("partyMessage",partyMessage,sendPath)
        
    if t == 5: #Guild
        if len(guildMessage["guildMessage"]) == 10:
            guildMessage["guildMessage"].pop(0)
        guildMessage["guildMessage"].append(player + ': ' +msg)
        chatSend("guildMessage",guildMessage,sendPath)
        
    #if t == 2: #Private
     
     
     
def chatSend(which,data,sendPath):
    sendingMessage = ""
    global qrId
    for messageData in data[which]:
        if sendingMessage == "":
            sendingMessage = messageData
        else:
            sendingMessage = sendingMessage + 'Ψ' + messageData
    character_data = get_character_data()        
    sendingData = {"accountId":character_data['account_id'],which:sendingMessage,"qrId":qrId}; 
    try:
        resp = http.request('GET', sendPath, fields=sendingData,timeout=5)
       
    except:
        log('Chat message could not be sent.')
        pass
        
    
def chatReceive():
    global oldMessageCount
    global chatSetState
    global qrId
    sendPath = "http://www.mechayazilim.com/chatReceive.php"
    character_data = get_character_data()        
    sendingData = {"accountId":character_data["account_id"],"qrId":qrId}  
    try:
        resp = http.request('GET', sendPath, fields=sendingData,timeout=5)
    except:
        log('Chat data could not be received.')
        pass
    try:
        bottingRequestText = json.loads(resp.data.decode('utf-8'))
        for p in bottingRequestText['androidToPcData']:
            receiveMessage = p['sendMessage']
            whichChat = p['whichChat']
            messageCount = p['sendMessageCount']
            if (oldMessageCount != messageCount) and (chatSetState == True):
                if whichChat == "0":
                    phBotChat.Party(receiveMessage)
                if whichChat == "1":
                    phBotChat.Guild(receiveMessage)
                
                
            oldMessageCount = messageCount
            chatSetState = True
    except:
        pass
    
#___________________PARTY ___________________# 

def partyInfoSend():
    sendPath = "http://www.mechayazilim.com/partyReceive.php"
    character_data = get_character_data()  
    partyInfo = get_party()
    global qrId
    sendingMessage = ""
    for p in partyInfo:
        sendingMessage = sendingMessage + str(partyInfo[int(p)]['name'])+  '☽' + str(partyInfo[int(p)]['hp_percent']) +  '☽' + str(partyInfo[int(p)]['mp_percent']) + 'Ψ' 
    sendingData = {"accountId":character_data['account_id'],"partyUsers":sendingMessage,"qrId":qrId};    
    try:
        resp = http.request('GET', sendPath, fields=sendingData,timeout=5)
        
    except:
        log('PartyInfo could not be sent')
        pass

#___________________INVENTORY___________________# 
        
def inventoryInfoSend():
    sendPath = "http://mechayazilim.com/itemReceive.php"
    inventoryData= get_inventory()
    character_data = get_character_data()  
    global qrId
    sendingMessage = ""
    
    for i in range(0,len(inventoryData['items'])): 
        if inventoryData['items'][i] != None:
            name = str(inventoryData['items'][i]['name'])
            plus = str(inventoryData['items'][i]['plus'])
            quantity = str(inventoryData['items'][i]['quantity'])
            data = quantity + '☽' + plus +  '☽' + name + 'Ψ'
            sendingMessage = sendingMessage + data 
           
    sendingMessage=sendingMessage.replace("'","")
    sendingData = {'accountId':character_data['account_id'],'itemData':sendingMessage,'qrId':qrId}
    try:

        resp = http.request('GET', sendPath, fields=sendingData,timeout=5)
        
    except:
        log('Item info could not be sent.')
        pass
          
          
#___________________GAME EVENTS___________________#     
     
def handle_event(t, data):
    global deadCounter
    global qrId
    accountData = get_character_data()

    if t == 7:
        
        notificationData = {"accountId":accountData["account_id"],"notificationCount":"0","qrId":qrId}
        getNotificationData = notificationData.copy()
        try:
            resp = http.request('GET', notificationPath, fields=getNotificationData,timeout=5)
        except:
            log('Death notification could not be sent.')
            pass
        deadCounter += 1
    if t == 5:
        
        notificationData = {"accountId":accountData["account_id"],"notificationCount":"1","qrId":qrId}
        getNotificationData = notificationData.copy()
        try:
            resp = http.request('GET', notificationPath, fields=getNotificationData,timeout=5)
        except:
            log('Rare item drop could not be sent.')
            pass


    

    
def botting():
    global oldReceiveTrainingRadius
    global oldReceiveTrainingAreaX
    global oldReceiveTrainingAreaY
    global oldReceiveStartBot
    global oldReceiveStopBot
    global setState
    global qrId
    global bottingDataPath
    
    trainingArea = get_training_position()
    accountData = get_character_data()
    bottingData = {"accountId":accountData["account_id"],"qrId":qrId}
    getBottingData = bottingData.copy()
    try:
        resp = http.request('GET', bottingDataPath, fields=getBottingData,timeout=5)
       
    except:
        
        pass
    try:
        bottingRequestText = json.loads(resp.data.decode('utf-8')) 
        for p in bottingRequestText['androidToPcData']:
            trainingRadius = p['trainingRadius']
            trainingAreaX = p['trainingAreaX']
            trainingAreaY = p['trainingAreaY']
            receiveStartBot = p['startBot']
            receiveStopBot = p['stopBot']
            
            if ((oldReceiveTrainingRadius != trainingRadius) or (oldReceiveTrainingAreaX != trainingAreaX) or (oldReceiveTrainingAreaY !=trainingAreaY)) and setState == True:
                set_training_position(0, float(trainingAreaX), float(trainingAreaY), 0.0)
                set_training_radius(float(trainingRadius))
                
            if ((oldReceiveStartBot != receiveStartBot) or  (oldReceiveStopBot !=receiveStopBot)) and setState ==True:
                if receiveStartBot == "1":
                    start_bot()
                else:
                    stop_bot()
                

            oldReceiveTrainingRadius = trainingRadius
            oldReceiveTrainingAreaX = trainingAreaX
            oldReceiveTrainingAreaY =trainingAreaY
            oldReceiveStartBot = receiveStartBot
            oldReceiveStopBot =receiveStopBot
            setState = True
    except:
        log("Error")
    
#___________________QR CODE___________________# 

def createQR():
    global oneClick
    
    if oneClick == True:
        oneClick = False
        character_data = get_character_data() 
        sendPath = "http://www.mechayazilim.com/qrReceive.php"
        global qrId    
        accountId = character_data['account_id']
        playerId = character_data['player_id']
        server = character_data['server']
        name = character_data['name']
        creatingQR = str(accountId) + '~' +  str(playerId) + '~' + str(server)+ '~' + str(name)+ '~' +str(randint(100000, 9999999))
        
        if os.path.isfile('Plugins/userInfo'):
            pass
        else:
            try:
                os.mkdir('Plugins/userInfo')
            except:
                pass
        with open('Plugins/userInfo/'+ character_data['server'] + '_' + character_data['name'] + '.json', 'w') as json_dosya:
            json.dump(creatingQR, json_dosya)
     
        sendingData = {'newQrId':creatingQR,'oldQrId':qrId}
        getData = character_data.copy()
        getData.update(sendingData)
        try:
            resp = http.request('GET', sendPath, fields=getData,timeout=5)
            createQRCodeShow(creatingQR)
            
        except:
            log('QR Code could not be sent.')
            pass

 
sayi = ""

def createQRCodeShow(creatingQR):
    global oneClick
    global window
    if creatingQR != "":
        window = Tk()
        window_height = 500
        window_width = 300
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))

        window.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        window["bg"] = "#ffffff"
        window["bd"] = 1
        window.overrideredirect(1)
        
        notificationLabel= Label(window)
        notificationLabel.grid(row= 1, column=0, sticky= N+S+E+W)
        myQr = pyqrcode.create(creatingQR)
        qrImage = myQr.xbm(scale=6)
        photo = BitmapImage(data=qrImage)
        notificationLabel.config(image= photo,width=300, bg='#ffffff',borderwidth=2, relief="ridge")
        
        lab1 = Label(window, text="Please scan the QR Code\nfrom Silkroad Remote App",  font=("Helvetica", 16,),bg='#ffffff',fg='black',borderwidth=2, relief="ridge")
        lab1.grid(row=0, column= 0, sticky= N+S+E+W)

        
        
        

        #Making responsive layout:
        totalRows= 2
        totalCols = 1

        for row in range(totalRows+1):
            window.grid_rowconfigure(row, weight=1)

        for col in range(totalCols+1):
            window.grid_columnconfigure(col, weight=1)

        #looping the GUI
        saydir("Closing in 3..")
        window.after(1000, lambda: saydir("Closing in 2.."))  # 2
        window.after(2000, lambda: saydir("Closing in 1.."))  # 1 
        window.after(3000, lambda: saydir("Closing in 0.."))  # 0
        
        
        window.after(4000, lambda: deneme()) 
        window.after(4000, lambda: window.destroy()) 
        
        window.mainloop()    
        
def saydir(sayi2):
    global window
    lab2 = Label(window, text = sayi2,  font=("Helvetica", 26,),bg='#111111',fg='#ffffff',borderwidth=2, relief="ridge")
    lab2.grid(row=2, column= 0, sticky= N+S+E+W)
    
    
def deneme():
    global oneClick
    oneClick = True
    