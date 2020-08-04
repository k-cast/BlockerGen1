#!/usr/bin/python
import tkinter
from tkinter import messagebox
from tkinter import *
import tkinter.font as font
from BlockerGen1 import *

## GUI ##
root = Tk()
root.title('Automated Spotter Gen1')
#root.config(cursor='none') 
root.geometry('800x480') #windowed mode for dev
#root.attributes('-fullscreen', True) 

buttonFont = font.Font(family='Helvetica', size=18, weight='bold')

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

def ExitApplication():
    MsgBox = messagebox.askquestion('Exit Application','Are you sure you want to exit the application?',icon = 'warning')
    if MsgBox == 'yes':
        robot.close()
        pump.close()
        root.destroy()
    else:
        messagebox.showinfo('Return','You will now return to the application screen.')

initButton = Button(root, text='INITIALIZE', bg='springgreen', command=initialize)
initButton['font'] = buttonFont

exitButton = Button(root, text='CLOSE', width=17, fg='red', command=ExitApplication)
exitButton['font'] = buttonFont

sysprimeButton = Button(root, text='PRIME', width=17, bg='paleturquoise', command=sysprime)
sysprimeButton['font'] = buttonFont

originButton = Button(root, text='OFFSET POS.', bg='darkorange', command=origin)
originButton['font'] = buttonFont

fillButton = Button(root, text='FILL', bg='deepskyblue', height= 3, command=fill)
fillButton['font'] = buttonFont

emptyButton = Button(root, text='EMPTY', bg='IndianRed1', command=empty)
emptyButton['font'] = buttonFont

babaluButton = Button(root, text='RUN\n BABALU/FALCON', bg='purple1', height=4, command=babalu)
babaluButton['font'] = buttonFont

falconButton = Button(root, text='RUN\n FALCON', bg='purple1', height=4, command=falcon)
falconButton['font'] = buttonFont

cardeaButton = Button(root, text='RUN\n CARDEA/GAIA', bg='orchid1', height=4, command=cardea) 
cardeaButton['font'] = buttonFont

gaiaButton = Button(root, text='RUN\n GAIA', bg='orchid1', height=4, command=gaia) 
gaiaButton['font'] = buttonFont

sysprimeButton.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
originButton.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')
initButton.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
exitButton.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')
fillButton.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
emptyButton.grid(row=1, column=2, padx=5, pady=5, sticky='nsew')
babaluButton.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')
falconButton.grid(row=2, column=2, padx=5, pady=5, sticky='nsew')
cardeaButton.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')
gaiaButton.grid(row=3, column=2, padx=5, pady=5, sticky='nsew')

if __name__ == '__main__':
    root.mainloop()
