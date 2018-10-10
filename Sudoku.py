#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  iua2.py
#  
#  Copyright 2018 Unknown <root@hp425>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class Select_digit(Gtk.Dialog):
    def __init__(self):
        super(Select_digit, self).__init__()
        self.add_buttons ("Cancelar", Gtk.ResponseType.CANCEL)
        
        grid = Gtk.Grid()
        
        for y in range(3):
            for x in range(3):
                b = Gtk.Button("{:d}".format(y*3 + x + 1), 
                        relief = Gtk.ReliefStyle.NONE)
                grid.attach(b, x, y, 1, 1)
                b.connect("clicked", self.on_button_clicked)
                
                
        self.get_content_area().add(grid)
        self.show_all()
                
                
    def on_button_clicked(self, btn):
        t = int(btn.get_label())
        self.response(t)



class Sudoku(Gtk.Frame):
    def __init__(self):
        super(Sudoku, self).__init__(
                    label = "Sudoku",
                    margin = 4)

        self.grid = Gtk.Grid(
                    margin = 6,
                    column_spacing = 3,
                    row_spacing = 3)

        self.buttons = {}
        i = 0
        for y in range(11):
            dx = 3
            for x in range(11):
                if x / 3 == 1 or x / 7 == 1:
                    sep = Gtk.Separator.new(Gtk.Orientation.VERTICAL)
                    self.grid.attach(sep,x,y,1,1)
                elif y / 3 == 1 or y / 7 == 1:
                    sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
                    self.grid.attach(sep,x,y,1,1)
                else:
                    b = Gtk.Button(" ")
                    self.buttons[i] = b
                    i+=1
                    self.grid.attach(b, x, y, 1, 1)
                    b.connect("clicked", self.on_button_clicked)
            
        self.add(self.grid)
        
        
    def on_button_clicked(self, btn):
        sel = Select_digit()
        
        resp = sel.run()
        if resp in range(1, 10):
            btn.set_label(str(resp))
        sel.destroy()
        
        
    def load_original(self, loadmap):
        loadmap = loadmap.replace(" ", "").replace("-", " ")
        
        for y in range(9):
            for x in range(9):
                index = x + 9*y
                char = loadmap[index]
                b = self.buttons[index]
                b.set_label(char)
                if char != " ":
                    b.set_sensitive(False)
                

class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect("destroy", self.on_destroy)
        self.set_size_request(300, 200)
        
        sudoku = Sudoku()
        sudoku.load_original(
                "-2- 5-6 -1-"
                "6-3 179 ---"
                "-1- 3-- ---"
                "--1 --2 34-"
                "349 -1- -26"
                "2-6 4-7 8--"
                "--- 658 ---"
                "5-8 743 -6-"
                "76- --1 ---")
        
        self.add(sudoku)
        
        self.show_all()
        
        
    def on_destroy(self, wdw):
        Gtk.main_quit()
        
    def run(self):
        Gtk.main()


def main(args):
    mw = MainWindow()
    mw.run()
    
    return 0
    
    

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
