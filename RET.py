# encoding=utf8
'''
Created on Jul 9, 2013
@author: james
'''

from Tkinter import *
import Tkinter, os, codecs
import time, re, tkMessageBox
from tkFileDialog import askopenfilename
import sys
reload(sys)
sys.setdefaultencoding('utf8')

if __name__ == '__main__': 
    # data containers
    root = Tk()
    root.title('Relation Annotation Tool V1.0 ')
    currentProtein = ''
    UniprotID = ''
    tagLists = {}
    tagIndex = 0
    cancel = False
    idPrefix = 'PROT'
    targetFilePath = ''
    
    # get order list
    def readOrder(path, orderList):
        for line in open(path):
            if line == '':
                continue
            line = line[:-1]
            splits = line.split('\t')
            orderList.append((u'task\\' + splits[0], int(splits[1])))
        return orderList
    
    # read tasks and orders
    def readOrders():
        try:
            orderList = []
            for path in os.listdir('orders'):
                orderList += (readOrder('orders/' + path, orderList))
            orderList = sorted(orderList, key=lambda tup:tup[1], reverse=True)
            return [tup[0] for tup in orderList]
        except:
            return
    
    
    # Open next file that need to be annnotated in 'task' folder
    def autoNext():
        global targetFilePath
        saveFile()
        clearData()
        txtFileSet = readAlltxtFilenames()
        taggedFileSet = readAlltaggedFilenames()
        flag = False
        for path in orderList:
            if path in txtFileSet and path not in taggedFileSet:
                targetFilePath = path
                root.title('Relation Annotation Tool ' + targetFilePath)
                readFile = open(path, 'r')
                allLines = ''.join(readFile.readlines())
                readFile.close()
                text.insert(1.0, allLines)
                flag = True
                break
        if not flag:
            tkMessageBox.showinfo("Congratulations!", "No task file in 'task' folder. To annotate a file, choose 'file->open'")
            
    def openBySelf():
        global targetFilePath
        selectedFile = askopenfilename(initialdir='task', filetypes=[("txt files", "*.txt")])
        print selectedFile
        if selectedFile == '':
            return
        else:
            saveFile()
            txtFileSet = readAlltxtFilenames()
            taggedFileSet = readAlltaggedFilenames()
            print 'aa'
            try:
                readFile = open(selectedFile, 'r')
                allLines = ''.join(readFile.readlines())
                readFile.close()
                targetFilePath = selectedFile
                clearData()
                text.insert(1.0, allLines)
                root.title('Relation Annotation Tool ' + targetFilePath)
            except:
                pass
            
    def readAlltxtFilenames(path=u'task'):
        try:
            txtFileSet = set()
            for f in os.listdir(path):
                filePath = os.path.join(path, f)
                if os.path.isdir(filePath):
                    txtFileSet = txtFileSet.union(readAlltxtFilenames(path=filePath))
                elif filePath.endswith('.txt'):
                    txtFileSet.add(filePath)
            return txtFileSet
        except:
            return

    def readAlltaggedFilenames(path=u'task'):
        try:
            taggedFileSet = set()
            for f in os.listdir(path):
                filePath = os.path.join(path, f)
                if os.path.isdir(filePath):
                    taggedFileSet = taggedFileSet.union(readAlltaggedFilenames(path=filePath))
                elif filePath.endswith('.tagged'):
                    taggedFileSet.add(filePath[:-1 * len('.tagged')])
            return taggedFileSet
        except:
            return
                
    # convert taglist into strings£¬for saving
    def taglistEncode():
        strTags = ''
        tags = []
        for tagName in text.tag_names():
            if tagName.startswith(idPrefix):
                tags.append('\t'.join(tagLists[tagName]))
        return '\n'.join(tags)
    
    # delete all tags of a text
    def clearTags(textWidget):
        for tagName in textWidget.tag_names():
            textWidget.tag_delete(tagName)
        
    # clear data
    def clearData():
        global currentProtein
        global UniprotID
        global tagLists
        global tagIndex
        global cancel
        entryP1.delete(0, END)
        entryP2.delete(0, END)
        entryKW.delete(0, END)
        text.delete(1.0, END)
        textEntities.delete(1.0, END)
        textrelation.delete(1.0, END)
        clearTags(text)
        clearTags(textEntities)
        clearTags(textrelation)
        currentProtein = ''
        UniprotID = ''
        tagLists = {}
        tagIndex = 0
        cancel = False
        idPrefix = 'PROT'
        
    def saveFile():
        saveFilePath = targetFilePath + '.tagged'
        saveFile1(saveFilePath)

    # save file
    def saveFile1(path):
        sourceText = text.get(1.0, END)
        sourceEntities = textEntities.get(1.0, END)

        relationl = []
        for line in textrelation.get(1.0, END).split('\n'):
            if line != '':
                relationl.append(line)
        trelations = '\n'.join(relationl)
        savefile = open(path, 'w')
        savefile.write('###Source text###\n')
        savefile.write(sourceText)
        savefile.write('\n\n###Entities###\n')
        savefile.write(sourceEntities)
        savefile.write('\n\n###Relations###\n')
        savefile.write(trelations)
        savefile.close()
    
    # form a relation
    def relationrecordEncode(p1, p2, keywords):
        return '<([' + p1 + '])> ' + keywords + ' <([' + p2 + '])>'
    
    # decode a relation record into a tuple
    def relationRecordDecode(str):
        splits = re.split('<([|])>', str)
        dc = {}
        dc['p1'] = len(splits) == 5 and splits[1] or ''
        dc['p2'] = len(splits) == 5 and splits[3] or ''
        dc['kw'] = len(splits) == 5 and splits[2] or ''
        return dc
        
    # right click selected text, to add the selected text into keyword text field
    def fillKeyWord(str):
        if entryKW.get() != '':
            entryKW.insert(END, ',')
        entryKW.insert(END, str)

    # center the window
    def center(win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() / 2) - (width / 2)
        y = (win.winfo_screenheight() / 2) - (height / 2)
        win.geometry('{0}x{1}+{2}+{3}'.format(width, height, x, y))
        
    # right click an entity record in textEntities text area£¬to put the entities into entity text field
    def fillEntityFromEntities(index):
        strindex = str(index)
        prefix = strindex[0:strindex.find('.') + 1]
        start = float(prefix + '0')
        line = textEntities.get(start, textEntities.index(prefix + 'end'))
        if entryP1.get() == '':
            entryP1.insert(END, line)
        elif entryP2.get() == '':
            entryP2.insert(END, line)
    
    # left click a highlighted entity, to put it into the entity text field
    def fillEntityFromText(event, tagName):
        line = '\t'.join(tagLists[tagName])
        if entryP1.get() == '':
            entryP1.insert(END, line)
        elif entryP2.get() == '':
            entryP2.insert(END, line)
    
    def updateTag(textId, tagName, buttonStr, func):
        textId.tag_delete(tagName)
        textId.tag_add(tagName, 1.0, textrelation.index('end'))
        textId.tag_bind(tagName, buttonStr, func)
    
    # insert relation
    def insertRelation():
        p1 = entryP1.get()
        p2 = entryP2.get()
        keywords = entryKW.get()
        if p1 != '' and p2 != '' and keywords != '':
            str = relationrecordEncode(p1, p2, keywords) + '\n' 
            textrelation.insert(END, str)
            updateTag(textrelation, 'tag_relation', '<Button-3>', lambda x: deleterelation(textrelation.index(CURRENT)))
            entryP1.delete(0, END)
            entryP2.delete(0, END)
    
    # delete a relation by right click        
    def deleterelation(index):
        strindex = str(index)
        prefix = strindex[0:strindex.find('.') + 1]
        start = float(prefix + '0')
        textrelation.delete(start, textrelation.index(prefix + 'end'))
        updateTag(textrelation, 'tag_relation', '<Button-3>', lambda x: deleterelation(textrelation.index(CURRENT)))
        
    def handlerAdaptor(fun, **kwds):
        return lambda event, fun = fun, kwds = kwds: fun(event, **kwds)  
    
    # add an entity
    def insertEntity(str):
        textEntities.insert(END, str)
        textEntities.tag_delete('tag_entities')
        textEntities.tag_add('tag_entities', 1.0, textEntities.index('end'))
        textEntities.tag_bind('tag_entities', '<Button-1>', lambda x: fillEntityFromEntities(textEntities.index(CURRENT)))
    
    def getEntity(UniprotID , currentProtein, first, last):
        return (UniprotID , currentProtein, first, last)
    
    def entityEncode(tup):
        return '\t'.join(tup)
    
    def entityDecoder(str):
        return str.split('\t')
    
    # annotate an entity
    def annoteEntity():
        global tagIndex
        global currentProtein
        global UniprotID
        global cancel
        currentProtein = text.selection_get()
        first = text.index('sel.first')
        last = text.index('sel.last')
        msg_box(currentProtein);
        if not cancel and UniprotID != '':   
            tagName = idPrefix + str(tagIndex)
            tagIndex += 1
            text.tag_add(tagName, first , last)
            text.tag_config(tagName, background='black', foreground='yellow')
            text.tag_bind(tagName, '<Button-3>', handlerAdaptor(cancelTag, tagName=tagName))
            text.tag_bind(tagName, '<Button-1>', handlerAdaptor(fillEntityFromText, tagName=tagName))
            
            tagLists[tagName] = getEntity(UniprotID , currentProtein, first, last);
            insertEntity(entityEncode(tagLists[tagName]) + '\n')
        UniprotID = ''
        currentProtein = ''
        cancel = False
        
        
    # delete highlighted entity
    def cancelTag(event, tagName):
        text.tag_delete(tagName)
        item = entityEncode(tagLists[tagName])
        if tagName in tagLists:
            del tagLists[tagName]
            updateEntities()
        if entryP1.get() == item:
            entryP1.delete(0, END)
        if entryP2.get() == item:
            entryP2.delete(0, END)
        
        i = 0
        for line in textrelation.get(1.0, END).split('\n'):
            i += 1
            if item in line:
                deleterelation(float(str(i) + '.0'))
                 
        
    # refresh entities
    def updateEntities():
        textEntities.delete(1.0, textEntities.index('end'))
        for i in range(0, tagIndex):
            tagName = idPrefix + str(i)
            if tagName in tagLists:
                textEntities.insert(textEntities.index('end'), '\t'.join(tagLists[tagName]) + '\n')
                
    # clear text widged
    def delete(textWidget, str):
        content = textWidget.get(1.0, END)
        i = 0
        for line in content.split('\n'):
            i += 1
            if str in line:
                textWidget.delete(float(str(i) + '.0'), textWidget.index(str(i) + '.end'))
    
    
    #
    def help_box():
        top = Toplevel(root)
        top.title('README.md')
        top.transient(root)
        top.grab_set()
        lf = LabelFrame(top, borderwidth=0)
        text = Text(lf)
        scroll = Scrollbar(lf, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side=LEFT)
        scroll.pack(side=RIGHT, fill=Y)
        lf.pack(side = TOP)
        lines = ''.join(file('readme.txt', 'r').readlines())
        text.insert(1.0, lines)
        cbutton = Button(top, text='confirm', command=top.destroy)
        cbutton.pack(side=BOTTOM)
        center(top)
        top.wait_window()
    
    
    def msg_box(proteinName, title='Annotate entity ID', msg='Annotate entity ID'):
        top = Toplevel(root)
        top.title(title)
        top.transient(root)
        top.grab_set()
        # label0 = Label(top, text=msg)
        # label0.pack()
        lfContent = LabelFrame(top, borderwidth=0)
        lfContent.pack(side=TOP)
        lfEntry = LabelFrame(lfContent, borderwidth=0)
        lfLabel = LabelFrame(lfContent, borderwidth=0)
        lfEntry.pack(side=RIGHT)
        lfLabel.pack(side=LEFT)
        Label(lfLabel, text='Entity name:  ').pack(side=TOP)
        Label(lfLabel, text='Entity ID  :').pack(side=BOTTOM)
        entryProt = Entry(lfEntry, width=40)
        entryProt.insert(0, proteinName)
        entryProt.pack(side=TOP)
        entryId = Entry(lfEntry, width=40)
        entryId.pack(side=BOTTOM)
        entryId.focus()
        lfButtons = LabelFrame(top, borderwidth=0)
        lfButtons.pack(side=BOTTOM)
        button2 = Button(lfButtons, text='confirm', command=lambda: submit_name(entryId, top))
        button2.pack(side=LEFT)
        button3 = Button(lfButtons, text='cancel',
                                command=lambda: cancelIDAnno(top))
        button3.pack(side=RIGHT)
        center(top)
        top.wait_window()

    def cancelIDAnno(top):
        global cancel
        top.destroy()
        cancel = True
        
    def submit_name(entry0, top):
        global UniprotID
        UniprotID = entry0.get()
        top.destroy()
        
    def empty(event):
        return 'break'
    

    # read file
    orderList = readOrders()
    txtFileSet = readAlltxtFilenames()
    taggedFileSet = readAlltaggedFilenames()
    
    # GUI drawing
    menubar = Menu(root)
    
    # Entity Frame
    labelframeNER = LabelFrame(root, text='Text')
    labelframeNER.pack(fill='both', expand='yes', side=LEFT)
    lfNER = LabelFrame(labelframeNER, borderwidth=0)
    lfNER.pack(side=BOTTOM)
    Button(labelframeNER, text='Annotate Entity', fg='blue', bd=2, width=28, command=annoteEntity).pack(side=BOTTOM)
    text = Text(lfNER, height=26, width=80)
    text.tag_bind('sel', '<Button-1>', lambda x: fillKeyWord(text.selection_get()))
    scroll = Scrollbar(lfNER, command=text.yview)
    text.configure(yscrollcommand=scroll.set)
    text.pack(side=LEFT)
    scroll.pack(side=LEFT, fill=Y)
    flag = False
    if orderList != None:
        for path in orderList:
            if path in txtFileSet and path not in taggedFileSet:
                targetFilePath = path
                root.title('Relation Annotation Tool ' + targetFilePath)
                readFile = open(path, 'r')
                allLines = ''.join(readFile.readlines())
                readFile.close()
                text.insert(1.0, allLines)
                flag = True
                break
    if not flag:
        tkMessageBox.showinfo("Congratulations!", "No task file in 'task' folder. To annotate a file, choose 'file->open'")
        
    text.bind('<Key>', empty)
    text.bind("<Control-s>", lambda x:saveFile())
   
    # Engity List Frame
    labelframeEntities = LabelFrame(root, text='Entities')
    labelframeEntities.pack(fill='both', expand='yes', side=LEFT)
    lfEntities = LabelFrame(labelframeEntities, borderwidth=0)
    lfEntities.pack(side=BOTTOM)
    textEntities = Text(lfEntities, height=26, width=40)
    textEntities.bind('<Key>', empty)
    textEntities.bind("<Control-s>", lambda x:saveFile())
    scrollEntities = Scrollbar(lfEntities, command=text.yview)
    textEntities.configure(yscrollcommand=scrollEntities.set)
    textEntities.pack(side=LEFT)
    scrollEntities.pack(side=LEFT, fill=Y)
    textEntities.tag_add('tag_entities', 1.0, textEntities.index('end'));
    textEntities.tag_bind('tag_entities', '<Button-1>', lambda x: fillEntityFromEntities(textEntities.index(CURRENT)))
    titleFrame = LabelFrame(labelframeEntities, border=0)
    label = Label(titleFrame, text='Entity ID\t\tEntity Name\tStart\tEnd')
    label.pack(side=BOTTOM)
    titleFrame.pack(side=BOTTOM)
    
    # Relation Frame
    labelframerelation = LabelFrame(root, text='Relations')
    labelframerelation.pack(fill='both', expand='yes', side=LEFT)
    labelframeP1 = LabelFrame(labelframerelation, borderwidth=0)
    entryP1 = Entry(labelframeP1)
    labelframeP2 = LabelFrame(labelframerelation, borderwidth=0)
    entryP2 = Entry(labelframeP2)
    labelframeKW = LabelFrame(labelframerelation, borderwidth=0)
    entryKW = Entry(labelframeKW)
    Label(labelframeP1, text='Entity 1                  :').pack(side=LEFT)
    Label(labelframeP2, text='Entity 2                  :').pack(side=LEFT)
    Label(labelframeKW, text='Relation Keyword:').pack(side=LEFT)
    entryP1.pack(side=LEFT)
    entryP2.pack(side=LEFT)
    entryKW.pack(side=LEFT)
    Button(labelframeP1, text='Clear', command=lambda: entryP1.delete(0, END)).pack(side=LEFT)
    Button(labelframeP2, text='Clear', command=lambda: entryP2.delete(0, END)).pack(side=LEFT)
    Button(labelframeKW, text='Clear', command=lambda: entryKW.delete(0, END)).pack(side=LEFT)
    labelframeP1.pack(side=TOP)
    labelframeP2.pack(side=TOP)
    labelframeKW.pack(side=TOP)
    Button(labelframerelation, text='Annotate a relation', fg='blue', bd=2, width=28, command=insertRelation).pack(side=TOP)
    lfrelation = LabelFrame(labelframerelation, borderwidth=0)
    lfrelation.pack(side=BOTTOM)
    textrelation = Text(lfrelation, height=26, width=70)
    scrollrelation = Scrollbar(lfrelation, command=text.yview)
    textrelation.tag_add('tag_relation', 1.0, textrelation.index('end'))
    textrelation.configure(yscrollcommand=scrollrelation.set)
    textrelation.pack(side=LEFT)
    scrollrelation.pack(side=LEFT, fill=Y)
    
    # Create Menus
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label='Next file', command=autoNext)
    filemenu.add_command(label='Open', command=openBySelf)
    filemenu.add_separator()
    filemenu.add_command(label='Save', command=saveFile, accelerator="Ctrl+S")
    filemenu.add_separator()
    filemenu.add_command(label='Quit', command=root.quit)
    menubar.add_cascade(label='File', menu=filemenu)
 
 
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label='How to', command=help_box)
    menubar.add_cascade(label='Help', menu=helpmenu)
    
    
    # display menu
    root.config(menu=menubar)
    root.bind_all("<Control-s>", lambda x:saveFile())
    # centerwindow
    center(root)
    mainloop()
