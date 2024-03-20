#Felixel18 on github
#Programm gets an n number long number pad input (with n being the number of items/empty spaces NumberField.CurrentNumber has)
#needs an rasberry pi pico with lcd display and i2c port with sda on pin 20 and scl on pin 21
#also a joystick on pin 26/27 and the joystick button on pin 14/an extra button on pin 14  

from time import sleep_ms
from machine import I2C, Pin, ADC
from machine_i2c_lcd import I2cLcd

class NumberField():
    def __init__(self):
        #Initiate I2C
        self.i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100000)
        #Initiate LCD over I2C
        self.lcd = I2cLcd(self.i2c, 0x27, 4, 20)
        self.Button=Pin(14,Pin.IN, Pin.PULL_UP)
        
        self.joystick_x_pin = ADC(Pin(26)) 
        self.joystick_y_pin = ADC(Pin(27))
        self.Cursory=0
        self.Cursorx=0
        self.NumberPadItems=[["EMPTY",],["0","1","2","3"],["4","5","6","7"],["8","9","Delete","Enter"]]
        self.CurrentNumber=[" "," "," "]
        self.returnBool=False
        self.FirstExtraMarker=19
        self.SecondExtraMarker=19
        self.CurrentBoard=[self.CurrentNumber[0],self.CurrentNumber[1],self.CurrentNumber[2]," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ",
                           " "," "," "," "," ", " "," ",self.NumberPadItems[1][0]," ",self.NumberPadItems[1][1], " ",self.NumberPadItems[1][2]," ",self.NumberPadItems[1][3]," "," "," "," "," "," ",
                           " "," "," "," "," ", " "," ",self.NumberPadItems[2][0]," ",self.NumberPadItems[2][1], " ",self.NumberPadItems[2][2]," ",self.NumberPadItems[2][3]," "," "," "," "," "," ",
                           " "," "," "," "," ", " "," ",self.NumberPadItems[3][0]," ",self.NumberPadItems[3][1], " ", "D", " ","E"," "," "," "," "," "," "]
    def rebuildsCurrentBoard(self):
        self.CurrentBoard=[self.CurrentNumber[0],self.CurrentNumber[1],self.CurrentNumber[2]," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ",
                           " "," "," "," "," ", " "," ",self.NumberPadItems[1][0]," ",self.NumberPadItems[1][1], " ",self.NumberPadItems[1][2]," ",self.NumberPadItems[1][3]," "," "," "," "," "," ",
                           " "," "," "," "," ", " "," ",self.NumberPadItems[2][0]," ",self.NumberPadItems[2][1], " ",self.NumberPadItems[2][2]," ",self.NumberPadItems[2][3]," "," "," "," "," "," ",
                           " "," "," "," "," ", " "," ",self.NumberPadItems[3][0]," ",self.NumberPadItems[3][1], " ", "D", " ","E"," "," "," "," "," "," "]
        self.CurrentBoard[self.FirstExtraMarker]="|"
        self.CurrentBoard[self.SecondExtraMarker]="|"
    def printBoard(self):
        self.rebuildsCurrentBoard()
        for FieldInput in self.CurrentBoard:
            self.lcd.putchar(FieldInput)
    
    def GetExtraMarkers(self):
        if self.Cursory==0:
            self.FirstExtraMarker=19
            self.SecondExtraMarker=19
        elif self.Cursory==3 and self.Cursorx==2:
            self.FirstExtraMarker=70
            self.SecondExtraMarker=72
        elif self.Cursory==3 and self.Cursorx==3:
            self.FirstExtraMarker=72
            self.SecondExtraMarker=74
        else:
            CurrentItem=self.NumberPadItems[self.Cursory][self.Cursorx]
            print(CurrentItem)
            print(self.Cursorx)
            #Copy and rewrite to prevent selector selecting written-down numbers
            CurrentBoardCopy=self.CurrentBoard
            CurrentBoardCopy[0]=" "
            CurrentBoardCopy[1]=" "
            CurrentBoardCopy[2]=" "
            CurrentIndex=CurrentBoardCopy.index(CurrentItem)
            self.FirstExtraMarker=CurrentIndex-1
            self.SecondExtraMarker=CurrentIndex+1
    def start_usage(self):
        #Start screen usage.
        print("Display on")
        self.lcd.display_on()
        print("Background light on")
        self.lcd.backlight_on()
        #Display test Output
        self.lcd.putstr("Initiating display:" + "\n\n" + "Display functioning.")
        sleep_ms(3000)
    def end_usage(self):
        self.lcd.clear()
        self.lcd.putstr("Ended display usage.\nDisplay not functioning.")
        sleep_ms(1000)
        self.lcd.clear()
        sleep_ms(300)
        #End screen usage.
        print("Background light off")
        self.lcd.backlight_off()
        print("Display off")
        self.lcd.display_off()
    def GetLastCurrentNumberPosition(self):
        CurrentNumberLen=len(self.CurrentNumber)
        for CurrentNumIndex in range(CurrentNumberLen):
            CurrentInversedNumIndex=CurrentNumberLen-CurrentNumIndex-1
            if self.CurrentNumber[CurrentInversedNumIndex]!=" ":
                return CurrentInversedNumIndex
        return -1
    def Clicked(self):    
        #Failsafe to prevent crashes
        CurrentItems=self.NumberPadItems[self.Cursory]
        if self.Cursorx>(len(CurrentItems)-1):
            self.Cursorx=len(CurrentItems)-1
        ClickedItem=CurrentItems[self.Cursorx]
        LastBlockedIndex=self.GetLastCurrentNumberPosition()
        if ClickedItem=="EMPTY":
            return
        elif ClickedItem=="Enter":
            self.returnBool=True
            return
        elif ClickedItem=="Delete":
            if LastBlockedIndex==-1:
                return
            else:
                self.CurrentNumber[LastBlockedIndex]=" "
        else:
            if LastBlockedIndex==len(self.CurrentNumber)-1:
                return
            else:
                self.CurrentNumber[LastBlockedIndex+1]=ClickedItem

    #Credit to sage071920 on github for the lcd values
    #Modification to meet cursor expectation
    def handle_joystick_input(self):
        # Read analog values from the joystick
        x_value = self.joystick_x_pin.read_u16()
        y_value = self.joystick_y_pin.read_u16()
        print("x_value: "+str(x_value))
        print("y_value: "+str(y_value))
        
        # Determine joystick direction based on analog values
        # Add hysteresis to joystick input
        if y_value > 61000:
            if not self.Cursory==0:
                self.Cursory-=1
                CurrentListSize=len(self.NumberPadItems[self.Cursory])
                if  CurrentListSize <= self.Cursorx:
                    self.Cursorx=CurrentListSize-1
        elif y_value < 500:
            if not len(self.NumberPadItems)-1==self.Cursory:
                self.Cursory+=1
                CurrentListSize=len(self.NumberPadItems[self.Cursory])
                if  CurrentListSize <= self.Cursorx:
                    self.Cursorx=CurrentListSize-1
        if x_value > 61000:
            if not self.Cursorx==0:
                self.Cursorx-=1
            
        elif x_value < 500:
            if len(self.NumberPadItems[self.Cursory])-1<=self.Cursorx:
                self.Cursorx=len(self.NumberPadItems[self.Cursory])-1
            else:
                self.Cursorx+=1
        self.GetExtraMarkers()
        # Read the button state
        button_state = self.Button.value()
        if button_state==0:
            self.Clicked()
            print("Click")

    def ContinuosRequest(self):
        self.returnBool=False
        


        while True:
            self.handle_joystick_input()
            self.printBoard()
            if self.returnBool:
                break
        CurrentStr=(self.CurrentNumber[0]+self.CurrentNumber[1]+self.CurrentNumber[2]).replace(" ","")
        if CurrentStr=="":
            print("THIS IS A FAILSAFE WHICH SHOULDNT BE ABLE TO BE TRIGGERED.")
        else:
            return int(CurrentStr)


NumPad=NumberField()
print(NumPad.ContinuosRequest())

    #def NumberPad():
        