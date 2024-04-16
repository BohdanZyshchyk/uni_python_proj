# -*- coding: utf-8 -*-
from tkinter.ttk import Notebook, Combobox 

try:
    from Tkinter import *
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog

    raise RuntimeError('Python 2 not supported! Restart script with python from venv')
except ImportError:
    from tkinter import *
    from tkinter import messagebox
    from tkinter import filedialog
    from tkinter.simpledialog import Dialog

import os
import xml.etree.ElementTree as ET
import platform


def GetScriptExtension():
    name = platform.system()
    if name == "Windows":
        return ".cmd"
    else:
        return ".command"

def GetPlatform():
    name = platform.system()
    if name == "Windows":
        return "win"
    else:
        return "mac"

if GetPlatform() == 'win':
    import win32gui, win32con

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

class ProjectDialog(Dialog):

        def __init__(self, parent, path, script, filetypes, filename_extension, title=None):
            self.project_path = StringVar()
            self.build_path = StringVar()
            self.module_name = StringVar()
            self.remove_sources = BooleanVar()
            self.path_script = path
            self.script_name = script
            self.filename_extension = filename_extension
            self.filetypes = filetypes
            self.cb = None
            self.modules = []
            Dialog.__init__(self, parent, title)

        def ask_project_file(self):
            return filedialog.askopenfilename(filetypes=[(self.filetypes, self.filename_extension)])

        def ask_build_path(self):
            return filedialog.askdirectory()

        def select_project_path(self):
            project_path = self.ask_project_file()
            self.set_project_path(project_path)

        def set_project_path(self, project_path):
            self.project_path.set(project_path)

        def select_build_path(self):
            build_path = self.ask_build_path()
            if build_path:
                self.build_path.set(build_path)

        def body(self, master):
            # Basic scheme filename
            frame = Frame(master)
            Label(frame, text='Project file:').pack(side=LEFT)
            Label(frame, textvariable=self.project_path).pack(side=LEFT)
            Button(frame, text='..', command=self.select_project_path).pack(side=LEFT)
            frame.pack(anchor=W)

        def buttonbox(self):
            box = Frame(self)

            w = Button(box, text="Combine", width=10, command=self.combine, default=ACTIVE)
            w.pack(side=LEFT, padx=5, pady=5)
            w = Button(box, text="Cancel", width=10, command=self.cancel)
            w.pack(side=LEFT, padx=5, pady=5)

            self.bind("<Return>", self.combine)
            self.bind("<Escape>", self.cancel)

            box.pack()

        def combine(self):
            if self.project_path:
                cwd = os.getcwd()
                if "." in self.script_name:
                    command = 'cd '+ cwd + self.path_script + ' && start '  + self.script_name  +  " " + self.project_path.get()
                else:
                    command = 'cd '+ cwd + self.path_script + ' && start '  + self.script_name + GetScriptExtension() +  " " + self.project_path.get()
                print(command)
                os.system(command)

root = Tk()

class Tab(Frame):
    def __init__(self, parent, node):
        super().__init__(parent)
        self.parent = parent
        self.InitUI(node)

    def onClick(self, script, path, params=None):
        cwd = os.getcwd()
        name = platform.system()
        inputValue = ''
        if params:
            inputValue = params.get()
        if "." in script:
            command = '@echo off && cd '+ cwd + path + '&& start ' + script + f' {inputValue}' f' {inputValue}'
        else:
            command = '@echo off && cd '+ cwd + path + '&& start ' + script + GetScriptExtension() + f' {inputValue}'
        if name != "Windows":
            command = 'cd '+ cwd + path + '&& '+ cwd + path + script + GetScriptExtension() + f' {inputValue}'

        os.system(command)
        

    def InitTab(self, node):
        columnNum = 0
        for column in node:
            self.InitColumn(column, columnNum)
            columnNum = columnNum + 1

    def InitUI(self, node):
        self.InitTab(node)

    def InitButtonImpl(self, node, buttonName, scriptName, scriptPath, row, column, params = None, columnspan=None):
        fun = lambda script=scriptName, path=scriptPath : self.onClick(script, scriptPath, params)
        button = Button(self, text=buttonName, command=fun)
        button.grid(row=row, column=column, sticky='news', padx = 3, pady = 1, columnspan=columnspan)
        tooltip = node.get("tooltip")
        if  tooltip != None :
            CreateToolTip(button, tooltip)

    def InitButton(self, node, buttonNum, columnNum):
        nameButton = node.get("name")
        scriptName = node.get("scriptName")
        scriptPath = node.get("scriptPath")

        self.InitButtonImpl(node, nameButton, scriptName, scriptPath, buttonNum, columnNum)
        print("AddButton", nameButton)

    def InitButtonParameters(self, node, buttonNum, columnNum):
        nameButton = node.get("name")
        scriptName = node.get("scriptName")
        scriptPath = node.get("scriptPath")
        defaultValue = node.get("defaultValue")
        labelName = node.get("label")

        print("AddButton", nameButton)

        # Create the Label widget for the text
        label = Label(self, text=labelName)
        label.grid(row=buttonNum+1, column=columnNum, sticky='w', padx = 3, pady = 1, columnspan=1)
        
        # Create the Entry widget for the input field
        entryText = StringVar()
        entry = Entry(self, textvariable=entryText)
        # Insert a default value
        entry.insert(0, defaultValue)
        # Position the entry widget in the grid right next to the label
        entry.grid(row=buttonNum+2, column=columnNum, sticky='news', padx = 3, pady = 1, columnspan=1)
        self.InitButtonImpl(node, nameButton, scriptName, scriptPath, buttonNum, columnNum, entryText)

    def InitButtonExplorer(self, node, buttonNum, columnNum):
        nameButton = node.get("name")
        scriptName = node.get("scriptName")
        scriptPath = node.get("scriptPath")
        title = node.get("title")
        filenameExtension = node.get("filenameExtension")
        filetypes = node.get("filetypes")

        button = Button(self, text=nameButton, command = lambda : ProjectDialog(root, scriptPath, scriptName, filetypes, filenameExtension, title=title))
        button.grid(row=buttonNum, column=columnNum, sticky='news', padx = 3, pady = 1)
        tooltip = node.get("tooltip")
        if  tooltip != None :
            CreateToolTip(button, tooltip)

    def InitColumn(self, node, columnNum):
        buttonNum = 0
        for button in node:
            platformOS = button.get("platform")
            platformOK = platformOS == None
            platformOK = platformOK | (platformOS == GetPlatform())
            if platformOK :
               if button.tag == "ButtonExplorer":
                  self.InitButtonExplorer(button, buttonNum, columnNum)
                  buttonNum = buttonNum + 1
               elif button.tag == "Button":
                  self.InitButton(button, buttonNum, columnNum)
                  buttonNum = buttonNum + 1
               elif button.tag == "ButtonParemeters":
                  self.InitButtonParameters(button, buttonNum, columnNum)
                  buttonNum = buttonNum + 3

class MainWindow(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.parent.title("Menu for developer")
        self.centerWindow()
        self.initUI()

    def centerWindow(self):
        w = 550
        h = 300

        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()

        x = (sw - w) / 2
        y = (sh - h) / 2

        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def initUI(self):
        self.parent['padx'] = 10
        self.parent['pady'] = 10
        self.notebook = Notebook(self, width=1000, height=700)

        tree = ET.parse('./menu/scripts.xml')
        treeRoot = tree.getroot()

        for child in treeRoot:
            tabName = child.get("name")
            self.notebook.add(Tab(self,child), text=tabName)

        self.notebook.pack()
        self.pack()

def main():
    window = MainWindow(root)
    if GetPlatform() == 'win':
        hide = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hide , win32con.SW_HIDE)
    root.mainloop()

if __name__ == '__main__':
	main()
