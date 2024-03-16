import pygame,sys,math,random,os,copy,pickle
from pygame.locals import *
pygame.init()
screen = pygame.display.set_mode((1000,700),RESIZABLE)
fpsClock = pygame.time.Clock()

#Fonts
font1=pygame.font.Font('Assets/Montserrat-Semibold.ttf', 16)#Main font
smallFont=pygame.font.Font('Assets/Montserrat-Semibold.ttf', 10)#Smaller Font

savesList=[]

#Images
for filename in os.listdir("Assets"):#Loads assets 
    if filename.endswith(".png"):
        vars()[str(filename[:-4])]=pygame.image.load("Assets/"+filename).convert_alpha()

    elif filename.endswith(".jpg"):
        vars()[str(filename[:-4])]=pygame.image.load("Assets/"+filename).convert()


for filename in os.listdir("Saves"):#Loads saves       
    if filename.endswith(".p"):
        if filename!="integratedCircuits.p":
            savesList.append(filename[:-2])
pygame.display.set_icon(icon_img)#Sets icon to an and gate
            
#Sounds
beep=pygame.mixer.Sound("Assets/beep.wav")
beep.set_volume(0.2)

#Variables
camerax=0
cameray=0
mouseDownCamerax=0#Location of camera when mouse goes down
mouseDownCameray=0
zoomLevel=1.0#How zoomed in the user is, 1 being the maximum, it will be used as a scalar
zoomSpeed=0.1#Speed that zoom changes
mousex,mousey=400,400
mouseDownx,mouseDowny=0,0
minimumWindowWidth,minimumWindowHeight=800,500
selectedMenu="Gates"
selectedTool="Mouse"
selectedItem=""
currentFile="New File"
leftMouseClicked=False
rightMouseClicked=False
leftMouseDown=False
rightMouseDown=False

##Circuit Building Variables
gridSize=20
gridToggle=True
fullscreenToggle=False
developerToggle=False
componentList=[]
wireList=[]
commentList=[]
integratedList=[]
windowList=[]#Used to store all open windows
currentID=1
wireStartID,wireEndID=0,0
wireStartType=""
wireStartSlot=0
integratedName=""
wireThickness=4
stopWire=False #Used to track when the wire should stop being placed
speed = 1
commentx,commenty = None,None
comment=""

##Colours
backgroundDefaultColour,gridDefaultColour,wireOffDefaultColour,wireOnDefaultColour,commentDefaultColour=(255,255,255),(150,150,150),(0,0,0),(0,255,0),(0,0,0)
backgroundColour,gridColour,wireOffColour,wireOnColour,commentColour=backgroundDefaultColour,gridDefaultColour,wireOffDefaultColour,wireOnDefaultColour,commentDefaultColour

class Menu():
    def __init__(self,menuName,items):
        self.menuName=menuName
        self.text=font1.render(str(self.menuName),True,(255,255,255))
        self.textWidth=self.text.get_width()
        self.items=items
    def drawMenuSelect(self,x):
        global selectedMenu,selectedTool
        if selectedMenu==self.menuName:#Checking if it is selected Menu
            pygame.draw.rect(screen,(100,100,100),(x-5,0,self.textWidth+10,20),0)
            
        if collide(mousex,mousey,x-5,0,self.textWidth+10,20):#Checking mouse collisions
            if leftMouseClicked==True:
                selectedMenu=self.menuName
                selectedTool="Mouse"
                pygame.mouse.set_cursor(*pygame.cursors.arrow)
            elif selectedMenu!=self.menuName:
                pygame.draw.rect(screen,(60,60,60),(x-5,0,self.textWidth+10,20),0)
        screen.blit(self.text,(x,0))

    def drawMenusItems(self):
        if selectedMenu==self.menuName:
            if self.menuName=="Options":
                drawOptionsMenu()
            elif self.menuName=="Integrated":
                drawIntegratedMenu()
                xPos=5
                for item in self.items:
                    item.drawMenuItem(xPos)
                    if xPos==55:
                        xPos+=110
                    xPos+=50
                
            else:
                xPos=5
                for item in self.items:
                    item.drawMenuItem(xPos)
                    xPos+=50

        



class MenuButton():
    def __init__(self,buttonName,image):
        self.buttonName=buttonName
        self.image=image
    def drawMenuButton(self,x):
        global selectedTool,selectedItem,wireList,componentList,camerax,cameray,zoomLevel,windowList,SideMenuInputBox,currentFile,windowList,commentList
        if selectedTool==self.buttonName:#Checking if it is selected Menu button
            pygame.draw.rect(screen,(100,100,100),(x,0,20,20),0)
            
        if collide(mousex,mousey,x,0,20,20):#Checking mouse collisions
            if leftMouseClicked==True:
                selectedTool=self.buttonName
                selectedItem=""
                if selectedTool=="Move":
                    pygame.mouse.set_cursor(*pygame.cursors.broken_x)
                else:
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)

                if selectedTool=="New":
                    wireList=[]
                    componentList=[]
                    windowList=[]
                    commentList=[]
                    camerax=0
                    cameray=0
                    zoomLevel=1
                    SideMenuInputBox=InputBox("")
                    selectedTool="Mouse"
                    currentFile = "New File"
                    setCaption()

                elif selectedTool=="Help":
                    windowList.append(GuideMenu(guideList[0].name))
                    selectedTool = "Mouse"
                     
            elif selectedTool!=self.buttonName:
                pygame.draw.rect(screen,(60,60,60),(x,0,20,20),0)
            ##Shows info about button
            infoText=smallFont.render(str(self.buttonName),True,(255,255,255))
            screen.blit(infoText,(mousex-30,mousey+10))
        screen.blit(self.image,(x,0))

#Creating menu buttons 
menuButtonObjects=[MenuButton("Mouse",mouseIconImage),
                   MenuButton("Delete",deleteIconImage),
                   MenuButton("Move",moveIconImage),
                   MenuButton("Comment",commentIconImage),
                   MenuButton("Load",loadIconImage),
                   MenuButton("Save",saveIconImage),
                   MenuButton("New",newIconImage),
                   MenuButton("Help",helpIconImage)]

class MenuItem():#Boxes/ items for each menu option
    def __init__(self,itemName,itemImage):
        self.itemName=itemName
        self.image=itemImage
    def drawMenuItem(self,x):
        global selectedItem,selectedTool,integratedList,menuObjects,integratedName,windowList,integratedList,menuObjects
        if selectedItem==self.itemName:
            pygame.draw.rect(screen,backgroundColour,(x,25,44,44),0)#Each item should be 40x40, so the box is 44x44 just abit bigger
            pygame.draw.rect(screen,(255,0,0),(x,25,44,44),2)
            screen.blit(self.image,(x+2,27))
        elif collide(mousex,mousey,x,25,50,50):
            pygame.draw.rect(screen,backgroundColour,(x,25,44,44),0)
            pygame.draw.rect(screen,(120,120,120),(x,25,44,44),2)
            infoText=font1.render(self.itemName.upper(),True,commentColour)
            if self.itemName == "Switch" or self.itemName == "Basics":
                screen.blit(infoText,((x+30)-infoText.get_width()/2,70))
            else:
                screen.blit(infoText,((x+22)-infoText.get_width()/2,70))
            if leftMouseClicked==True:
                if selectedMenu=="Guides":#If guide menu selected
                    windowList.append(GuideMenu(self.itemName))
                    
                elif self.itemName=="New":##Creates new integrated cirucit if new is clicked
                    if integratedName!="":
                        for i in integratedList:
                            if i.name==integratedName:
                                return
                        integratedList.append(IntegratedCircuit())
                        menuObjects[3].items.append(MenuItem(integratedList[-1].name,complexGateImage))
                        integratedName=""
                        enterIntegratedText=False
                        IntegratedInputBox.entering=False#Resets variables for integrated circuits
                        IntegratedInputBox.value=""
                        saveIntegrated()
                elif selectedMenu=="Integrated" and selectedItem=="Delete" and self.itemName!="Delete":
                    for i in integratedList:##Deletes an integrated circuits
                        if i.name == self.itemName:
                            integratedList.remove(i)#Removes from saves and menu
                            saveIntegrated()
                            menuObjects[3].items.remove(self)
                            selectedItem=""
                            selectedTool="Mouse"
                        
                else:
                    selectedItem=self.itemName
                    selectedTool=""
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
            screen.blit(self.image,(x+2,27))
        else:
            pygame.draw.rect(screen,backgroundColour,(x,22,44,44),0)
            pygame.draw.rect(screen,(0,0,0),(x,22,44,44),2)
            screen.blit(self.image,(x+2,24))
        


##Menu object list
menuObjects=[Menu("Gates",[MenuItem("and",andGateImage),MenuItem("or",orGateImage),MenuItem("not",notGateImage),MenuItem("nand",nandGateImage),MenuItem("nor",norGateImage),MenuItem("xor",xorGateImage),MenuItem("buffer",bufferGateImage)]),
             Menu("Inputs",[MenuItem("Switch",switchOffImage),MenuItem("Button",buttonOffImage),MenuItem("Clock",pulseImage)]),
             Menu("Outputs",[MenuItem("LED",lightOffImage),MenuItem("Speaker",speakerOffImage),MenuItem("7-Segment Display",displayImage)]),
             Menu("Integrated",[MenuItem("New",newCircuitImage),MenuItem("Delete",deleteCircuitImage)]),
             #Menu("Additional",[]),
             Menu("Guides",[MenuItem("Basics",guideImage),MenuItem("Adder",guideImage)]),
             Menu("Options",[])]


class CheckBox():
    def __init__(self,variable):
        self.value=variable#Sets value to true or false
        
    def drawCheckBox(self,x,y):
        pygame.draw.rect(screen,(255,255,255),(x,y,20,20),0)
        if collide(mousex,mousey,x,y,20,20):
            pygame.draw.rect(screen,(120,120,120),(x,y,20,20),2)#Makes it different colour when mouse over it
            if leftMouseClicked==True:
                self.value = not self.value
        else:
            pygame.draw.rect(screen,(0,0,0),(x,y,20,20),1)

        if self.value==True:
            pygame.draw.line(screen,(0,0,0),(x+5,y+15),(x+15,y+5),4)#This is ticks
            pygame.draw.line(screen,(0,0,0),(x+5,y+15),(x+3,y+10),4)
        return self.value


#####Components

class Component():
    def __init__(self):
        self.x=camerax+roundDown(mousex*(1/zoomLevel)-(gridSize/2)*zoomLevel,gridSize*zoomLevel)#sets x and y of components relative to camera
        self.y=cameray+roundDown(mousey*(1/zoomLevel)-(gridSize/2)*zoomLevel,gridSize*zoomLevel)
        self.item=selectedItem
        self.ID=currentID
        self.state=0
        self.width=40
        self.name=""
        self.integrated=False#Checks to see if it is an integrated circuit
    def collision(self):
        global wireStartID,wireEndID,currentID,wireList,currentID,wireStartType,windowList,SideMenuInputBox,wireStartSlot,wireList,componentList,stopWire

        loopCount=0
        for i in self.outputs:
            if collide(mousex,mousey,(int(self.x+self.width*i[1]-camerax-5)*zoomLevel),(self.y+40*i[2]-cameray-5)*zoomLevel,10*zoomLevel,10*zoomLevel):
                pygame.draw.rect(screen,(50,50,50),((self.x+self.width*i[1]-camerax-5)*zoomLevel,(self.y+40*i[2]-cameray-5)*zoomLevel,10*zoomLevel,10*zoomLevel),2)
                if self.integrated==True:#If it is an integrated Circuit it will show info about the connections name
                    nameText=smallFont.render(str(self.outputNames[loopCount]),True,(0,0,0))
                    screen.blit(nameText,(mousex-40,mousey+10))                    

                
                if leftMouseClicked == True:
                    if wireStartID == 0:
                        wireStartID = self.ID
                        i[0].append(currentID)
                        wireStartSlot = loopCount
                        wireStartType = "Output"
                    elif wireStartID != 0 and wireStartType=="Input":
                        wireEndID = wireStartID#Swapping start and end, as the wrong way round
                        wireStartID=self.ID
                        i[0].append(currentID)
                        wireList.append(Wire(wireStartID,wireEndID))
                        wireStartID=0
                        wireEndID=0
                        wireStartType=0
                        wireStartSlot=0
                        currentID+=1
                    stopWire=False
                    return      
            loopCount+=1#Loop count to know where current wire is being placed, in case it needs to be deleted


        loopCount=0 
        for i in self.inputs:
            if collide(mousex,mousey,(self.x+self.width*i[1]-camerax-5)*zoomLevel,(self.y+40*i[2]-cameray-5)*zoomLevel,10*zoomLevel,10*zoomLevel):

                if self.integrated==True:#If it is an integrated Circuit it will show info about the connections name
                    nameText=smallFont.render(str(self.inputNames[loopCount]),True,(0,0,0))
                    screen.blit(nameText,(mousex-40,mousey+10))  
                
                if i[0]=="free":
                    pygame.draw.rect(screen,(50,50,50),((self.x+self.width*i[1]-camerax-5)*zoomLevel,(self.y+40*i[2]-cameray-5)*zoomLevel,10*zoomLevel,10*zoomLevel),2)
                    #Connecting wire to a components inputs
                    if leftMouseClicked == True:
                        if wireStartID == 0:
                            wireStartID = self.ID
                            i[0] = currentID
                            wireStartSlot = loopCount
                            wireStartType = "Input"
                            
                        elif wireStartID != 0 and wireStartType == "Output":
                            i[0] = currentID
                            wireEndID=self.ID
                            wireList.append(Wire(wireStartID,wireEndID))
                            wireStartID=0
                            wireEndID=0
                            wireStartType=0
                            wireStartSlot=0
                            currentID+=1
                        stopWire=False
                        return

            loopCount+=1


        #Bringing up the item's side menu:   
        if collide(mousex,mousey,(self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel,self.width*zoomLevel,self.width*zoomLevel):#If item right clicked
            nameText=smallFont.render(self.name,True,commentColour)
            screen.blit(nameText,(mousex-40,mousey+10))
            if rightMouseClicked==True:
                windowList=[]#resets list first, should change later to allow many windows at once
                windowList.append(SideMenu(self.ID))
                SideMenuInputBox=InputBox(self.name)#Resets with new components name

    def checkDelete(self):
        global wireList,componentList
        if collide(mousex,mousey,(self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel,self.width*zoomLevel,self.width*zoomLevel):#If item left clicked
            if leftMouseClicked == True and selectedTool == "Delete":#Detects if object has been clicked to delete
                ##Need to loop through wires, if start or end ID the same delete that wire, also cycle through components to find the other end of the wire and clear contents of its inputs or outputs

                for wire in wireList:
                    if wire.startID ==self.ID or wire.endID == self.ID:
                        for component in componentList:
                            
                            if wire.startID == component.ID:##Removes wire from outputs
                                for out in component.outputs:
                                    if wire.ID in out[0]:
                                        out[0].remove(wire.ID)
                                        
                            elif wire.endID == component.ID:##Removes wire from inputs
                                for inp in component.inputs:
                                    if wire.ID == inp[0]:
                                        inp[0]="free"
                        wireList.remove(wire)
                componentList.remove(self)## Deletes component by reffering to itself


class Wire():
    def __init__(self,startID,endID):
        self.startID=startID
        self.endID=endID
        self.ID=currentID
        self.state=0
        self.colour=(0,0,0)
    def draw(self):
        startx,starty,endx,endy="","","",""
        for i in componentList:
            if i.ID==self.startID:
                for out in i.outputs:#Check outputs for start position
                    if self.ID in out[0]:
                        startx,starty=(i.x+i.width*out[1]-camerax)*zoomLevel,(i.y+40*out[2]-cameray)*zoomLevel
                        
            elif i.ID==self.endID:
                for inp in i.inputs:#Check inputs for end position
                    if inp[0]==self.ID:
                        endx,endy=(i.x+i.width*inp[1]-camerax)*zoomLevel,(i.y+40*inp[2]-cameray)*zoomLevel

            if startx!="" and starty!="" and endx!="" and endy!="":
                ##Draw Wire
                if self.state==False:
                    pygame.draw.line(screen,wireOffColour,(startx,starty),(endx,endy),int(zoomLevel*wireThickness))
                else:
                    pygame.draw.line(screen,wireOnColour,(startx,starty),(endx,endy),int(zoomLevel*wireThickness))
    def setState(self,components,wires):       
        for i in components:
            if self.startID==i.ID:
                for out in i.outputs:
                    if self.ID in out[0]:
                        self.state = out[3]#Set state to components output state

class IntegratedCircuit(Component):
    def __init__(self):
        Component.__init__(self)
        self.internalComponentList=copy.deepcopy(componentList)#Creates it's own list of components, used for top bar, this is not the circuit which gets placed
        self.internalWireList=copy.deepcopy(wireList)
        self.name=integratedName

        numOutputs=0
        numInputs=0
    
        self.outputIDs=[]
        self.inputIDs=[]

        self.outputNames=[]#Used to show names of connections
        self.inputNames=[]

        self.integrated=True

        
        for i in self.internalComponentList:##Setting up all input and outputs
            if i.item == "Switch":
                numInputs+=1
                self.inputIDs.append(i.ID)
                self.inputNames.append(i.name)
            elif i.item == "LED":
                numOutputs+=1
                self.outputIDs.append(i.ID)
                self.outputNames.append(i.name)

        self.inputs,self.outputs=[],[]
        for i in range(numOutputs):
            self.outputs.append([[],(i+1)/(1+numOutputs),0,False])
        for i in range(numInputs):
            self.inputs.append(["free",(i+1)/(1+numInputs),1])##Both add 1 so wire connections are centered

        self.width=max(30,max(numInputs,numOutputs)*10,smallFont.render(self.name,True,(0,0,0)).get_width()+10)



class IntegratedGate(Component):
    def __init__(self,internalComponentList,internalWireList,item,outputIDs,inputIDs,outputs,inputs,width,outputNames,inputNames):#Will get this from a loop, when placing, taken from IntegratedCircuit of the correct name
        Component.__init__(self)
        self.internalComponentList=copy.deepcopy(internalComponentList)
        self.internalWireList=copy.deepcopy(internalWireList)
        self.item=item
        self.outputIDs=outputIDs.copy()
        self.inputIDs=inputIDs.copy()
        self.outputs=copy.deepcopy(outputs)
        self.inputs=copy.deepcopy(inputs)
        self.width=width
        self.outputNames=outputNames
        self.inputNames=inputNames
        self.integrated=True
    def draw(self):
        pygame.draw.rect(screen,(255,255,255),((self.x+5-camerax)*zoomLevel,(self.y+5-cameray)*zoomLevel,self.width*zoomLevel,30*zoomLevel),0)
        pygame.draw.rect(screen,(0,0,0),((self.x+5-camerax)*zoomLevel,(self.y+5-cameray)*zoomLevel,self.width*zoomLevel,30*zoomLevel),int(2*zoomLevel))
        for i in self.outputs:
            pygame.draw.line(screen,(0,0,0),((self.x-camerax+self.width*i[1])*zoomLevel,(self.y-cameray)*zoomLevel),((self.x-camerax+self.width*i[1])*zoomLevel,(self.y-cameray+5)*zoomLevel),int(2*zoomLevel))
        for i in self.inputs:
            pygame.draw.line(screen,(0,0,0),((self.x-camerax+self.width*i[1])*zoomLevel,(self.y-cameray+40)*zoomLevel),((self.x-camerax+self.width*i[1])*zoomLevel,(self.y-cameray+35)*zoomLevel),int(2*zoomLevel))
        textImg=smallFont.render(self.item,True,(0,0,0))##Renders text to display on the gate!!!!!
        screen.blit(textImg,((self.x+10-camerax)*zoomLevel,(self.y-cameray+14)*zoomLevel))
    def setState(self,components,wires):

        #Firstly I will set all of the internal switches to the related input, so the outputs in the switches are correct
        for wire in wires:
            loopCount=0
            for inp in self.inputs:
                if wire.ID==inp[0]:
                        for i in self.internalComponentList:
                            if i.ID == self.inputIDs[loopCount]:
                                if wire.state==True:
                                    i.outputs[0][3] = True#Sets output of the internal inputs, so these are starting values
                                else:
                                    i.outputs[0][3] = False
                loopCount+=1


        #I will then test all internal LED's and set them to the output values
        for i in self.internalComponentList:
            if i.item!="Switch":
                i.setState(self.internalComponentList,self.internalWireList)
            if i.item == "LED":
                loopCount=0
                for out in self.outputIDs:
                    if out==i.ID:
                        if i.state == True:
                            self.outputs[loopCount][3] = True
                        else:
                            self.outputs[loopCount][3] = False
                    loopCount+=1

        for wire in self.internalWireList:
            wire.setState(self.internalComponentList,self.internalWireList)


class AndGate(Component):
    def __init__(self):
        Component.__init__(self)
        self.outputs=[[[],0.5,0,False]]#x and y multipliers of where wire will connect
        self.inputs=[["free",0.25,1],["free",0.75,1]]#free?, x multiplyer, y multiplyer

    def draw(self):
        image=pygame.transform.scale(andGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
        screen.blit(image,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))
    def setState(self,components,wires):
        positive=0#How many inputs are 1
        for wire in wires:
            if wire.ID == self.inputs[0][0] or wire.ID == self.inputs[1][0]:
                if wire.state==True:
                    positive+=1
        if positive==2:
            self.outputs[0][3]=True
        else:
            self.outputs[0][3]=False


class NandGate(Component):
    def __init__(self):
        Component.__init__(self)
        self.outputs=[[[],0.5,0,False]]#x and y multipliers of where wire will connect
        self.inputs=[["free",0.25,1],["free",0.75,1]]#free?, x multiplyer, y multiplyer

    def draw(self):
        image=pygame.transform.scale(nandGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
        screen.blit(image,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))
    def setState(self,components,wires):
        positive=0#How many inputs are 1
        for wire in wires:
            if wire.ID == self.inputs[0][0] or wire.ID == self.inputs[1][0]:
                if wire.state==True:
                    positive+=1
        if positive==2:
            self.outputs[0][3]=False
        else:
            self.outputs[0][3]=True


class XorGate(Component):
    def __init__(self):
        Component.__init__(self)
        self.outputs=[[[],0.5,0,False]]#x and y multipliers of where wire will connect
        self.inputs=[["free",0.25,1],["free",0.75,1]]#free?, x multiplyer, y multiplyer

    def draw(self):
        image=pygame.transform.scale(xorGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
        screen.blit(image,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))
    def setState(self,components,wires):
        positive=0#How many inputs are 1
        for wire in wires:
            if wire.ID == self.inputs[0][0] or wire.ID == self.inputs[1][0]:
                if wire.state==True:
                    positive+=1
        if positive==1:
            self.outputs[0][3]=True
        else:
            self.outputs[0][3]=False



class NorGate(Component):
    def __init__(self):
        Component.__init__(self)
        self.outputs=[[[],0.5,0,False]]#x and y multipliers of where wire will connect
        self.inputs=[["free",0.25,1],["free",0.75,1]]#free?, x multiplyer, y multiplyer

    def draw(self):
        image=pygame.transform.scale(norGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
        screen.blit(image,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))
    def setState(self,components,wires):
        positive=0#How many inputs are 1
        for wire in wires:
            if wire.ID == self.inputs[0][0] or wire.ID == self.inputs[1][0]:
                if wire.state==True:
                    positive+=1
        if positive>=1:
            self.outputs[0][3]=False
        else:
            self.outputs[0][3]=True

class NotGate(Component):
    def __init__(self):
        Component.__init__(self)
        self.outputs=[[[],0.5,0,False]]#x and y multipliers of where wire will connect
        self.inputs=[["free",0.5,1]]#free?, x multiplyer, y multiplyer

    def draw(self):
        image=pygame.transform.scale(notGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
        screen.blit(image,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))
    def setState(self,components,wires):
        positive=0#How many inputs are 1
        for wire in wires:
            if wire.ID == self.inputs[0][0]:
                self.outputs[0][3]=not wire.state#Sets state to the opposite of the wire


class BufferGate(Component):
    def __init__(self):
        Component.__init__(self)
        self.outputs=[[[],0.5,0,False]]#x and y multipliers of where wire will connect
        self.inputs=[["free",0.5,1]]#free?, x multiplyer, y multiplyer

    def draw(self):
        image=pygame.transform.scale(bufferGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
        screen.blit(image,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))
    def setState(self,components,wires):
        positive=0#How many inputs are 1
        for wire in wires:
            if wire.ID == self.inputs[0][0]:
                self.outputs[0][3]=wire.state





class OrGate(Component):
    def __init__(self):
        Component.__init__(self)
        self.outputs=[[[],0.5,0,False]]#x and y multipliers of where wire will connect
        self.inputs=[["free",0.25,1],["free",0.75,1]]#free?, x multiplyer, y multiplyer

    def draw(self):
        image=pygame.transform.scale(orGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
        screen.blit(image,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))
    def setState(self,components,wires):
        positive=0#How many inputs are 1
        for wire in wires:
            if wire.ID == self.inputs[0][0] or wire.ID == self.inputs[1][0]:
                if wire.state==True:
                    positive+=1
        if positive>0:
            self.outputs[0][3]=True
        else:
            self.outputs[0][3]=False

class LED(Component):
    def __init__(self):
        Component.__init__(self)
        self.outputs=[]#x and y multipliers of where wire will connect
        self.inputs=[["free",0.5,1]]#free?, x multiplyer, y multiplyer

    def draw(self):
        if self.state==False:
            image=pygame.transform.scale(lightOffImage,(int(40*zoomLevel),int(40*zoomLevel)))
        else:
            image=pygame.transform.scale(lightOnImage,(int(40*zoomLevel),int(40*zoomLevel)))
        screen.blit(image,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))
    def setState(self,components,wires):
        for wire in wires:
            if wire.ID==self.inputs[0][0]:
                self.state = wire.state



class Speaker(Component):
    def __init__(self):
        Component.__init__(self)
        self.outputs=[]#x and y multipliers of where wire will connect
        self.inputs=[["free",0.5,1]]#free?, x multiplyer, y multiplyer

    def draw(self):
        if self.state==False:
            image=pygame.transform.scale(speakerOffImage,(int(40*zoomLevel),int(40*zoomLevel)))
        else:
            image=pygame.transform.scale(speakerOnImage,(int(40*zoomLevel),int(40*zoomLevel)))
            if not pygame.mixer.get_busy():
                beep.play()##Play a beep sound to show it is on
        screen.blit(image,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))
    def setState(self,components,wires):
        for wire in wires:
            if wire.ID==self.inputs[0][0]:
                self.state = wire.state










class Display(Component):
    def __init__(self):
        Component.__init__(self)
        self.outputs=[]#x and y multipliers of where wire will connect
        self.inputs=[["free",0.2,1],["free",0.4,1],["free",0.6,1],["free",0.8,1]]#free?, x multiplyer, y multiplyer

    def draw(self):
        if self.state==0:##Drawing correct number, this could be simplified with exec()
            image=pygame.transform.scale(display0,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==1:
            image=pygame.transform.scale(display1,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==2:
            image=pygame.transform.scale(display2,(int(40*zoomLevel),int(40*zoomLevel)))  
        elif self.state==3:
            image=pygame.transform.scale(display3,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==4:
            image=pygame.transform.scale(display4,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==5:
            image=pygame.transform.scale(display5,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==6:
            image=pygame.transform.scale(display6,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==7:
            image=pygame.transform.scale(display7,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==8:
            image=pygame.transform.scale(display8,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==9:
            image=pygame.transform.scale(display9,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==10:
            image=pygame.transform.scale(display0,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==11:
            image=pygame.transform.scale(display1,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==12:
            image=pygame.transform.scale(display2,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==13:
            image=pygame.transform.scale(display3,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==14:
            image=pygame.transform.scale(display4,(int(40*zoomLevel),int(40*zoomLevel)))
        elif self.state==15:
            image=pygame.transform.scale(display5,(int(40*zoomLevel),int(40*zoomLevel)))

        screen.blit(image,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))
        
    def setState(self,components,wires):
        self.state=0
        for wire in wires:
            if wire.ID==self.inputs[0][0] and wire.state==True:
                self.state+=8
            elif wire.ID==self.inputs[1][0] and wire.state==True:
                self.state+=4
            elif wire.ID==self.inputs[2][0] and wire.state==True:
                self.state+=2
            elif wire.ID==self.inputs[3][0] and wire.state==True:
                self.state+=1

class Switch(Component):
    def __init__(self):
        Component.__init__(self)
        self.outputs=[[[],0.5,0,False]]#x and y multipliers of where wire will connect
        self.inputs=[]#free?, x multiplyer, y multiplyer

    def draw(self):
        if self.outputs[0][3] == False:
            image=pygame.transform.scale(switchOffImage,(int(40*zoomLevel),int(40*zoomLevel)))
        else:
            image=pygame.transform.scale(switchOnImage,(int(40*zoomLevel),int(40*zoomLevel)))
            
        screen.blit(image,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))
    def setState(self,components,wires):
        if collide(mousex,mousey,(self.x-camerax)*zoomLevel,(self.y-cameray+5)*zoomLevel,40*zoomLevel,40*zoomLevel) and leftMouseClicked == True and selectedTool=="Mouse":
            self.outputs[0][3] = not self.outputs[0][3]#If button is clicked, the output will change state

class Button(Component):
    def __init__(self):
        Component.__init__(self)
        self.outputs=[[[],0.5,0,False]]#x and y multipliers of where wire will connect
        self.inputs=[]#free?, x multiplyer, y multiplyer
        self.counter=0

    def draw(self):
        if self.outputs[0][3] == False:
            image=pygame.transform.scale(buttonOffImage,(int(40*zoomLevel),int(40*zoomLevel)))
        else:
            image=pygame.transform.scale(buttonOnImage,(int(40*zoomLevel),int(40*zoomLevel)))
            
        screen.blit(image,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))
    def setState(self,components,wires):
        if collide(mousex,mousey,(self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel,40*zoomLevel,40*zoomLevel) and leftMouseClicked == True and selectedTool=="Mouse":
            self.counter=0#Starts the button being positive
            self.outputs[0][3] = True

        elif self.counter>=60:
            self.outputs[0][3] = False
            
        elif self.counter<60:
            self.counter+=speed


class Clock(Component):
    def __init__(self):
        Component.__init__(self)
        self.outputs=[[[],0.5,0,False]]#x and y multipliers of where wire will connect
        self.inputs=[]#free?, x multiplyer, y multiplyer
        self.counter=0

    def draw(self):
        image=pygame.transform.scale(pulseImage,(int(40*zoomLevel),int(40*zoomLevel)))    
        screen.blit(image,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))
    def setState(self,components,wires):
        self.counter+=speed#Adds program speed to the counter
        if self.counter>=120:
            self.counter=0#If larger then resets timer for next oscillation
            self.outputs[0][3] = False
        elif self.counter>=60:
            self.outputs[0][3] = True
        else:
            self.outputs[0][3] = False


class InputBox():##Text can be entered, it will change a wanted vairable
    def __init__(self,variable):
        self.value=variable
        self.entering=False
    def draw(self,x,y,width,variable):
        #self.value=variable
        pygame.draw.rect(screen,(255,255,255),(x,y,width,16),0)#Draws box
        pygame.draw.rect(screen,(0,0,0),(x,y,width,16),1)
        if collide(mousex,mousey,x,y,width,16):
            pygame.draw.rect(screen,(150,150,150),(x,y,width,16),1)

            
            if leftMouseClicked==True:
                self.entering= not self.entering
                
        elif self.entering==True:##If already selected it will show border
            pygame.draw.rect(screen,(150,150,150),(x,y,width,16),1)

        if self.value=="":
            text=font1.render(str("Name"),True,(200,200,200))
            screen.blit(text,(x,y-2))
        else:
            text=font1.render(str(self.value),True,(0,0,0))
            screen.blit(text,(x,y-2))
        return self.value ##Gives value of text box back




class SideMenu():#Shows info about objects when they are right clicked
    def __init__(self,ID):
        self.width=150
        self.x=-self.width
        self.height=200
        self.objectID=ID
    def draw(self):
        pygame.draw.rect(screen,(100,100,100),(self.x,screen.get_height()/2-self.height/2,self.width,self.height),0)#Drawing actual box
        pygame.draw.rect(screen,(0,0,0),(self.x,screen.get_height()/2-self.height/2,self.width,self.height),2)#Border
        pygame.draw.rect(screen,(0,0,0),(self.x,screen.get_height()/2-self.height/2,self.width,20),0)
        for i in componentList:
            if i.ID==self.objectID:
                if i.item=="7-Segment Display":
                    barText=font1.render(str("Display"),True,(255,255,255))##Gets the type of item
                    screen.blit(barText,(self.x+10,screen.get_height()/2-self.height/2))
                else:  
                    barText=font1.render(str(i.item),True,(255,255,255))##Gets the type of item
                    screen.blit(barText,(self.x+10,screen.get_height()/2-self.height/2))

                nameText=font1.render("Name:",True,(255,255,255))##Gets the type of item
                screen.blit(nameText,(self.x+10,screen.get_height()/2-self.height/2+20))                
                i.name=SideMenuInputBox.draw(self.x+10,screen.get_height()/2-self.height/2+40,100,i.name)#Shows items input box

                #Objects ID's
                objIDText=font1.render("Object's ID: "+str(i.ID),True,(255,255,255))##Gets the type of item
                screen.blit(objIDText,(self.x+10,screen.get_height()/2-self.height/2+60))   

                #Objects Outputs
                objOutsText=font1.render("Outputs: ",True,(255,255,255))##Gets the type of item
                screen.blit(objOutsText,(self.x+10,screen.get_height()/2-self.height/2+85))

                text=""
                for out in i.outputs:
                    if out[3]==True:
                        text=text+"1"
                    else:
                        text=text+"0"
                objOutsText=font1.render(str(text),True,(255,255,255))##Gets the type of item
                screen.blit(objOutsText,(self.x+10,screen.get_height()/2-self.height/2+105)) 




                
        if self.x<0:
            self.x+=30#Moves box, so has animation into screen


class Guide():
    def __init__(self,name,contentList,imageList):
        self.name=name#Name of guide
        self.contentList=contentList#List of text, each item per page
        self.imageList=imageList#List of images, each image per page- size of 250 x 200 maximum


########################################List of the guide classes
guideList=[Guide("Basics",["""This software is designed to simulate computer hardware. It does not deal with physical properties of a computer and does not use voltage or currents. Instead it focuses on the actual computer logic and the structure of computer systems.""",
"""There are several menus which each contain computer components. This guide will explain the Gates, Inputs and Outputs. Firstly as each component may have outputs at the top and inputs at the bottom, the inputs into a component will be processed into an output that can be connected to another component."""
,"""The SWITCH will change state when clicked by the mouse. This will change it's output between 1 and 0.  """
,"""The LED has 1 input. If the input is 1, the LED will light up, else it will stay off. These are used to indicate the state of a circuit and show outputs of circuits."""
,"""Logic Gates check the inputs, if the inputs meet certian requiremnts then they will output true."""
,"""The AND GATE - If and only if both outputs are 1 it will output 1"""
,"""The OR GATE - If at leats one input is 1, then it will output 1"""
,"""The NOT GATE - Reverses the input, so if input is 1 then output is 0"""
,"""The NAND GATE - If both inputs are not 1 it will output 1"""
,"""The NOR GATE - If either input is 1 it will output 0"""
,"""The XOR GATE - (exclusive or) will output 1 if exactly one input is 1"""
,"""The BUFFER GATE - The output is equal to the input"""
,"""To connect an output to an input simply click a connection and then click another of a different type. A wire will be created between the 2 items, this will turn green when the wire's input is 1."""
                           ],[andGateImage,None,switchOnImage,lightOnImage,None,andGateImage,orGateImage,notGateImage,nandGateImage,norGateImage,xorGateImage,bufferGateImage,None]),
           Guide("Adder",["""An adder is used within a computer to add 2 binary numbers together. This guide will show you how to create an 8-bit adder with a 9-bit output. Firstly consider binary addition. 1+1=0 with a carry bit of 1. 0+1=1"""
                          ,"""To create the circuit for this place 2 switches which each represent a binary value within a larger number"""
                          ,"""Then place 2 LED's which will act as the Sum and Carry bits of the addition. Right click each switch and LED and name them appropriately"""
                          ,"""If both switches are 1 then the carry will be 1. So the carry is 1 when switch 1 AND switch 2 are on."""
                          ,"""The sum is 1 if only on switch is on. An XOR can be used to simulate this. Connect the XOR gate and the AND gate to the inputs and outputs correctly"""
                          ,"""What you have created is a half adder. For the full circuit we will also need full adders which also accept a carry bit from the previous adder. So go to the integrated page and save this as an integrated circuit, then click new."""
                          ,"""For the full adder place 3 switches A,B and carry. Also place 2 LED's for the Sum and Carry bits, also label these appropriately."""
                          ,"""We again connect an XOR gate with inputs A & B and an AND gate with inputs A & B. Yet these are not the sum and carry bits as we must factor in the carry from the previous addition"""
                          ,"""The sum is 1 if only A XOR B is 1 or if only C is 1. So use an XOR to connect these to the Sum output"""
                          ,"""The carry is 1 if A AND B is 1 or (C AND (A XOR B)) is 1, so use an OR gate to connect these"""
                          ,"""Once this has been created also save it as an integrated circuit and click new page"""
                          ,"""Now to build the 8-bit adder using these integrated circuits. Start by placing 2 rows of 8 switches and 1 row of 9 LED's to use as inputs and outputs to our adder circuit."""
                          ,"""The first 2 switches (1st from each row) can be connected using the half adder, all the others can be connected with full adders, using the carry from the previous integrated circuit as an input."""
                          ,"""Connect each sum output to the correct LED in the row and the circuit will be complete. Note that you can keep adding as many adders as you desire and this will still work."""]
                           ,[complexGateImage,switchOnImage,lightOnImage,andGateImage,xorGateImage,complexGateImage,None,None,xorGateImage,None,complexGateImage,None,None,lightOnImage])]                    

class GuideMenu():#Shows info about objects when they are right clicked
    def __init__(self,name):
        self.width=300
        self.x=screen.get_width()
        self.height=400
        self.pageNumber=0#Step of the guide
        self.name=name
        for i in guideList:
            if name == i.name:
                self.contentList=i.contentList
                self.imageList=i.imageList
    def draw(self):
        if self.x>screen.get_width()-self.width:
            self.x-=30#Moves box, so has animation into screen
        else:
            self.x=screen.get_width()-300
        pygame.draw.rect(screen,(100,100,100),(self.x,screen.get_height()/2-self.height/2,self.width,self.height),0)#Drawing actual box
        pygame.draw.rect(screen,(0,0,0),(self.x,screen.get_height()/2-self.height/2,self.width,self.height),2)#Border
        pygame.draw.rect(screen,(0,0,0),(self.x,screen.get_height()/2-self.height/2,self.width,20),0)


            
        barText=font1.render(str(self.name)+"  "+str(self.pageNumber+1)+"/"+str(len(self.contentList)),True,(255,255,255))##Shows guide name
        screen.blit(barText,(self.x+10,screen.get_height()/2-self.height/2))

        ##Displaying the guides content
        count=0
        texty=30
        text=self.contentList[self.pageNumber]
        for char in self.contentList[self.pageNumber]:#Makes text spread across several lines of length 20 characters
            if count>20 and char==" ":
                guideText=font1.render(text[:count],True,(0,0,0))
                screen.blit(guideText,(self.x+10,screen.get_height()/2-self.height/2+texty))
                text=text[count:]
                texty+=20
                count=0
            count+=1
        guideText=font1.render(text[:count],True,(0,0,0))
        screen.blit(guideText,(self.x+10,screen.get_height()/2-self.height/2+texty))##Shows last line

        if self.imageList[self.pageNumber]!=None:
            screen.blit(self.imageList[self.pageNumber],(self.x+150-self.imageList[self.pageNumber].get_width(),screen.get_height()/2+50))#Max size of image is about 200x100

        ##Next and previous buttons
        if self.pageNumber<len(self.contentList)-1:
            pygame.draw.rect(screen,(200,200,200),(self.x+20,screen.get_height()/2+self.height*0.4,60,30),0)
            pygame.draw.rect(screen,(0,0,0),(self.x+20,screen.get_height()/2+self.height*0.4,60,30),2)
            nextText=font1.render("Next",True,(0,0,0))
            screen.blit(nextText,(self.x+30,screen.get_height()/2+self.height*0.4+5))
            if collide(mousex,mousey,self.x+20,screen.get_height()/2+self.height*0.4,60,30):
                pygame.draw.rect(screen,(100,100,100),(self.x+20,screen.get_height()/2+self.height*0.4,60,30),2)#Hover box
                if leftMouseClicked==True:
                    self.pageNumber+=1##Next page

        elif self.pageNumber==len(self.contentList)-1:
            pygame.draw.rect(screen,(200,200,200),(self.x+20,screen.get_height()/2+self.height*0.4,70,30),0)
            pygame.draw.rect(screen,(0,0,0),(self.x+20,screen.get_height()/2+self.height*0.4,70,30),2)
            nextText=font1.render("Finish",True,(0,0,0))
            screen.blit(nextText,(self.x+30,screen.get_height()/2+self.height*0.4+5))
            if collide(mousex,mousey,self.x+20,screen.get_height()/2+self.height*0.4,70,30):
                pygame.draw.rect(screen,(100,100,100),(self.x+20,screen.get_height()/2+self.height*0.4,70,30),2)#Hover box
                if leftMouseClicked==True:
                    windowList.remove(self)               


        if self.pageNumber>0:
            pygame.draw.rect(screen,(200,200,200),(self.x+100,screen.get_height()/2+self.height*0.4,90,30),0)
            pygame.draw.rect(screen,(0,0,0),(self.x+100,screen.get_height()/2+self.height*0.4,90,30),2)
            nextText=font1.render("Previous",True,(0,0,0))
            screen.blit(nextText,(self.x+110,screen.get_height()/2+self.height*0.4+5))
            if collide(mousex,mousey,self.x+100,screen.get_height()/2+self.height*0.4,90,30):
                pygame.draw.rect(screen,(100,100,100),(self.x+100,screen.get_height()/2+self.height*0.4,90,30),2)#Hover Box
                if leftMouseClicked==True:
                    self.pageNumber-=1#Previous Page
        

class Slider():
    def __init__(self,value,minimum,maximum,colour):
        self.value=value
        self.min=minimum
        self.max=maximum
        self.colour=colour
    def draw(self,x,y,width,height):
        pygame.draw.rect(screen,self.colour,(x,y,width,height),0)#Draws shape of slider
        pygame.draw.rect(screen,(0,0,0),(x,y,width,height),2)

        pygame.draw.circle(screen,(0,0,0),(int(x+width*((self.value-self.min)/(self.max-self.min))),int(y+height/2)),int(height/2))#Draws ball in correct location on the slider

        ##Setting a hold to the value of the variable
        if collide(mousex,mousey,x,y,width,height):
            if leftMouseDown==True:
                self.value=self.min+(mousex-x)*(self.max-self.min)/width
            infoText=smallFont.render(str("%.1f"%self.value),True,commentColour)
            screen.blit(infoText,(mousex-30,mousey+10))
        return self.value


class Comment():
    def __init__(self,text,x,y):
        self.text=text
        self.x=x
        self.y=y
    def draw(self):
        text=font1.render(self.text,True,commentColour)#Renders a saved comment to screen
        screen.blit(text,((self.x-camerax)*zoomLevel,(self.y-cameray)*zoomLevel))


class SaveIntegratedClass():
    def __init__(self):
        self.list = integratedList#i will copy this list into the class used for saving
    def setVariables(self):
        global integratedList,menuObjects
        integratedList = self.list
        for i in integratedList:
            menuObjects[3].items.append(MenuItem(i.name,complexGateImage))


class SaveProjectClass():
    def __init__(self):
        self.componentList = componentList
        self.wireList = wireList
        self.commentList = commentList
        self.currentID = currentID
    def setVariables(self):
        global componentList, wireList, commentList, currentID
        componentList = self.componentList
        wireList = self.wireList
        commentList = self.commentList
        currentID = self.currentID


def roundDown(num,divisor):
    return num-(num%divisor)

def collide(checkx,checky,x,y,w,h):#Funtion to check collisions on a rectangle
    if checkx>x and checkx<x+w and checky>y and checky<y+h:
        return True
    else:
        return False

def setCaption():
    caption='Computer Logic System'
    for i in range(round(screen.get_width()/10)):
        caption+=" "
    caption+=currentFile
    pygame.display.set_caption(caption)

def drawDragBox():
    if leftMouseDown==True and mousex>50 and selectedTool=="Mouse":
        pygame.draw.rect(screen,commentColour,(mouseDownx,mouseDowny,mousex-mouseDownx,mousey-mouseDowny),2)

def drawIntegratedMenu():
    global integratedName
    integratedName=IntegratedInputBox.draw(105,22,100,integratedName)

IntegratedInputBox=InputBox(integratedName)
SideMenuInputBox=InputBox("")


def drawOptionsMenu():
    global gridToggle,fullscreenToggle,screen,developerToggle,wireThickness

    global backgroundColour,gridColour,wireOffColour,wireOnColour,commentColour
    
    pygame.draw.rect(screen,(100,100,100),(0,20,screen.get_width(),50),0)#Larger Rectangle
    #Checkbox Options
    showGridCheckBox = CheckBox(gridToggle)
    gridToggle = showGridCheckBox.drawCheckBox(5,24)
    gridText = font1.render("Show Grid",True,(0,0,0))
    screen.blit(gridText,(30,25))
    
    fullscreenCheckBox = CheckBox(fullscreenToggle)
    fullscreenBox = fullscreenCheckBox.drawCheckBox(5,46)
    if fullscreenBox!=fullscreenToggle:#Checks if the fullscreen option has been changed, so action can be taken
        fullscreenToggle=not fullscreenToggle
        if fullscreenToggle==True:
            screen = pygame.display.set_mode((1600,900),FULLSCREEN)
        else:
            screen = pygame.display.set_mode((1600,900),RESIZABLE)
            setCaption()   #Restore shape of caption, with filename in the middle
    fullscreenText = font1.render("Fullscreen",True,(0,0,0))
    screen.blit(fullscreenText,(30,47))


    developerCheckBox = CheckBox(developerToggle)
    developerToggle = developerCheckBox.drawCheckBox(screen.get_width()-35,44)
    developerText = font1.render("Developer Info",True,(0,0,0))
    screen.blit(developerText,(screen.get_width()-135,25))

    ###############SLIDERS

    ##Wire thickness
    wireText=font1.render("Wire Width",True,(0,0,0))
    screen.blit(wireText,(130,30))
    wireThicknessSlider=Slider(wireThickness,1,10,(255,255,255))
    wireThickness=wireThicknessSlider.draw(130,50,100,10)

    ##volume
    volumeText=font1.render("Volume",True,(0,0,0))
    screen.blit(volumeText,(260,30))
    volumeSlider=Slider(beep.get_volume(),0,0.5,(255,255,255))
    beep.set_volume(volumeSlider.draw(245,50,100,10))


    ###############RGB Colour Settings
    text=font1.render("Background",True,(0,0,0))
    screen.blit(text,(350,30))
    r,g,b=Slider(backgroundColour[0],0,255,(255,0,0)),Slider(backgroundColour[1],0,255,(0,255,0)),Slider(backgroundColour[2],0,255,(0,0,255))
    backgroundColour = (r.draw(360,50,20,8),g.draw(390,50,20,8),b.draw(420,50,20,8))

    text=font1.render("Grid",True,(0,0,0))
    screen.blit(text,(480,30))
    r,g,b=Slider(gridColour[0],0,255,(255,0,0)),Slider(gridColour[1],0,255,(0,255,0)),Slider(gridColour[2],0,255,(0,0,255))
    gridColour = (r.draw(460,50,20,8),g.draw(490,50,20,8),b.draw(520,50,20,8))

    text=font1.render("Wire Off",True,(0,0,0))
    screen.blit(text,(565,30))
    r,g,b=Slider(wireOffColour[0],0,255,(255,0,0)),Slider(wireOffColour[1],0,255,(0,255,0)),Slider(wireOffColour[2],0,255,(0,0,255))
    wireOffColour = (r.draw(560,50,20,8),g.draw(590,50,20,8),b.draw(620,50,20,8))

    text=font1.render("Wire On",True,(0,0,0))
    screen.blit(text,(665,30))
    r,g,b=Slider(wireOnColour[0],0,255,(255,0,0)),Slider(wireOnColour[1],0,255,(0,255,0)),Slider(wireOnColour[2],0,255,(0,0,255))
    wireOnColour = (r.draw(660,50,20,8),g.draw(690,50,20,8),b.draw(720,50,20,8))

    text=font1.render("Comments",True,(0,0,0))
    screen.blit(text,(755,30))
    r,g,b=Slider(commentColour[0],0,255,(255,0,0)),Slider(commentColour[1],0,255,(0,255,0)),Slider(commentColour[2],0,255,(0,0,255))
    commentColour = (r.draw(760,50,20,8),g.draw(790,50,20,8),b.draw(820,50,20,8))

def drawMenu():
    #Top Bar
    pygame.draw.rect(screen,(0,0,0),(0,0,screen.get_width(),20),0)
    pygame.draw.rect(screen,(100,100,100),(0,20,screen.get_width(),20),0)
    menuTitleX=0
    for menu in menuObjects:
        menu.drawMenuSelect(menuTitleX)
        menu.drawMenusItems()
        menuTitleX+=menu.text.get_width()+20

    menuButtonX=screen.get_width()-160
    for menuButton in menuButtonObjects:
        menuButton.drawMenuButton(menuButtonX)
        menuButtonX+=20

    #Bottom bar
    pygame.draw.rect(screen,(100,100,100),(0,screen.get_height()-20,screen.get_width(),20),0)
    
    mouseInfoText=font1.render("x:"+str(round(mousex))+" y:"+str(round(mousey)),True,(255,255,255))
    screen.blit(mouseInfoText,(screen.get_width()-mouseInfoText.get_width(),screen.get_height()-19))
    
    ##PlaceHolder For lots of info
    zoomInfoText=font1.render("Zoom Level: "+str(round(int(100*zoomLevel),1))+"%",True,(255,255,255))
    screen.blit(zoomInfoText,(screen.get_width()-zoomInfoText.get_width()*2,screen.get_height()-19))

    cameraInfoText=font1.render("Camera Position: "+str(round(camerax))+","+str(round(cameray)),True,(255,255,255))
    screen.blit(cameraInfoText,(10,screen.get_height()-19))


def drawDeveloperInfo():
    if developerToggle == True:
        devList=[["Selected Item: ",selectedItem],
                 ["Selected Tool: ",selectedTool],
                 ["Selected Menu: ",selectedMenu],
                 ["Current ID: ",currentID],
                 ["Left Mouse Down: ",leftMouseDown],
                 ["Right Mouse Down: ",rightMouseDown],
                 ["Wire Thickness: ",wireThickness],
                 ["Framerate: ",round(fpsClock.get_fps(),1)]]
        count=2
        for i in devList:
            devInfoText=font1.render(i[0]+str(i[1]),True,commentColour)
            screen.blit(devInfoText,(10,screen.get_height()-count*20))
            count+=1    

def drawGrid():##Means zoom tool is not really required
    if zoomLevel>0.3 and gridToggle==True:#Only shows grid at an appropriate zoom level, otherwise looks bad and runs poorly
        for i in range(round((screen.get_width()+20)/(gridSize*zoomLevel))):
            pygame.draw.line(screen,gridColour,(i*(gridSize*zoomLevel),0),(i*(gridSize*zoomLevel),screen.get_height()),1)
        for i in range(round(screen.get_height()/(gridSize*zoomLevel))):
            pygame.draw.line(screen,gridColour,(0,i*(gridSize*zoomLevel)),(screen.get_width(),i*(gridSize*zoomLevel)),1)

def moveCamera():
    global camerax,cameray
    if (leftMouseDown==True and selectedTool=="Move") or rightMouseDown==True:
        camerax=mouseDownCamerax-roundDown((mousex-mouseDownx)*(1/zoomLevel),gridSize*zoomLevel)
        cameray=mouseDownCameray-roundDown((mousey-mouseDowny)*(1/zoomLevel),gridSize*zoomLevel)##Fix the dodgy CAMERA, snap to grid

def drawComponents():
    global stopWire,wireStartID,wireStartType,wireStartSlot
    if leftMouseClicked == True and wireStartID!=0:#Will run if clicked not on object, as if clicked on object it will return from this funtion before this code segment
        stopWire=True
    
    for i in componentList:
        i.draw()
        i.setState(componentList,wireList)#Gives it the lists it will use to set its state
    if selectedTool=="Mouse":
        for i in componentList:
            i.collision()
    elif selectedTool=="Delete":
        for i in componentList:
            i.checkDelete()

    if stopWire==True:
        for i in componentList:
            if i.ID == wireStartID:
                if wireStartType == "Output":
                    i.outputs[wireStartSlot][0].remove(currentID)#If an output
                elif wireStartType == "Input":
                    i.inputs[wireStartSlot][0]="free"#If an input
                wireStartID = 0
                wireStartType = ""
                wireStartSlot = 0#Reset relevant variables and return
                return          

def drawWires():
    for i in wireList:
        i.draw()
        i.setState(componentList,wireList)


def drawWindows():
    for i in windowList:
        i.draw()


def mouseOverComponent():
    for i in componentList:
        if collide(mousex,mousey,(i.x-camerax)*zoomLevel,(i.y-cameray)*zoomLevel,i.width*zoomLevel,40*zoomLevel):
            return True
    return False       

def placeComponents():
    global currentID,integratedList,menuObjects
    if selectedItem!="" and mousey>80:
        if selectedItem=="and":##Each one draws component being placed, and can place it when clicked
            image=pygame.transform.scale(andGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
            screen.blit(image,(roundDown(mousex-(gridSize/2)*zoomLevel,gridSize*zoomLevel),roundDown(mousey-(gridSize/2)*zoomLevel,gridSize*zoomLevel)))
            if leftMouseClicked and mouseOverComponent()==False:
                componentList.append(AndGate())
                currentID+=1
        elif selectedItem=="or" and mouseOverComponent()==False:
            image=pygame.transform.scale(orGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
            screen.blit(image,(roundDown(mousex-(gridSize/2)*zoomLevel,gridSize*zoomLevel),roundDown(mousey-(gridSize/2)*zoomLevel,gridSize*zoomLevel)))
            if leftMouseClicked:
                componentList.append(OrGate())
                currentID+=1
        elif selectedItem=="xor" and mouseOverComponent()==False:
            image=pygame.transform.scale(xorGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
            screen.blit(image,(roundDown(mousex-(gridSize/2)*zoomLevel,gridSize*zoomLevel),roundDown(mousey-(gridSize/2)*zoomLevel,gridSize*zoomLevel)))
            if leftMouseClicked:
                componentList.append(XorGate())
                currentID+=1
        elif selectedItem=="nor" and mouseOverComponent()==False:
            image=pygame.transform.scale(norGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
            screen.blit(image,(roundDown(mousex-(gridSize/2)*zoomLevel,gridSize*zoomLevel),roundDown(mousey-(gridSize/2)*zoomLevel,gridSize*zoomLevel)))
            if leftMouseClicked:
                componentList.append(NorGate())
                currentID+=1
        elif selectedItem=="not" and mouseOverComponent()==False:
            image=pygame.transform.scale(notGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
            screen.blit(image,(roundDown(mousex-(gridSize/2)*zoomLevel,gridSize*zoomLevel),roundDown(mousey-(gridSize/2)*zoomLevel,gridSize*zoomLevel)))
            if leftMouseClicked:
                componentList.append(NotGate())
                currentID+=1
        elif selectedItem=="nand" and mouseOverComponent()==False:
            image=pygame.transform.scale(nandGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
            screen.blit(image,(roundDown(mousex-(gridSize/2)*zoomLevel,gridSize*zoomLevel),roundDown(mousey-(gridSize/2)*zoomLevel,gridSize*zoomLevel)))
            if leftMouseClicked:
                componentList.append(NandGate())
                currentID+=1

        elif selectedItem=="buffer" and mouseOverComponent()==False:
            image=pygame.transform.scale(bufferGateImage,(int(40*zoomLevel),int(40*zoomLevel)))
            screen.blit(image,(roundDown(mousex-(gridSize/2)*zoomLevel,gridSize*zoomLevel),roundDown(mousey-(gridSize/2)*zoomLevel,gridSize*zoomLevel)))
            if leftMouseClicked:
                componentList.append(BufferGate())
                currentID+=1

        elif selectedItem=="Switch" and mouseOverComponent()==False:
            image=pygame.transform.scale(switchOffImage,(int(40*zoomLevel),int(40*zoomLevel)))
            screen.blit(image,(roundDown(mousex-(gridSize/2)*zoomLevel,gridSize*zoomLevel),roundDown(mousey-(gridSize/2)*zoomLevel,gridSize*zoomLevel)))
            if leftMouseClicked:
                componentList.append(Switch())
                currentID+=1

        elif selectedItem=="Button" and mouseOverComponent()==False:
            image=pygame.transform.scale(buttonOffImage,(int(40*zoomLevel),int(40*zoomLevel)))
            screen.blit(image,(roundDown(mousex-(gridSize/2)*zoomLevel,gridSize*zoomLevel),roundDown(mousey-(gridSize/2)*zoomLevel,gridSize*zoomLevel)))
            if leftMouseClicked:
                componentList.append(Button())
                currentID+=1

        elif selectedItem=="Clock" and mouseOverComponent()==False:
            image=pygame.transform.scale(pulseImage,(int(40*zoomLevel),int(40*zoomLevel)))
            screen.blit(image,(roundDown(mousex-(gridSize/2)*zoomLevel,gridSize*zoomLevel),roundDown(mousey-(gridSize/2)*zoomLevel,gridSize*zoomLevel)))
            if leftMouseClicked:
                componentList.append(Clock())
                currentID+=1

        elif selectedItem=="LED" and mouseOverComponent()==False:
            image=pygame.transform.scale(lightOffImage,(int(40*zoomLevel),int(40*zoomLevel)))
            screen.blit(image,(roundDown(mousex-(gridSize/2)*zoomLevel,gridSize*zoomLevel),roundDown(mousey-(gridSize/2)*zoomLevel,gridSize*zoomLevel)))
            if leftMouseClicked:
                componentList.append(LED())
                currentID+=1

        elif selectedItem=="Speaker" and mouseOverComponent()==False:
            image=pygame.transform.scale(speakerOffImage,(int(40*zoomLevel),int(40*zoomLevel)))
            screen.blit(image,(roundDown(mousex-(gridSize/2)*zoomLevel,gridSize*zoomLevel),roundDown(mousey-(gridSize/2)*zoomLevel,gridSize*zoomLevel)))
            if leftMouseClicked:
                componentList.append(Speaker())
                currentID+=1

        elif selectedItem=="7-Segment Display" and mouseOverComponent()==False:
            image=pygame.transform.scale(displayImage,(int(40*zoomLevel),int(40*zoomLevel)))
            screen.blit(image,(roundDown(mousex-(gridSize/2)*zoomLevel,gridSize*zoomLevel),roundDown(mousey-(gridSize/2)*zoomLevel,gridSize*zoomLevel)))
            if leftMouseClicked:
                componentList.append(Display())
                currentID+=1

        for i in integratedList:#Checking names of integrated circuits, in case one is being placed
            if i.name==selectedItem:
                pygame.draw.rect(screen,(255,255,255),(roundDown((mousex-(gridSize/2)*zoomLevel),gridSize*zoomLevel)+5*zoomLevel,roundDown((mousey-(gridSize/2)),gridSize*zoomLevel)+5*zoomLevel,i.width*zoomLevel,30*zoomLevel),0)
                pygame.draw.rect(screen,(0,0,0),(roundDown((mousex-(gridSize/2)*zoomLevel),gridSize*zoomLevel)+5*zoomLevel,roundDown((mousey-(gridSize/2)),gridSize*zoomLevel)+5*zoomLevel,i.width*zoomLevel,30*zoomLevel),int(2*zoomLevel))


                screen.blit(smallFont.render(i.name,True,(0,0,0)),(roundDown((mousex-(gridSize/2)*zoomLevel),gridSize*zoomLevel)+10*zoomLevel,roundDown((mousey-(gridSize/2)),gridSize*zoomLevel)+14*zoomLevel))

                if leftMouseClicked==True and mouseOverComponent()==False:
                    componentList.append(IntegratedGate(i.internalComponentList,i.internalWireList,i.name,i.outputIDs,i.inputIDs,i.outputs,i.inputs,i.width,i.outputNames,i.inputNames))
                    currentID+=1


def placeWires():
    if wireStartID!=0:
        for i in componentList:
            if i.ID==wireStartID:
                for inp in i.inputs:
                    if inp[0]==currentID:
                        pygame.draw.line(screen,wireOffColour,((i.x+i.width*inp[1]-camerax)*zoomLevel,(i.y+40*inp[2]-cameray)*zoomLevel),(mousex,mousey),int(zoomLevel*wireThickness))

                for out in i.outputs:
                    if currentID in out[0]:
                        pygame.draw.line(screen,wireOffColour,((i.x+i.width*out[1]-camerax)*zoomLevel,(i.y+40*out[2]-cameray)*zoomLevel),(mousex,mousey),int(zoomLevel*wireThickness))

def saveIntegrated():#Saves all circuits in a pickle file
    saveClass=SaveIntegratedClass()
    with open("Assets/integratedCircuits.p","wb") as file:
        pickle.dump(saveClass,file)
    
def loadIntegrated():#Retrieves list of circuits from pickle file
    with open("Assets/integratedCircuits.p","rb") as file:
        saveClass=pickle.load(file)
    saveClass.setVariables()

def drawLoad():
    global selectedTool,currentFile,savesList
    count=0
    for i in savesList:#Each is name of file
        pygame.draw.rect(screen,(100,100,100),(screen.get_width()-100,45+count*20,100,15))#Draw bar
        if collide(mousex,mousey,screen.get_width()-100,45+count*20,100,15):
            pygame.draw.rect(screen,(200,200,200),(screen.get_width()-100,45+count*20,100,15))
            
            if leftMouseClicked == True:#If clicked then saves it as the file name and sets caption etc
                saveClass = SaveProjectClass()
                with open("Saves/"+str(i)+".p","rb") as file:
                    saveClass=pickle.load(file)
                saveClass.setVariables()
                currentFile=i
                setCaption()
                selectedTool = "Mouse"
            elif rightMouseClicked == True:#If right clicked it DELETES the file
                os.remove("Saves/"+str(i)+".p")
                savesList.remove(i)
                
        text=smallFont.render(str(i),True,(255,255,255))#Show name of file
        screen.blit(text,(screen.get_width()-95,46+count*20))
        count+=1

SaveInputBox=InputBox(currentFile)

def processSave():
    global currentFile,selectedTool,saveList
    if currentFile=="New File":#This will be the case if not saved yet as it needs to be renamed to save
        pygame.draw.rect(screen,(100,100,100),(screen.get_width()/2-100,screen.get_height()/2-50,200,100),0)#Drawing box in middle of screen
        pygame.draw.rect(screen,(0,0,0),(screen.get_width()/2-100,screen.get_height()/2-50,200,100),2)

        pygame.draw.rect(screen,(0,0,0),(screen.get_width()/2-100,screen.get_height()/2-50,200,20),0)
        text=font1.render("Name Project",True,(255,255,255))
        screen.blit(text,(screen.get_width()/2-60,screen.get_height()/2-50))

        SaveInputBox.draw(screen.get_width()/2-80,screen.get_height()/2-10,160,currentFile)#Using class to show a text box

        #Set it when clicked
        pygame.draw.rect(screen,(200,200,200),(screen.get_width()/2-80,screen.get_height()/2+20,50,20),0)
        pygame.draw.rect(screen,(0,0,0),(screen.get_width()/2-80,screen.get_height()/2+20,50,20),2)
       
        nextText=font1.render("Save",True,(0,0,0))
        screen.blit(nextText,(screen.get_width()/2-76,screen.get_height()/2+20,50,20))

        if collide(mousex,mousey,screen.get_width()/2-80,screen.get_height()/2+20,50,20):
            pygame.draw.rect(screen,(100,100,100),(screen.get_width()/2-80,screen.get_height()/2+20,50,20),2)#Hover box
            if leftMouseClicked==True:
                currentFile = SaveInputBox.draw(screen.get_width()/2-80,screen.get_height()/2-10,160,currentFile)#Sets name of file, so that it can save
                setCaption()


        #Cancel button
        pygame.draw.rect(screen,(200,200,200),(screen.get_width()/2+20,screen.get_height()/2+20,60,20),0)
        pygame.draw.rect(screen,(0,0,0),(screen.get_width()/2+20,screen.get_height()/2+20,60,20),2)
       
        nextText=font1.render("Close",True,(0,0,0))
        screen.blit(nextText,(screen.get_width()/2+24,screen.get_height()/2+20,60,20))

        if collide(mousex,mousey,screen.get_width()/2+20,screen.get_height()/2+20,60,20):
            pygame.draw.rect(screen,(100,100,100),(screen.get_width()/2+20,screen.get_height()/2+20,60,20),2)#Hover box
            if leftMouseClicked==True:
                selectedTool="Mouse"
    else:
        saveClass=SaveProjectClass()##Uses the save project class to pickle the object into a storage file
        with open("Saves/"+str(currentFile)+".p","wb") as file:
            pickle.dump(saveClass,file)
        selectedTool="Mouse"
        if currentFile not in savesList:
            savesList.append(currentFile)

def drawComments():
    global commentx,commenty,comment
    if selectedTool!="Comment":
        commentx,commenty,comment=None,None,""

    if leftMouseClicked == True and mousey>80 and selectedTool == "Comment":#Starts typing new comment at mouse position
        commentx,commenty=mousex,mousey
        
    if commentx!=None:#If currently typing
        currentText = font1.render(comment,True,commentColour)
        screen.blit(currentText,(commentx,commenty))
        pygame.draw.line(screen,commentColour,(commentx+currentText.get_width()+2,commenty),(commentx+currentText.get_width()+2,commenty+20),2)
    for com in commentList:
        com.draw()

                                    
#Pre start processes
setCaption()
loadIntegrated()

while True:
    screen.fill(backgroundColour)#Set Background Colour
    info=pygame.display.Info()#Collects info about window size

    #Building Area
    drawGrid()
    drawWires()
    drawComponents()
    moveCamera()
    placeComponents()
    placeWires()
    drawComments()

    #Foreground/Menu
    drawDragBox()
    drawMenu()
    drawDeveloperInfo()
    drawWindows()

    ##Saving and Loading Menus and processing
    if selectedTool=="Load":
        drawLoad()
    elif selectedTool=="Save":
        processSave()

    #Reset MouseVariables
    leftMouseClicked=False
    rightMouseClicked=False

    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == VIDEORESIZE and fullscreenToggle==False:#Resizing window
            if event.w<minimumWindowWidth:
                event.w=minimumWindowWidth
            if event.h<minimumWindowHeight:
                event.h=minimumWindowHeight
            screen = pygame.display.set_mode((event.w,event.h),RESIZABLE)
            setCaption()
            
        elif event.type==MOUSEMOTION:
            mousex,mousey=event.pos
            
        elif event.type==MOUSEBUTTONUP:
            if event.button==1:
                leftMouseClicked=True
                leftMouseDown=False#Reset the mouse being held down
            elif event.button==3:
                rightMouseClicked=True
                rightMouseDown=False
                
        elif event.type==MOUSEBUTTONDOWN:
            if event.button==5:
                if zoomLevel>0.2:
                    zoomLevel-=zoomSpeed
            elif event.button==4:
                if zoomLevel<2:
                    zoomLevel+=zoomSpeed
            elif event.button==1:#Left mouse button gone down?
                leftMouseDown=True
                mouseDownx,mouseDowny=event.pos
                mouseDownCamerax,mouseDownCameray=camerax,cameray#Where camera was when mouse went down
            elif event.button==3:
                rightMouseDown=True
                mouseDownx,mouseDowny=event.pos
                mouseDownCamerax,mouseDownCameray=camerax,cameray#Where camera was when mouse went down
                
        elif event.type==KEYDOWN:
            if event.key == K_ESCAPE:
                selectedTool="Mouse"
                selectedItem=""
                windowList=[]
            if IntegratedInputBox.entering==True:##if typing in box then these letters will be entered
                if event.key==K_BACKSPACE:
                    IntegratedInputBox.value=IntegratedInputBox.value[:-1]
                else:
                    if len(str(integratedName))<10:
                        IntegratedInputBox.value=IntegratedInputBox.value+str(event.unicode)

            elif SideMenuInputBox.entering==True:
                if event.key==K_BACKSPACE:
                    SideMenuInputBox.value=SideMenuInputBox.value[:-1]
                else:
                    if len(str(SideMenuInputBox.value))<10:
                        SideMenuInputBox.value=SideMenuInputBox.value+str(event.unicode)
            elif SaveInputBox.entering==True:
                if event.key==K_BACKSPACE:
                    SaveInputBox.value=SaveInputBox.value[:-1]
                else:
                    if len(str(SaveInputBox.value))<20:
                        SaveInputBox.value=SaveInputBox.value+str(event.unicode)
            elif commentx!=None:
                if event.key==K_BACKSPACE:
                    comment=comment[:-1]
                elif event.key==K_RETURN:
                    commentList.append(Comment(comment,camerax+commentx/zoomLevel,cameray+commenty/zoomLevel))
                    commentx,commenty=None,None
                    comment=""
                else:
                    if len(str(comment))<50:
                        comment=comment+str(event.unicode)                
                
    pygame.display.update()
    fpsClock.tick(120)














#Finally tidy code and screenshot


##Stretch sliders to fill enter options menu
##Add hotkeys and hotkey file, with defaults
##Add more colours for LEDs?
##Change max input box to length of text image not length
##Add indicator to wether it has been saved
#Coloured or non coloured items 

    
    


    
    
