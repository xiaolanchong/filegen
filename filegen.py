import tkinter as tk
import tkinter.messagebox
import re
import datetime

hdrTemplate = \
"""/// @file   %hdrfile%
/// @brief  %classname% class definition
/// @author Eugene Gorbachev (eugeneg@cqg.com)
/// @date   Created on: %date%

#pragma once

"""

hdrBodyTemplate = \
"""/// <description>
class %classname%
{
public:
   explicit %classname%();
   virtual ~%classname%();
};
"""

srcHeaderTemplate = \
"""/// @file   %srcfile%
/// @brief  %classname% class implementation
/// @author Eugene Gorbachev (eugeneg@cqg.com)
/// @date   Created on: %date%

#include "stdafx.h"
#include "%hdrfile%"

"""

srcBodyTemplate = \
"""%classname%::%classname%()
{
}

%classname%::~%classname%()
{
}
"""

def isAlphaNum(word):
    m = re.match('^[a-z_][a-z0-9_]', word, re.S | re.IGNORECASE)
    return m is not None

def getFileName(className, isSrcFile):
    m = re.match('^(I|C)[A-Z]', className, re.S)
    ext = "cpp" if isSrcFile else "h"
    return (className[1:] if m else className) + "." + ext

class FileGenerator:
    def __init__(self, className, namespaces):
        self.namespaces = []
        for namespace in namespaces.split():
            namespace = namespace.strip()
            if not isAlphaNum(namespace):
                raise RuntimeError("Namespace '" + namespace + "' is not alphanumeric, a-z, 0-9, _ allowed only")
            self.namespaces.append(namespace)
        self.className = className.strip()

        if not isAlphaNum(self.className):
            raise RuntimeError("Class name '" + self.className + "' is not alphanumeric, a-z, 0-9, _ allowed only")
        self.instantiate()
        self.write()

    def instantiate(self):
        hdrFileName = getFileName(self.className, False)
        srcFileName = getFileName(self.className, True)
        now = datetime.datetime.now()
        nowStr = now.strftime("%d-%b-%Y")
        self.hdrHeader = hdrTemplate.replace('%classname%', self.className)
        self.hdrHeader = self.hdrHeader.replace('%hdrfile%',   hdrFileName)
        self.hdrHeader = self.hdrHeader.replace('%date%',   nowStr)
        self.hdrBody = hdrBodyTemplate.replace('%classname%', self.className)
        self.srcHeader = srcHeaderTemplate.replace('%classname%', self.className)
        self.srcHeader = self.srcHeader.replace('%srcfile%',   srcFileName)
        self.srcHeader = self.srcHeader.replace('%date%',   nowStr)
        self.srcHeader = self.srcHeader.replace('%hdrfile%',   hdrFileName)
        self.srcBody = srcBodyTemplate.replace('%classname%', self.className)

    def writeNamespaceOpening(self, f):
        for namespace in self.namespaces:
            f.writelines(["namespace " + namespace + "\n", "{\n", "\n"])

    def writeNamespaceClosing(self, f):
        for namespace in self.namespaces:
            f.writelines(["\n", "}\n"])

    def write(self):
        with open(getFileName(self.className, False) ,mode='w') as f:
            f.write(self.hdrHeader)
            self.writeNamespaceOpening(f)
            f.write(self.hdrBody)
            self.writeNamespaceClosing(f)

        with open(getFileName(self.className, True) ,mode='w') as f:
            f.write(self.srcHeader)
            self.writeNamespaceOpening(f)
            f.write(self.srcBody)
            self.writeNamespaceClosing(f)

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        f1 = tk.Frame(self)
        f1.pack(padx=8, pady=8)

        tk.Label(f1, text="Class name").grid(row = 1, column = 1, padx=8, pady=8)
        self.className = tk.StringVar()
        entClassName = tk.Entry(f1, width=50, textvariable=self.className)
        entClassName.grid(row = 1, column = 2, padx=8, pady=8)
        entClassName.bind("<Key>", self.onEnterClassName)
        self.className.set("MyClass")

        tk.Label(f1, text="Namespace(s)").grid(row = 2, column = 1, padx=8, pady=8)
        self.namespaces = tk.StringVar()
        entNamespace = tk.Entry(f1, width=50, textvariable=self.namespaces)
        entNamespace.grid(row = 2, column = 2, padx=8, pady=8)
        self.namespaces.set("webapi imm")

       # f2 = tk.Frame(self)
       # f2.pack(padx=8, pady=8)
       # self.chkInterface = tk.Checkbutton(f2, text="Interface")
       # self.chkInterface.pack(side="right")

        self.fileCreator = tk.Button(self)
        self.fileCreator["text"] = "Create File(s)"
        self.fileCreator["command"] = self.createFile
        self.fileCreator.pack(side="right", padx=8, pady=8)

    def onEnterClassName(self, event):
        className = self.className.get()
        disable = len(className) < 5
        self.fileCreator.configure(state ="disable" if disable else "normal")

    def createFile(self):
        className = self.className.get()
        if not className:
            tkinter.messagebox.showerror("Error", "No class name specified")
            return
        try:
            gen = FileGenerator(className, self.namespaces.get())
        except Exception as e:
            tkinter.messagebox.showerror("Error", str(e))




root = tk.Tk()
app = Application(master=root)
app.mainloop()

