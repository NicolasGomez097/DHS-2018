#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, GtkSource
import re
import pdb

from sim_gui_menu import MainMenu
from sym_table import Symbol_table
from Atmega328 import Atmega328
from sim_sim import Disassembler

IMAGE_DIR = "images/"

class Tools(Gtk.Box):
    def __init__(self, parent):
        super(Tools, self).__init__(
                    orientation = Gtk.Orientation.VERTICAL)
        self.parent = parent
        
        for image, handler, tooltip in (
                    ("paso.svg",    self.on_step_clicked, "Ejecutar un paso"),
                    ("correr.svg",  self.on_run_clicked, "Ejecutar"),
                    ("detener.svg", self.on_stop_clicked, "Detener"),
                    ("reset.svg",   self.on_reset_clicked, "Reiniciar")):
            btn = Gtk.Button(
                        relief = Gtk.ReliefStyle.NONE,
                        tooltip_text = tooltip)
            btn.connect("clicked", handler)
            pxb = GdkPixbuf.Pixbuf.new_from_file_at_size(IMAGE_DIR + image, 20, 20)
            img = Gtk.Image.new_from_pixbuf(pxb)
            btn.set_image(img)
            
            self.pack_start(btn, False, False, 2)
            
            
    def on_step_clicked(self, btn):
        self.parent.viewer.mark_pc(self.parent.cpu.pc, False)
        self.parent.cpu.single_step()
        self.parent.regs.update_registers()
        self.parent.viewer.mark_pc(self.parent.cpu.pc)


    def on_run_clicked(self, btn):
        pass


    def on_stop_clicked(self, btn):
        pass


    def on_reset_clicked(self, btn):
        self.parent.cpu.reset()
        self.parent.regs.update_registers()
        self.parent.viewer.mark_pc(self.parent.cpu.pc)



class Registers(Gtk.Frame):
    def __init__(self, parent):
        super(Registers, self).__init__(
                    label = "Registros",
                    vexpand = False,
                    margin = 4)
        
        self.parent = parent
        
        descr = Pango.FontDescription("Monospace 10")
        
        self.pc_store = Gtk.ListStore(str)
        self.pc_entry  = Gtk.TreeView(
                    model = self.pc_store)                    
        renderer = Gtk.CellRendererText(editable = True)
        renderer.connect("edited", self.pc_edited)
        col = Gtk.TreeViewColumn("PC:", renderer, text=0)
        self.pc_entry.append_column(col)
        self.pc_store.append(["0x0000"])
        
        flags_label = Gtk.Label("Flags:", xalign = 0)
        flags_label.modify_font(descr)
        self.flags_grid = Gtk.Grid()
        self.flag_labels = []
        
        for x, f in enumerate("ITHSVNZC"):
            lbl = Gtk.Label(f, width_request = 20)
            lbl.modify_font(descr)
            self.flags_grid.attach(lbl, x, 0, 1, 1)
            lbl = Gtk.Label("-")
            lbl.modify_font(descr)
            self.flag_labels.append(lbl)
            self.flags_grid.attach(lbl, x, 1, 1, 1)
        
        sp_label = Gtk.Label("SP:", xalign = 0)
        sp_label.modify_font(descr)
        self.sp_label2 = Gtk.Label("")
        self.sp_label2.modify_font(descr)
        
        self.reg_store = Gtk.ListStore(str, str, str, str, str, str, str, str, str)
        reg_view  = Gtk.TreeView(
                    model = self.reg_store)
                    
        renderer = Gtk.CellRendererText()
        
        col = Gtk.TreeViewColumn("Reg", renderer, text=0)
        reg_view.append_column(col)
        
        for i in range(8):
            editable_render = Gtk.CellRendererText(editable = True)
            editable_render.connect("edited", self.reg_edited, i + 1)
            col = Gtk.TreeViewColumn(" +{:d}".format(i), editable_render, text = i + 1)
            reg_view.append_column(col)
            
        for r in range(0, 32, 8):
            self.reg_store.append( ["{:d}".format(r)] + ['-']*8 )
        
        grid = Gtk.Grid(
                    margin = 4,
                    vexpand = True,
                    column_spacing = 4)
        for wdg, x, y in (
                    (self.pc_entry, 0, 0),
                    (flags_label, 0, 2), (self.flags_grid, 0, 3),
                    (sp_label, 0, 4), (self.sp_label2, 0, 5)):
            grid.attach(wdg, x, y, 1, 1)
            
        grid.attach(reg_view, 2, 0, 1, 6)
        
        self.add(grid)
        self.update_registers()

    def reg_edited(self, widget, path, text, column):
        value = int(text,0)
        text = "0x{:02x}".format(value)
        self.reg_store[path][column] = text
        self.parent.cpu.ram[int(path)*8 + column-1] = value
    
    def pc_edited(self, widget, path, text):
        try:
            value = int(text,0)
            if value%2 == 0 and int(self.parent.cpu.flash.get_highest_used()) > value:
                text = "0x{:04x}".format(value)
                self.pc_store[path][0] = text
                self.parent.viewer.mark_pc(self.parent.cpu.pc, False)
                self.parent.cpu.pc = value
                self.parent.viewer.mark_pc(value)
        except Exception as e:
            pass
            
    def update_registers(self):
        # Program counter
        self.pc_store[0][0] = "0x{:04x}".format(self.parent.cpu.pc)
        self.parent.viewer.mark_pc(self.parent.cpu.pc)
        
        # Banderas
        fl = self.parent.cpu.flags
        for bit in range(8):
            self.flag_labels[bit].set_text(str(fl >> (7 - bit) & 0x01))
            
        # Stack pointer
        self.sp_label2.set_text("0x{:04x}".format(self.parent.cpu.sp))
        
        # Registers
        self.reg_store.clear()
        for reg in range(0, 32, 8):
            l = [str(reg)] + ["0x{:02x}".format(self.parent.cpu.ram[reg + offs]) for offs in range(8)]
            self.reg_store.append(l)



class Viewer(Gtk.Notebook):
    def __init__(self, parent):
        super(Viewer, self).__init__(
                    vexpand = True,
                    hexpand = True)
        self.parent = parent
        self.dis_buffer = None
        self.dis_index = {}
        
        self.mem_buffer = Gtk.TextBuffer()
        self.mem_view = Gtk.TextView(
                    buffer = self.mem_buffer,
                    editable = False)
        descr = Pango.FontDescription("Monospace 10")
        self.mem_view.modify_font(descr)
                    
        scroller = Gtk.ScrolledWindow()
        scroller.add(self.mem_view)
        
        self.append_page(scroller, Gtk.Label("Flash"))
        
        
    def update(self, new_text):
        self.mem_buffer.set_text(new_text)

    def go_to_page(self, page_name):
        number = self.get_n_pages()
        for i in range(number):
            page = self.get_nth_page(i)
            text = self.get_tab_label_text(page)
            if text == page_name:
                return page

        return None


    def add_page(self, page_name):
        if self.go_to_page(page_name) == None:
            descr = Pango.FontDescription("Monospace 10")
            scroller = Gtk.ScrolledWindow()
            self.dis_store = Gtk.ListStore(str, str)
            self.dis_view = Gtk.TreeView(
                        model = self.dis_store)
            self.dis_selection = self.dis_view.get_selection()
            self.dis_view.modify_font(descr)
            
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn("", renderer, text = 0)
            self.dis_view.append_column(col)
            
            col = Gtk.TreeViewColumn("Codigo", renderer, text = 1)
            self.dis_view.append_column(col)
                        
            scroller.add(self.dis_view)
            scroller.show_all()
            num = self.append_page(scroller, Gtk.Label(page_name))
            self.set_current_page(num)
        else:
            self.dis_store.clear()
        return self.dis_store
        
        
    def add_disasm_page(self, page_name, dis_text):
        bff = self.add_page(page_name)
        for line in dis_text.split('\n'):
            self.dis_store.append( ("", line))
        self.reindex()
        self.parent.regs.update_registers()


    def reindex(self):
        self.dis_index = {}
        for row in self.dis_store:
            r = re.match("([0-9a-hA-H]{4})", row[1])
            if r != None:
                self.dis_index[r.group(1)] = row.path
        
    def highlight_address(self, addr):
        addrx = "{:04x}".format(addr)
        if addrx in self.dis_index:
            self.dis_selection.select_path(self.dis_index[addrx])
            self.dis_view.scroll_to_cell(self.dis_index[addrx])
            
            
    def mark_pc(self, pc, visible = True):
        addrx = "{:04x}".format(pc)
        if addrx in self.dis_index:
            itr = self.dis_store.get_iter(self.dis_index[addrx])
            self.dis_store.set_value(itr, 0, "▶" if visible else "")
            self.dis_view.scroll_to_cell(self.dis_index[addrx])


        
class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect("destroy", lambda _: Gtk.main_quit())
        self.set_size_request(500, 400)
        
        symtable = Symbol_table()
        self.cpu = Atmega328(symtable)
        self.dis = Disassembler(self.cpu)
        
        self.mainmenu = MainMenu(self)        
        self.viewer = Viewer(self)
        self.viewer.update(self.cpu.flash.dump_words())
        self.tools = Tools(self)
        self.regs = Registers(self)
        
        grid = Gtk.Grid()
        grid.attach(self.mainmenu, 0, 0, 2, 1)
        grid.attach(self.tools,    0, 1, 1, 1)
        grid.attach(self.viewer,   1, 1, 1, 1)
        grid.attach(self.regs,     0, 2, 2, 1)
        
        self.add(grid)
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
