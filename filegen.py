import tkinter as tk
import tkinter.messagebox
import re
import datetime
import typing

hdr_template = """/// @brief  %classname% class definition
/// @author Eugene Gorbachev (eugeneg@cqg.com)
/// @date   Created on: %date%

#pragma once

"""

hdr_body_class_template = """/// <description>
class %classname%
{
public:
   explicit %classname%();
   virtual ~%classname%();
};
"""

hdr_body_interface_template = """/// <description>
class %classname%
{
public:
   virtual ~%classname%() = default;
};
"""

src_header_template = """/// @brief  %classname% class implementation
/// @author Eugene Gorbachev (eugeneg@cqg.com)
/// @date   Created on: %date%

#include "stdafx.h"
#include "%hdrfile%"

"""

src_body_template = """%classname%::%classname%()
{
}

%classname%::~%classname%()
{
}
"""


def is_alpha_num(word):
    m = re.match('^[a-z_][a-z0-9_]', word, re.S | re.IGNORECASE)
    return m is not None


def get_file_name(class_name: str, is_src_file: bool) -> str:
    is_old_hungarian_notation_for_class = re.match('^C[A-Z]', class_name, re.S)
    ext = "cpp" if is_src_file else "h"
    return (class_name[1:] if is_old_hungarian_notation_for_class else class_name) + "." + ext


class FileGenerator:
    def __init__(self, class_name: str, namespaces: typing.List[str]):
        self.namespaces = []
        for namespace in namespaces.split():
            namespace = namespace.strip()
            if not is_alpha_num(namespace):
                raise RuntimeError("Namespace '" + namespace + "' is not alphanumeric, a-z, 0-9, _ allowed only")
            self.namespaces.append(namespace)
        self.class_name = class_name.strip()
        self.is_interface = re.match('^I[A-Z]', self.class_name)

        if not is_alpha_num(self.class_name):
            raise RuntimeError("Class name '" + self.class_name + "' is not alphanumeric, a-z, 0-9, _ allowed only")
        self.hdr_header = ''
        self.hdr_body = ''
        self.src_header = ''
        self.src_body = ''
        self.instantiate()
        self.write()

    def instantiate(self):
        hdr_file_name = get_file_name(self.class_name, False)
        src_file_name = get_file_name(self.class_name, True)
        now = datetime.datetime.now()
        now_str = now.strftime("%d-%b-%Y")
        self.hdr_header = hdr_template.replace('%classname%', self.class_name)
        self.hdr_header = self.hdr_header.replace('%hdrfile%', hdr_file_name)
        self.hdr_header = self.hdr_header.replace('%date%', now_str)
        self.hdr_body = hdr_body_interface_template.replace('%classname%', self.class_name) if self.is_interface \
            else hdr_body_class_template.replace('%classname%', self.class_name)
        self.src_header = src_header_template.replace('%classname%', self.class_name)
        self.src_header = self.src_header.replace('%srcfile%', src_file_name)
        self.src_header = self.src_header.replace('%date%', now_str)
        self.src_header = self.src_header.replace('%hdrfile%', hdr_file_name)
        self.src_body = src_body_template.replace('%classname%', self.class_name)

    def write_namespace_opening(self, f):
        for namespace in self.namespaces:
            f.writelines(["namespace " + namespace + "\n", "{\n", "\n"])

    def write_namespace_closing(self, f):
        for _ in self.namespaces:
            f.writelines(["\n", "}\n"])

    def write(self):
        with open(get_file_name(self.class_name, False), mode='w') as f:
            f.write(self.hdr_header)
            self.write_namespace_opening(f)
            f.write(self.hdr_body)
            self.write_namespace_closing(f)

        if not self.is_interface:
            with open(get_file_name(self.class_name, True), mode='w') as f:
                f.write(self.src_header)
                self.write_namespace_opening(f)
                f.write(self.src_body)
                self.write_namespace_closing(f)


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.class_name = None
        self.namespaces = None
        self.file_creator = None
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        f1 = tk.Frame(self)
        f1.pack(padx=8, pady=8)

        tk.Label(f1, text="Class name").grid(row=1, column=1, padx=8, pady=8)
        self.class_name = tk.StringVar()
        ent_class_name = tk.Entry(f1, width=50, textvariable=self.class_name)
        ent_class_name.grid(row=1, column=2, padx=8, pady=8)
        ent_class_name.bind("<Key>", self.on_enter_class_name)
        self.class_name.set("MyClass")

        tk.Label(f1, text="Namespace(s)").grid(row=2, column=1, padx=8, pady=8)
        self.namespaces = tk.StringVar()
        ent_namespace = tk.Entry(f1, width=50, textvariable=self.namespaces)
        ent_namespace.grid(row=2, column=2, padx=8, pady=8)
        self.namespaces.set("webapi imm")

        self.file_creator = tk.Button(self)
        self.file_creator["text"] = "Create File(s)"
        self.file_creator["command"] = self.create_file
        self.file_creator.pack(side="right", padx=8, pady=8)

    def on_enter_class_name(self, _):
        class_name = self.class_name.get()
        disable = len(class_name) < 5
        self.file_creator.configure(state="disable" if disable else "normal")

    def create_file(self):
        class_name = self.class_name.get()
        if not class_name:
            tkinter.messagebox.showerror("Error", "No class name specified")
            return
        try:
            FileGenerator(class_name, self.namespaces.get())
        except Exception as e:
            tkinter.messagebox.showerror("Error", str(e))


root = tk.Tk()
app = Application(master=root)
app.mainloop()
