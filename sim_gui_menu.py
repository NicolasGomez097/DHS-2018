#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class MainMenu(Gtk.MenuBar):
    def __init__(self, toplevel):
        super(MainMenu, self).__init__()
        self.toplevel = toplevel
        
        menu = Gtk.Menu()
        for label, handler in (
                    ("Cargar .hex", self.load_hex), 
                    ("Guardar .asm", self.save_asm), 
                    ("", None),
                    ("Salir", self.exit_program), ):
            if label == "":
                item = Gtk.SeparatorMenuItem()
            else:
                item = Gtk.MenuItem(label)
                if handler != None:
                    item.connect("activate", handler)
            menu.append(item)
        
        item = Gtk.MenuItem("Archivo")
        item.set_submenu(menu)
        self.add(item)
        
        # Menu de herramientas
        menu = Gtk.Menu()
        for label, handler in (
                    ("Desensamblar", self.disasm), ):
            if label == "":
                item = Gtk.SeparatorMenuItem()
            else:
                item = Gtk.MenuItem(label)
                if handler != None:
                    item.connect("activate", handler)
            menu.append(item)
        
        item = Gtk.MenuItem("Herramientas")
        item.set_submenu(menu)
        self.add(item)

        # Menu de ayuda
        menu = Gtk.Menu()
        for label, handler in (
                    ("Acerca", self.about), ):
            if label == "":
                item = Gtk.SeparatorMenuItem()
            else:
                item = Gtk.MenuItem(label)
                if handler != None:
                    item.connect("activate", handler)
            menu.append(item)
        
        item = Gtk.MenuItem("Ayuda")
        item.set_submenu(menu)
        self.add(item)
      
        
    def load_hex(self, item):
        dlg = Gtk.FileChooserDialog(
                    parent = self.toplevel,
                    action = Gtk.FileChooserAction.OPEN,
                    buttons = ("Cancelar", Gtk.ResponseType.CANCEL,
                               "Cargar",   Gtk.ResponseType.ACCEPT))
             
        if dlg.run() == Gtk.ResponseType.ACCEPT:
            fname = dlg.get_filename()
            self.toplevel.cpu.flash.load_intel_hex(fname)
            self.toplevel.viewer.update(self.toplevel.cpu.flash.dump_words())
        dlg.destroy()
        
        
    def save_asm(self, item):
        dlg = Gtk.FileChooserDialog(
                    parent = self.toplevel,
                    action = Gtk.FileChooserAction.SAVE,
                    do_overwrite_confirmation = True,
                    buttons = ("Cancelar", Gtk.ResponseType.CANCEL,
                               "Guardar",  Gtk.ResponseType.ACCEPT))
             
        if dlg.run() == Gtk.ResponseType.ACCEPT:
            fname = dlg.get_filename()
            self.toplevel.cpu.flash.load_intel_hex(fname)
            self.toplevel.viewer.update(self.toplevel.cpu.flash.dump_words())
        dlg.destroy()
        
        
    def disasm(self, item):
        self.toplevel.viewer.add_disasm_page(
                "Desensamblado",
                self.toplevel.dis.disassemble(0, self.toplevel.cpu.flash.get_highest_used()))
            
    def exit_program(self, item):
        exit(0)
        
        
    def about(self, item):
        dlg = Gtk.AboutDialog(
            parent = self.toplevel,
            program_name = "Simulador AtMega 328 "
        )
        dlg.connect("response", lambda x, y: x.destroy())
        dlg.show()
        
        

class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect("destroy", lambda _: Gtk.main_quit())
        
        self.mainmenu = MainMenu(self)        
        
        self.add(self.mainmenu)
        self.show_all()
        
        
    def run(self):
        Gtk.main()


def main(args):
    mw = MainWindow()
    mw.run()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
