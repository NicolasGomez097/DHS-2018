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

import re
import pdb
from sim_mem import Memory
from Atmega328 import Atmega328
from sym_table import Symbol_table


class Disassembler():
    def __init__(self, cpu):
        self.cpu = cpu
        print("Numero de instrucciones: ", len(self.cpu.opcodes))


    def load_flash(self, prog_name):
        self.cpu.load_flash(prog_name)
        
        
    def disassemble(self, pc, end):
        # Pasada 1: Recoleccion de etiquetas
        tpc = pc
        while tpc < end:
            r = self.cpu.disassemble_one_instruction(tpc, self.cpu.symtable)
            if r == None:
                raise Exception("No puedo desensamblar en 0x{:04x}".format(tpc))
            tpc = r[1]
                
        # Pasada 2: Generacion del listado
        tpc = pc
        s = ""
        while tpc < end:
            r = self.cpu.disassemble_one_instruction(tpc, self.cpu.symtable)
            if r != None:
                lbl = self.cpu.symtable.create_label(tpc)
                sym = self.cpu.symtable.find_symbol(lbl)
                if type(sym) != bool:                   # Para detectar False!
                    s += "     {:s}:\n".format(lbl)
                s += "{:04x}{:s}\n".format(tpc, r[0])
                tpc = r[1]
            else:
                break

        s += "\n"
        s += "Tabla de simbolos\n"
        for l in self.cpu.symtable.dump_table():
            s += l + "\n"
            
        return s
        


def main(args):
    symtable = Symbol_table()
    cpu = Atmega328(symtable)
    
    dis = Disassembler(cpu)
    dis.load_flash("validate_hex.hex")

    pc = 0
    fin = cpu.flash.get_highest_used()
    print(fin)
    print(dis.disassemble(pc, fin))

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
