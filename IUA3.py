#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  windows.py
#  
#  Copyright 2018 curso <curso@LABJIUA1179>
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
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect("destroy", self.on_destroy)
        self.set_size_request(300,200)
        
        grid = Gtk.Grid()
        
        self.add(grid)
        self.show_all()
    
    def on_destroy(self, wind):
        Gtk.main_quit()
    
    
    def on_click(self, btn):
        nome = self.entry.get_text()
        self.lbl2.set_text("Hola " + nome)
    
    def run(self):
        Gtk.main()

def main(args):
    mw = MainWindow()
    mw.run()
    
    return 0
    

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
