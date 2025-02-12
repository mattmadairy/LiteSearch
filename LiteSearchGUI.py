#import os
from tkinter import *
from tkinter import Label
from PIL import Image, ImageTk
import LiteSearchBackend as LSB
import ctypes

#Global Variables
db_name = "litesearch.db"
table_name = "LiteBookData"

#Sets the appid for the program. This is used to set the icon in the taskbar.
myappid = u'Madairy.LiteSearch.1.0.0' 
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

#Clears text entry boxes
def resetEntry():
    LSB.log_event('RESET','MAIN WINDOW RESET', 'SYS')
    e1.delete(0, END)
    e2.delete(0, END)
      
#Pulls search & notification logs
#UNFINISHED needs display & print funtionality
def logFiles():
    print('Log Files Requested')
    LSB.log_event('REQUEST','LOG FILES TAB REQUESTED', 'MLM91')
    top = Toplevel()
    top.geometry('425x200')
    top.title('Baltimore County Police Dispatch LiteSearch')
    top.iconbitmap('imagery\Traffic_Light.ico')
    menu = Menu(root)
    top.config(menu=menu)
    filemenu = Menu(menu)
    menu.add_cascade(label ='File', 
                     menu = filemenu)
    filemenu.add_command(label ='Print', 
                         command = print('print log window'))
    logLabel = Label(top, 
                     text = 'Log Files', font=('Arial', 12,'bold'))
    logLabel.pack()
    top.mainloop()

#Displays About documentation
def about():
    LSB.log_event('REQUEST','REQUEST ABOUT INFO', 'MLM91')
    top = Toplevel()
    top.geometry('425x200')
    top.title('Baltimore County Police Dispatch LiteSearch')
    top.iconbitmap('imagery\Traffic_Light.ico')
    aboutFile = open(r'about.txt', 'r')
    aboutContent = aboutFile.read()
    aboutLabel = Label(top, 
                       text = aboutContent, 
                       wraplength=375, 
                       justify='left')
    aboutFile.close()
    aboutLabel.pack()
    top.mainloop()

#Displays ULA/License
def license():
    LSB.log_event('REQUEST','REQUEST LICENSE INFO', 'MLM91')
    top = Toplevel()
    top.geometry('425x350')
    top.title('Baltimore County Police Dispatch LiteSearch')
    top.iconbitmap('imagery\Traffic_Light.ico')
    licenseFile = open(r'LICENSE', 'r')
    licenseContent = licenseFile.read()
    aboutLabel = Label(top, 
                       text = licenseContent, 
                       wraplength=375, 
                       justify='left')
    
    aboutLabel.pack()
    top.mainloop()

#Allows users to submit a problem or correction. 
#UNFINISHED - Writes to SQLite DB but needs email functionality to send support request to developer.
def support():
    def commandSet():
        commandArgs = LSB.support_request(nameEntry.get(), emailEntry.get(), textBox.get(1.0, END))
        top.destroy()
        return commandArgs
    def resetEntry():
        LSB.log_event('RESET','SUPPORT WINDOW RESET', 'SYS')
        nameEntry.delete(0, END)
        emailEntry.delete(0, END)
        textBox.delete(1.0, END)

    LSB.log_event('REQUEST','REQUEST SUPPORT WINDOW', 'MLM91')
    top = Toplevel()
    top.geometry('425x365')
    top.title('Baltimore County Police Dispatch LiteSearch')
    top.iconbitmap('imagery\Traffic_Light.ico')
    #masterLabel = Label()
    supportLabel = Label(top, text = '\nContact Support\n', 
                         font = ('Arial', 12, 'bold'))

    nameLabel = Label(top, text = 'Name:', font=('Arial',12,'bold'))  
    nameEntry = Entry(top, width = 50)

    emailLabel = Label(top, text = 'Email Address:', font=('Arial',12,'bold'))
    emailEntry = Entry(top, width = 50)
    
    textBoxLabel = Label(top, text = 'Reason:', font=('arial',12,'bold'))
    textBox = Text(top, height=6, width=50)

    submitButton = Button(top, text='Submit', width=25, command = commandSet)
    resetButton = Button(top, text = 'Reset', width=25, command = resetEntry)

    supportLabel.pack()
    nameLabel.pack(anchor='w', padx=10)
    nameEntry.pack(anchor='w', padx=10)
    emailLabel.pack(anchor='w', padx=10)
    emailEntry.pack(anchor='w', padx=10)
    textBoxLabel.pack(anchor='w', padx=10)
    textBox.pack()
    submitButton.pack(padx=2.5, pady=10)
    resetButton.pack(padx=2.5)
    top.mainloop()

#Display results window
def displayResults():

    def commandArgs():
        LSB.log_event('ACK','RECORD CREATED', 'MLM91')
        requestDateTime = str(requestDateEntry.get() + requestTimeEntry.get())
        notificationDateTime = str(notificationDateEntry.get() + notificationTimeEntry.get())
        unit = unitEntry.get()
        UserId = userEntry.get()
        LSB.notificationRecord(requestDateTime, unit, displayIntersection, shortAgency, notificationDateTime, UserId)
        top.destroy()
        successWindow()

    LSB.log_event('REQUEST','REQUEST DB SEARCH', 'MLM91')
    top = Toplevel()
    top.minsize(425, 300)
    top.title('Baltimore County Police Dispatch LiteSearch')
    top.iconbitmap('imagery\Traffic_Light.ico')
   
    #Labels
    entryLabel = Label(top, text = '\nENTRY:', font = ('Arial', 12, 'bold'))
    CNRlabel = Label(top, text = 'Create Notification Record', font = ('Arial', 14, 'bold'))
    requestDateLabel = Label(top, text = 'Request Date:',font = ('Arial', 12))
    requestTimeLabel = Label(top, text = 'Request Time:',font = ('Arial', 12))
    unitLabel = Label(top, text = "Requesting Unit:", font=('Arial', 12))
    locationLabel = Label(top, text = 'Location:', font = ('Arial', 12))
    agencyLabel = Label(top, text = 'Agency:',font = ('Arial', 12))
    notificationDateLabel = Label(top, text = 'Notification Date:', font = ('Arial', 12))
    notificationTime = Label(top, text = 'Notification Time:', font = ('Arial', 12))
    userLabel = Label(top, text = 'User:', font = ('Arial', 12))
    
    entryLabel.pack(anchor='w', padx=10)

    entry1 = e1.get()
    entry2 = e2.get()
    entry = entry1 + " & " + entry2

    if entry1 and entry2 != "":
        entryData = Label(top, text = entry, font = ('Arial', 12, 'italic'))
        entryData.pack(pady=10)
        LSB.log_event('SEARCH', entry , 'MLM91')
        col1 = "MR"
        col2 = "SR"
        results = LSB.search_database(db_name, table_name, col1, col2, entry1, entry2)
        
        if results != []:
            success = True

        elif results == []:
            col1 = "SR"
            col2 = "MR"
            results = LSB.search_database(db_name, table_name, col1, col2, entry1, entry2)
            success = True
            
            if results ==[]:
                success = False

        if success is not True:
            resultsFromDB= Label(top, 
                                 text = 'NO RESULTS FOUND. PLEASE TRY AGAIN.', 
                                 font = ('Arial', 12, 'italic'))    
            LSB.log_event('NOT FOUND', 'NO RESULTS FOUND' , 'MLM91')
            resultsFromDB.pack()

        else:
            resultsLabel = Label(top, text = 'RESULTS:',
                             font = ('Arial', 12, 'bold'))
            resultsLabel.pack(anchor='w', padx=10)
            result = [item for t in results for item in t]
            shortAgency = ''.join(str(result[3]))
            displayIntersection = '\n&\n'.join(map(str, result[0:2])) +'\n'
            agency = LSB.contactInfo(result[2])
            displayAgency = '\n'.join(map(str, agency[1:3]))
            LSB.log_event('MATCH', displayIntersection + shortAgency, 'MLM91')
            resultsFromDB= Label(top, text = displayIntersection +'\n'+ displayAgency, 
                                 font = ('Arial', 12, 'italic'))
            resultsFromDB.pack(pady=10)                 
    
    else:
        noDataError = Label(top, text = "Error: No Data",
                             font = ('Arial', 12), 
                             fg= "red")
        LSB.log_event('ERROR', 'NO DATA' , 'MLM91')                     
        noDataError.pack(pady=10)
     
    #Entries
    requestDateEntry = Entry(top)
    requestTimeEntry = Entry(top)
    unitEntry = Entry(top)
    notificationDateEntry = Entry(top)
    notificationTimeEntry = Entry(top)
    userEntry = Entry(top)

    #Data
    locationData = Label(top, text = displayIntersection, font = ('Arial', 10 ,'bold'))
    agencyData = Label(top, text = displayAgency, font = ('Arial', 10, 'bold'))

    #Save Button
    saveButton = Button(top, text = 'Save', width = 20, command = commandArgs)
    resetButton = Button(top,text = 'Reset', width = 20, command = None)

    #Format window    
    CNRlabel.pack(side='top')
    requestDateLabel.pack(anchor='w', padx=10, pady=5)
    requestDateEntry.pack(anchor='w', padx=13, pady=2.5)
    requestTimeLabel.pack(anchor='w', padx=10, pady=2.5)
    requestTimeEntry.pack(anchor='w', padx=13, pady=2.5)
    unitLabel.pack(anchor='w', padx=10, pady=5)
    unitEntry.pack(anchor='w', padx=13)
    locationLabel.pack(anchor='w', padx=10, pady=5)
    locationData.pack(anchor='w', padx=25)
    agencyLabel.pack(anchor='w', padx=10, pady=5)
    agencyData.pack(anchor='w', padx=25)
    notificationDateLabel.pack(anchor='w', padx=10, pady=5)
    notificationDateEntry.pack(anchor='w', padx=13)
    notificationTime.pack(anchor='w', padx=10,pady=5)
    notificationTimeEntry.pack(anchor='w', padx=13)
    userLabel.pack(anchor='w', padx=10, pady=5)
    userEntry.pack(anchor='w', padx=13)
    saveButton.pack(pady=2.5)
    resetButton.pack(pady=2.5)


    top.mainloop()

def successWindow():
    top2 = Toplevel()
    top2.minsize(250, 100)
    top2.title('Success!')
    top2.iconbitmap('imagery\Traffic_Light.ico')
    recordCreateDT = Label(top2, text = "Record Created!", font = ('Arial', 14, 'bold'))
    recordCreateDT.pack( pady = 40)
    top2.mainloop()

#Populate main window list box with recent notifications
#Unfinished - data in textbox needs better formating
def listBoxPop():
    listBox.delete(0, END)
    notificationsListBox = LSB.listBoxData()
    for notification in notificationsListBox:
        timestamp = notification[1]
        unit = notification[3]
        dirtyLoc =  str(notification[4])
        loc = dirtyLoc.replace('\n', ' ')
        dirtyAgency = str(notification[5])
        agency = dirtyAgency.replace('\n', ' ')
        user = notification[7]
        joinData = [timestamp, unit, loc, agency, user]
        showNotificationData = '    '.join(joinData)
        listBox.insert(END, showNotificationData)
    root.after(3000, listBoxPop)

#Resize BG image
def resize_image(image_path, dpi=(96, 96)):
    img = Image.open(image_path)
    width, height = img.size

    # Calculate new size based on DPI
    new_width = int(width * dpi[0] / img.info.get('dpi', (96, 96))[0])
    new_height = int(height * dpi[1] / img.info.get('dpi', (96, 96))[1])

    img = img.resize((new_width, new_height), 
                     Image.LANCZOS)
    return ImageTk.PhotoImage(img)

#Main window initializer
root = Tk()
root.minsize(525, 525)
root.title('Baltimore County Police Dispatch LiteSearch')
root.configure(bg = 'white')
root.iconbitmap('imagery\Traffic_Light.ico')
LSB.log_event('PROGRAM START', 'PROGRAM STARTED SUCCESSFULLY', 'SYS')

#Menu bar
menu = Menu(root)
root.config(menu = menu)

#File menu
filemenu = Menu(menu)
menu.add_cascade(label = 'File', menu = filemenu)
filemenu.add_command(label = 'Log', command = logFiles)

#Help Menu
helpmenu = Menu(menu)
menu.add_cascade(label = 'Help', menu = helpmenu)
helpmenu.add_command(label = 'About', command = about)
helpmenu.add_command(label = "License", command = license)
helpmenu.add_command(label = 'Contact Support', command = support)

#Unable to download Pillow on this machine. Server connect error.
#Photo Object
image = resize_image("imagery\911logo.png")
imageLabel = Label(root, 
              image = image, 
              background = 'white')

#Title header
masterLabel = Label(root, text= 'LiteSearch', font= ('Arial', 16, 'bold', 'italic'), bg= 'white')
headerLabel = Label(root, text = '\nPlease enter the intersection below for agency\n responsible for traffic light maintinence.', 
                    font = ('Arial', 12), background ='white')

#Main Rd Entry
mainRdLabel = Label(root, text = 'Main Road', font=('Arial', 10, 'bold'), background = 'white')
e1 = Entry(root, width = 50, background = 'white')

#CrossStreet Entry
crossStLabel = Label(root, text ='Cross Street', font=('Arial', 10, 'bold'), background = 'white')
e2 = Entry(root, width = 50, background ='white')

#Buttons
searchButton = Button(root, text = 'Search', width = 25, command = displayResults)
resetButton = Button(root, text = 'Reset', width = 25, command = resetEntry)

#Listbox of prior notifications
listBox = Listbox(root, width=75)

#Listbox scrollbars
scrollbarY = Scrollbar(root, orient=VERTICAL, command=listBox.yview)
scrollbarX = Scrollbar(root, orient=HORIZONTAL, command=listBox.xview)
listBox.config(yscrollcommand=scrollbarY.set)
listBox.config(xscrollcommand=scrollbarX.set)

#Format/arrange window main window
imageLabel.pack()
masterLabel.pack()
headerLabel.pack()
mainRdLabel.pack( padx = 3)
e1.pack(padx=5, pady=2.5)
crossStLabel.pack(padx=3, pady=2.5)
e2.pack(padx=5, pady=2.5)
searchButton.pack(pady=2.5)
resetButton.pack(pady=2.5)
scrollbarX.pack(side=BOTTOM, fill=BOTH)
scrollbarY.pack(side=RIGHT, fill=Y)
listBox.pack(side=LEFT, 
             #padx=10, pady=10,
             fill= BOTH, 
             expand=True)

listBoxPop()
root.mainloop()