#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  sim_mem.py
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

import pdb

class Memory():
    FLASH, EEPROM, SRAM, REG = range(4)
    def __init__(self, size, memtype, base = 0):
        self.size = size
        self.memtype = memtype
        self.base = base
        self.highest_used = None
        
        self.mem = bytearray(self.size)
        self.bitmap = bytearray(self.size // 8)
        

    def empty(self, addr):
        """ Retorna True/False si 'addr' esta inicializada
        """
        b = addr - self.base
        return (self.bitmap[b // 8] & (1 << (b % 8))) == 0
        
        
    def get_highest_used(self, to_str = False):
        """ Devuelve la direccion mas alta inicializada (en bytes!)
        """
        if to_str:
            if self.highest_used == None:
                return "Empty"
            else:
                return "0x{:04x}".format(self.highest_used)
        else:
            return self.highest_used
        
        
    def update_highest_used(self, addr):
        if (self.highest_used == None) or (addr > self.highest_used):
            self.highest_used = addr

        
    def save_byte(self, addr, value):
        if (addr - self.base) >= self.size:
            print("Acceso fuera de la memoria")
            return
            
        self.update_highest_used(addr)
        self.mem[addr - self.base] = value
        self.mark(addr)
        
        
    def get_byte(self, addr):
        if (addr - self.base) >= self.size:
            print("Acceso fuera de la memoria")
            return
        if self.empty(addr): 
            return
        return self.mem[addr - self.base]
        
        
    def get_word(self, addr):
        assert (addr % 2) == 0
        
        if (addr - self.base) >= self.size:
            print("Acceso fuera de la memoria")
            return
        if self.empty(addr) or self.empty(addr + 1): 
            return
        return self.mem[addr - self.base] + (self.mem[addr - self.base + 1] << 8)
        
        
    def mark(self, addr):
        b = addr - self.base
        self.bitmap[b // 8] |= (1 << (b % 8))
       
       
    def dump(self):
        s = "      +0 +1 +2 +3 +4 +5 +6 +7 +8 +9 +A +B +C +D +E +F"
        for offs in range(self.size):
            if (offs % 16) == 0:
                s += "\n{:04x}: ".format(offs + self.base)
            if self.empty(offs + self.base):
                s+= "-- "
            else:
                s += "{:02x} ".format(self.mem[offs])
         
        return s + "\n"
        
        
    def dump_words(self):
        s = "       +0   +1   +2   +3   +4   +5   +6   +7 "
        for offs in range(0, self.size, 2):
            if (offs % 16) == 0:
                s += "\n{:04x}: ".format(offs + self.base)
            if self.empty(offs + self.base):
                s+= "---- "
            else:
                s += "{:04x} ".format((self.mem[offs+1] << 8) + self.mem[offs])
         
        return s + "\n"
        
        
    def load_intel_hex(self, fname):
        with open(fname, "r") as hexf:
            for line in hexf.readlines():
                line = line.rstrip('\n ')
                if len(line) < 11:
                    continue
                if line[0] != ':':
                    continue
                # Linea parece contener datos
                checksum = 0
                nr_bytes = int(line[1 : 3], 16)
                checksum += nr_bytes
                addr_h = int(line[3 : 5], 16)
                checksum += addr_h
                addr_l = int(line[5 : 7], 16)
                checksum += addr_l
                kind = int(line[7 : 9], 16)
                checksum += kind
                
                addr = (addr_h << 8) + addr_l
                
                #pdb.set_trace()
                if kind == 1:           # Fin del archivo?
                    t = int(line[9 : 11], 16)
                    checksum += t
                    if (checksum & 0xff) == 0:
                        break
                    else:
                        return False
                        
                elif kind != 0:
                    continue
                    
                # La linea contiene datos
                for offs in range(nr_bytes):
                    b = int(line[9 + offs*2 : 11 + offs*2], 16)
                    checksum += b
                    self.save_byte(addr + offs, b)
                    
                b = int(line[-2:], 16)
                checksum += b
                if (checksum & 0xff) != 0:
                    return False
                
       

def main(args):
    print("testing sim_mem")
    mem = Memory(1024, Memory.FLASH)
    print("Highest byte used: {:s}".format(mem.get_highest_used(True)))
    mem.save_byte(10, 0xaa)
    print("Highest byte used: {:s}".format(mem.get_highest_used(True)))
    
    mem.load_intel_hex("validate_hex.hex")
    print("Highest byte used: {:s}".format(mem.get_highest_used(True)))
    print(mem.dump_words())
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
