#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  sim_dis.py
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

class Symbol_table():
    def __init__(self):
        self.table = {}
        
        
    def add(self, sym, value = None):
        if  ((sym in self.table) and 
             (self.table[sym] != None) and 
             (self.table[sym] != value)):
            print("Valor definido con otro valor")
            return False
            
        self.table[sym] = value
        return True
        
        
    def create_label(self, addr):
        return "L{:04x}".format(addr)
        
        
    def find_symbol(self, sym):
        """ Funcion busca en la tabla. Devuelve:
            False: No esta en la tabla
            Valor: Si esta en la tabla y tiene valor
            None:  Si esta en la tabla y no tiene valor todavia
        """
        if sym in self.table:
            return self.table[sym]
        else:
            return False
            
    def find_none(self):
        return None in self.table.values();
            
    def dump_table(self):
        out = []
        for sym, val in sorted(self.table.items()):
            out.append("{:>20s} = {:s}".format(sym, str(val)))
        return out
        
        

def main(args):
    st = Symbol_table()
    st.add("main", 1234)
    st.add("nodef", None)
    st.add("xref", 4321)
    print("Tabla de simbolos:")
    for line in st.dump_table():
        print(line)
    print("Etiquetas sin definir: ", st.find_none())
    print("Valor de 'main': ", st.find_symbol("main"))
        
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
