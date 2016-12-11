import time
import os, sys
import logging
from datetime import datetime as czas
from os import system as systemowy
import wmi

# definicje stalych i zmiennych aplikacji
# stale okreslajace sciezki aplikacji
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logi')

# katalog logow aplikacji
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# plik logow aplikacji
plikLogow = czas.now().strftime("%Y-%b") + '.log'
plikLogowFull = os.path.join(LOG_DIR, plikLogow)

if not os.path.exists(plikLogowFull):
    logiToFile = open(plikLogowFull, 'w')
    logiToFile.write('SYSTEM INFO|Nazwa komputera|Data/czas|Nazwa procesu|ID Procesu|Opis czynnosci|\n')
    logiToFile.close() 

# konfiguracja systemu logowania aplikacji
logging.basicConfig(
    filename=plikLogowFull,
    level=logging.DEBUG
)

# ----------------------------------------------------------------------------------------
# pozyskanie zmiennych aplikacji z konsoli: nazwa procesu oraz czas testu bezczynnosci
proces = input('Podaj nazwe procesu (bez rozszerzenia): ')
zwloka = input('Podaj czas oczekiwania [s]: ')

# definicja zmiennych na podstawie zebranych informacji z konsoli
procesFull = proces + '.exe'
procesy = []
writeCountOld = {}
writeTransferOld = {}

# test odczytu: w przypadku badania bezczynnosci opartej na odczycie danych procesu
#readCountOld = {}
#readTransferOld = {}

# zapytania modulu systemowego WMI (Windows Management Instrumentation )
wqlFull = '''SELECT CSName, ProcessId, Caption, Description, ReadOperationCount, ReadTransferCount, WriteOperationCount, WriteTransferCount 
                FROM Win32_Process 
                WHERE Caption = '{}'
'''.format(procesFull)

wqlID = '''SELECT ProcessId
                FROM Win32_Process 
                WHERE Caption = '{}'
'''.format(procesFull)

# ----------------------------------------------------------------------------------------
# start aplikacji
c = wmi.WMI(find_classes=False)

# test systemu operacyjnego
for os in c.Win32_OperatingSystem():
    print (os.Caption, '\n')

# pobranie identyfikatorow wybranego aktywnego procesu i umieszczenie ich w tablicy
for identProcesu in c.query(wqlID):
    procesy.append(identProcesu.ProcessId)

# ustawienie wartosci poczatkowych elemntow tablicy procesow
for procesik in procesy:
    writeCountOld[procesik] = 0
    writeTransferOld[procesik] = 0

    # test odczytu
    #readCountOld[procesik] = 0
    #readTransferOld[procesik] = 0

while True:
    for i in c.query(wqlFull):  # for i in c.Win32_Process([lista kolumn w zakladce Procesy Menadzera zadan: 'ProcessId', 'Caption', etc...]):

        # ustawienie wartosci poczatkowych dla nowych identyfikatorow wybranego procesu
        if i.ProcessId not in writeCountOld:     
            writeCountOld[i.ProcessId] = 0

        if i.ProcessId not in writeTransferOld:     
            writeTransferOld[i.ProcessId] = 0

        # test bezczynnosci procesu na podstawie wybranego czasu
        if (i.WriteOperationCount == writeCountOld[i.ProcessId] or i.WriteTransferCount == writeTransferOld[i.ProcessId]):
            systemowy("taskkill /pid %i /f" % i.ProcessId)
            
            # logowanie zdarzen zakonczenia procesu (taskkill)
            logging.info("|%s|%s|%s|%i|Zakonczenie procesu ze wzgledu na bezczynnosc|" % (i.CSName, czas.now().strftime("%Y-%m-%d %H:%M:%S"), i.Caption, i.ProcessId))
         
        else:
        
            # dalsze monitorwanie procesu            
            print ("""
    Nazwa procesu: {}
    ID procesu: {}    

    Odczyty We/Wy: {}
    Odczyty We/Wy [bytes]: {}

    Zapisy We/Wy: {}
    Zapisy We/Wy [bytes]: {}
-------------------------------------------------    
    """.format(i.Caption, i.ProcessId, i.ReadOperationCount, i.ReadTransferCount, i.WriteOperationCount, i.WriteTransferCount))

            writeCountOld[i.ProcessId] = i.WriteOperationCount
            writeTransferOld[i.ProcessId] = i.WriteTransferCount             
            
    time.sleep(int(zwloka))
