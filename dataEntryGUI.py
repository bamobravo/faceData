from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from dataEntry import EntryLogic
from PIL.ImageTk import PhotoImage as Photo
import time
import matplotlib.pyplot as plt
import sqlite3
import os
import cv2
import shutil

def resizeImage(image):
    basewidth = 400
    wpercent = (basewidth / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    img = image.resize((basewidth, hsize), Image.ANTIALIAS)
    return img


class DataEntryGUI(Frame):

    def __init__(self,entryLogic):
        Frame.__init__(self,None)
        self.logic = entryLogic
        self.images=[]
        self.dataHolder=[]
        self.index =0
        self.filename=''
        self.dbname='data/metafile.db'
        self.grid()
        self.buildUI()

    def loadVideo(self):
        if self.filename:
            self.images =self.logic.loadVideo(self.filename)
        else:
            messagebox.showinfo("File Selection error",
                                "no file selected")

    def loadFile(self):
        self.filename=filedialog.askopenfilename(parent=self,title='Load Video File')
        self.statusVariable.set("processing video..............please wait...........")
        time.sleep(1)
        if self.filename:
            if not (self.filename.endswith('.mp4') or self.filename.endswith(".avi")):
                messagebox.showinfo("Visualizer error", "Filetype must be a .mp4 or .avi")
            else:
                self.statusVariable.set("processing video..............please wait...........")
                self.loadVideo()
                self.index=-1
                self.showNext(True)

    def clearSelection(self,container):
        selected = container.curselection()
        for select in selected:
             container.selection_clear(select) 


    def necessaryItemSelected(self):
        selectedExpression = list(map(int, self.listOptions.curselection()))
        selectStages =  list(map(int, self.stageList.curselection()))
        if len(selectedExpression) >0 and len(selectStages)>0:
            if len(self.dataHolder) <self.index :
                self.dataHolder[self.index]=(selectedExpression,selectStages,self.images[self.index])
            else:
                self.dataHolder.append((selectedExpression,selectStages,self.images[self.index]))
            return True
        return False

    def showNext(self,start=False):
        if not self.images and self.index+1 >= len(self.images):
            return
        if not start and not self.necessaryItemSelected():
            return
            
        self.index=self.index+1
        currentFrame = self.images[self.index]
        image = resizeImage(Image.fromarray(currentFrame))
        self.img =Photo(image)
        self.imageContainer.config(image=self.img)
        self.imageContainer.image=self.img
        self.statusVariable.set(" showing image ("+str((self.index+1))+"/"+str(len(self.images))+")")
        self.clearSelection(self.listOptions)
        self.clearSelection(self.stageList)

    def loadSelected(self):
        '''set the selected state for the previous button'''
        if self.index <0 and len(self.dataHolder)==0:
            return
        selectedExpression,selectStages,image = self.dataHolder[self.index]
        self.listOptions.selection_set(selectedExpression)
        self.stageList.selection_set(selectStages)

    def showPrevious(self):
        if self.index-1 < 0:
            return
        self.index=self.index-1
        self.loadSelected()
        currentFrame = self.images[self.index]
        image = resizeImage(Image.fromarray(currentFrame))
        self.img =Photo(image)
        self.imageContainer.config(image=self.img)
        self.imageContainer.image=self.img
        self.statusVariable.set(" showing image ("+str((self.index+1))+"/"+str(len(self.images))+")")

    def saveData(self):
        '''will save all the data here just check for necessary conditions'''
        if os.path.exists(self.dbname):
            os.remove(self.dbname)
        if os.path.exists("data/images"):
            shutil.rmtree("data/images")

        os.mkdir("data/images")
        conn = sqlite3.connect(self.dbname)
        cursor =conn.cursor()
        #create the table for saving the data
        sql ="CREATE table image_data(expressions text, positions text,image_path text)"
        cursor.execute(sql)
        conn.commit()
        print("saving data into the database might take something time to complete")
        self.processMetadata(cursor)
        conn.commit()
        conn.close()
        print("data saved into database successfully")
        
    def processMetadata(self,cursor):
        query ="INSERT into image_data(expressions,positions,image_path) VALUES(?,?,?)"
        data =[ (",".join(self.convertExpression(expression)),",".join(self.convertStage(stage)),self.saveImage(image,index)) for index,(expression,stage,image) in enumerate(self.dataHolder)]
        cursor.executemany(query,data)
        print("data saved successfully")

    def convertExpression(self,values):
        return [self.listOptions.get(x) for x in values]

    def convertStage(self,values):
        return [self.stageList.get(x) for x in values]

    def saveImage(self,image,index):
        newIndex = index+1
        filename= "data/images/"+str(newIndex)+".jpg"
        cv2.imwrite(filename,image)
        return filename

    def buildUI(self):
        label_title = Label(self,
                            text="Face Expression Data Generation",
                            font=("Ariel", 16))
        label_title.grid(columnspan=2) #entered into first row
        listValues = StringVar()
        self.expressionOption = 'happy sad angry fear contempt pain frustration surprise anxiety disgrace'
        listValues.set(self.expressionOption)
        positionList = StringVar()
        self.stageOption = "onset apex offset"
        positionList.set(self.stageOption)
        self.statusVariable = StringVar()
        self.statusVariable.set("")
        self.statusText = Label(self,textvariable=self.statusVariable)
        self.statusText.grid(row=1)#this moves into the next line
        self.fileButton = Button(self,text='choose file',command=self.loadFile)
        self.fileButton.grid(row=1,column=1)
        self.picFrame = Frame(self,bd=2,relief=FLAT)
        self.picFrame.grid(row=2, column=0,rowspan=5)
        #text to display the status
        #load the image to be displayed
        self.img = PhotoImage(file='image.png')
        self.img.subsample(4,4)
        self.imageContainer = Label(self.picFrame,image=self.img)
        self.imageContainer.image=self.img
        self.imageContainer.grid()
        self.lFrame = LabelFrame(self,text='Facial Expression')
        self.lFrame.grid(row=2, column=1,rowspan=2)
        self.listOptions=Listbox(self.lFrame,exportselection=0,listvariable=listValues,selectmode=MULTIPLE)
        self.listOptions.grid()
        self.stageFrame = LabelFrame(self,text='AU Stage')
        self.stageFrame.grid(row=4,column=1)
        self.stageList = Listbox(self.stageFrame,exportselection=0,listvariable=positionList)
        self.stageList.grid()
        #show the next and previous button
        buttonFrame = Frame(self)
        buttonFrame.grid(row=5,column=1)
        self.previousButton = Button(buttonFrame, text='Previous',command=self.showPrevious)
        self.previousButton.grid(row=0,column=0)
        self.nextButton = Button(buttonFrame,text='Next',command=self.showNext)
        self.nextButton.grid(row=0,column=1)
        self.saveBtn = Button(self,text='Save Data', command=self.saveData)
        self.saveBtn.grid(row=6,column=1)

        #load the checkbox here

logic = EntryLogic()
print("starting application")
app = DataEntryGUI(logic)
app.master.title("Face Expression Loading Data")
app.mainloop()