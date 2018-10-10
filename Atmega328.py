#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Atmega328.py
#
#  Copyright 2018 John Coppens <john@jcoppens.com>
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
from sim_mem import Memory

class OPC():
    mask      = 0
    remainder = 0
    opcstr    = ""
    opdcmd    = ""
    fmt       = None
    sim_instr = None

    def __init__(self, mask, remainder, opcstr, opdcmd, fmt, sim_instr):
        self.mask = mask
        self.remainder = remainder
        self.opcstr = opcstr
        self.opdcmd = opdcmd
        self.fmt = fmt
        self.sim_instr = sim_instr


class Atmega328():
    def calc_addr(self, pc, offs, rng):
        return pc + 2*(offs if offs < (rng // 2)
            else offs - rng)

    imm_4      = lambda d, s: "{K[0]:d}".format(**d)
    bit        = lambda d, s: "{s[0]:d}".format(**d)
    reg        = lambda d, s: "r{d[0]:d}".format(**d)
    reg_imm    = lambda d, s: "r{d[0]:d}, 0x{K[0]:x}".format(**d)
    reg8_imm   = lambda d, s: "r{:d}, 0x{:x}".format(d["d"][0] + 16, d["K"][0])
    reg_imm16  = lambda d, s: "r{d[0]:d}, 0x{k[0]:x}".format(**d)
    imm7_reg   = lambda d, s: "0x{k[0]:x}, r{d[0]:d}".format(**d)
    imm16_reg  = lambda d, s: "0x{k[0]:x}, r{d[0]:d}".format(**d)
    reg_bit    = lambda d, s: "r{d[0]:d}, {b[0]:x}".format(**d)
    bit_reg    = lambda d, s: "{b[0]:x}, r{d[0]:d}".format(**d)
    reg_reg    = lambda d, s: "r{d[0]:d}, r{r[0]:d}".format(**d)
    reg3_reg3  = lambda d, s: "r{:d}, r{:d}".format(d["d"][0] + 16, d["r"][0] + 16)
    reg4_reg4  = lambda d, s: "r{:d}, r{:d}".format(d["d"][0] + 16, d["r"][0] + 16)
    reg4       = lambda d, s: "r{:d}".format(d["d"][0] + 16)
    reg_x      = lambda d, s: "r{d[0]:d}, X".format(**d)
    reg_mx     = lambda d, s: "r{d[0]:d}, -X".format(**d)
    reg_xp     = lambda d, s: "r{d[0]:d}, X+".format(**d)
    reg_y      = lambda d, s: "r{d[0]:d}, Y".format(**d)
    reg_yp     = lambda d, s: "r{d[0]:d}, Y+".format(**d)
    reg_my     = lambda d, s: "r{d[0]:d}, -Y".format(**d)
    reg_yo     = lambda d, s: "r{d[0]:d}, Y+{q[0]:d}".format(**d)
    reg_z      = lambda d, s: "r{d[0]:d}, Z".format(**d)
    reg_zp     = lambda d, s: "r{d[0]:d}, Z+".format(**d)
    reg_mz     = lambda d, s: "r{d[0]:d}, -Z".format(**d)
    reg_zo     = lambda d, s: "r{d[0]:d}, Z+{q[0]:d}".format(**d)
    reg_io     = lambda d, s: "r{d[0]:d}, 0x{A[0]:02x}".format(**d)
    x_reg      = lambda d, s: "X, r{r[0]:d}".format(**d)
    xp_reg     = lambda d, s: "X+, r{r[0]:d}".format(**d)
    mx_reg     = lambda d, s: "-X, r{r[0]:d}".format(**d)
    y_reg      = lambda d, s: "Y, r{r[0]:d}".format(**d)
    yp_reg     = lambda d, s: "Y+, r{r[0]:d}".format(**d)
    my_reg     = lambda d, s: "-Y, r{r[0]:d}".format(**d)
    yo_reg     = lambda d, s: "Y+{q[0]:d}, r{r[0]:d}".format(**d)
    z_reg      = lambda d, s: "Z, r{d[0]:d}".format(**d)
    zp_reg     = lambda d, s: "Z+, r{d[0]:d}".format(**d)
    mz_reg     = lambda d, s: "-Z, r{d[0]:d}".format(**d)
    zo_reg     = lambda d, s: "Z+{q[0]:d}, r{d[0]:d}".format(**d)
    dreg_imm   = lambda d, s: "r{:d}, 0x{:x}".format(d["d"][0]*2+24, d["K"][0])
    dreg_dreg  = lambda d, s: "r{:d}, r{:x}".format(d["d"][0]*2, d["r"][0]*2)
    rel_add    = lambda d, s: "0x{:04x}".format(s.calc_addr(d["pc"], d["k"][0], 128))
    rel_add12  = lambda d, s: "0x{:04x}".format(s.calc_addr(d["pc"], d["k"][0], 4096))
    add17      = lambda d, s: "0x{k[0]:04x}".format(**d)
    bit_rel    = lambda d, s: "{s[0]:d}, 0x{k[0]:04x}".format(**d)
    no_opd     = lambda d, s: ""
    io_bit     = lambda d, s: "0x{A[0]:02x}, {b[0]:d}".format(**d)
    io_reg     = lambda d, s: "0x{A[0]:02x}, r{r[0]:d}".format(**d)
    reg8_reg8  = lambda d, s: "r{:d}, r{:d}".format(d["d"][0]+16, d["r"][0]+16)
    just_zp    = lambda d, s: "Z+"

    #ENUM
    I = 7
    T = 6
    H = 5
    S = 4
    V = 3
    N = 2
    Z = 1
    C = 0

    #GRUPO N
    def f_imm_4(self, opcstr, opd_dict):
        pass

    def f_bit(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg(self, opcstr, opd_dict):
        d = opd_dict["d"][0]

        #TST
        if opcstr == "tst":
            #calculo del resultado
            res = self.ram[d] & self.ram[d]
            
            #calculo de v
            self.set_flag(self.V,0)
            
            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))
            
            #calculo de s
            self.set_flag(self.S,self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff == 0:
                self.set_flag(self.Z,1)
            else:
                self.set_flag(self.Z,0)

    #GRUPO N
    def f_reg_imm(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg8_imm(self, opcstr, opd_dict):
        d = opd_dict["d"][0] + 16
        k = opd_dict["K"][0]

        #ANDI
        if opcstr == "andi":
            #calculo del resultado
            res = self.ram[d] & k

            #calculo de v
            self.set_flag(self.V,0)

            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))

            #calculo de s
            self.set_flag(self.S, self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff == 0:
                self.set_flag(self.Z,1)
            else:
                self.set_flag(self.Z,0)

            #guardado del resultado en el registro
            self.ram[d] = res & 0xff
        #CPI
        elif opcstr == "cpi":
            #calculo del resultado
            res = self.ram[d] - k

            #calculo de h
            d3 = self.get_bit(self.ram[d], 3)
            k3 = self.get_bit(k, 3)
            res3 = self.get_bit(res, 3)

            self.set_flag(self.H, (~d3) & k3 | k3 & res3 | res3 & (~d3))

            #calculo de v
            d7 = self.get_bit(self.ram[d], 7)
            k7 = self.get_bit(k, 7)
            res7 = self.get_bit(res, 7)

            self.set_flag(self.V, d7 & (~k7) & (~res7) | (~d7) & k7 & res7)

            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))

            #calculo de s
            self.set_flag(self.S, self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff == 0:
                self.set_flag(self.Z,1)
            else:
                self.set_flag(self.Z,0)

            #calculo de c
            if k > self.ram[d]:
                self.set_flag(self.C,1)
            else:
                self.set_flag(self.C,0)
        #ORI
        elif opcstr == "ori":
            #calculo del resultado
            res = self.ram[d] | k
            
            #calculo de v
            self.set_flag(self.V,0)
            
            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))
            
            #calculo de s
            self.set_flag(self.S,self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff == 0:
                self.set_flag(self.Z,1)
            else:
                self.set_flag(self.Z,0)
    
            #guardado del resultado en el registro
            self.ram[d] = res & 0xff
        #SBCI
        elif opcstr == "sbci":
            #calculo del resultado
            res = self.ram[d] - k - self.get_flag(7)

            #calculo de h
            d3 = self.get_bit(self.ram[d], 3)
            k3 = self.get_bit(k, 3) 
            res3 = self.get_bit(res, 3)
    
            self.set_flag(self.H, (~d3) & k3 | k3 & res3 | res3 & (~d3))

            #calculo de v
            d7 = self.get_bit(self.ram[d], 7) 
            k7 = self.get_bit(k, 7) 
            res7 = self.get_bit(res, 7)

            self.set_flag(self.V, d7 & (~k7) & (~res7) | (~d7) & k7 & res7)

            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))

            #calculo de s
            self.set_flag(self.S,self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff != 0:
                self.set_flag(self.Z, 0)

            #calculo de c
            d7 = self.get_bit(self.ram[d], 7) 
            k7 = self.get_bit(k, 7) 
            res7 = self.get_bit(res, 7)

            self.set_flag(self.C, (~d7) & k7 | k7 & res7 | res7 & (~d7))

            #guardado del resultado en el registro
            self.ram[d] = res & 0xff
            
    #GRUPO N
    def f_reg_imm16(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_imm7_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_imm16_reg(self, opcstr, opd_dict):
        pass

    #GRUPO 4
    def f_reg_bit(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_bit_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg_reg(self, opcstr, opd_dict):
        d = opd_dict["d"][0]
        r = opd_dict["r"][0]

        #ADC
        if opcstr == "adc":
            #calculo del resultado
            res = self.ram[r] + self.ram[d] + self.get_flag(self.C)


            #calculo de h
            d3 = self.get_bit(self.ram[d], 3)
            r3 = self.get_bit(self.ram[r], 3)
            res3 = self.get_bit(res, 3)

            self.set_flag(self.H, d3 & r3 | r3 & (~res3) | (~res3) & d3)

            #calculo de v
            d7 = self.get_bit(self.ram[d], 7)
            r7 = self.get_bit(self.ram[r], 7)
            res7 = self.get_bit(res, 7)

            self.set_flag(self.V, d7 & r7 & (~res7) | (~d7) & (~r7) & res7)

            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))

            #calculo de s
            self.set_flag(self.S, self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff == 0:
                self.set_flag(self.Z,1)
            else:
                self.set_flag(self.Z,0)
            print(self.flags)


            #calculo de c
            crr = self.get_bit(res,8)
            self.set_flag(self.C,crr)

            #guardado del resultado en el registro
            self.ram[d] = res & 0xff
        #ADD
        elif opcstr == "add":
            #calculo del resultado
            res = self.ram[r] + self.ram[d]

            #calculo de h
            d3 = self.get_bit(self.ram[d], 3)
            r3 = self.get_bit(self.ram[r], 3)
            res3 = self.get_bit(res, 3)

            self.set_flag(self.H, d3 & r3 | r3 & (~res3) | (~res3) & d3)

            #calculo de v
            d7 = self.get_bit(self.ram[d], 7)
            r7 = self.get_bit(self.ram[r], 7)
            res7 = self.get_bit(res, 7)

            self.set_flag(self.V, d7 & r7 & (~res7) | (~d7) & (~r7) & res7)

            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))

            #calculo de s
            self.set_flag(self.S, self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff == 0:
                self.set_flag(self.Z,1)
            else:
                self.set_flag(self.Z,0)

            #calculo de c
            c = self.get_bit(res ,8)
            self.set_flag(self.C, c)

            #guardado del resultado en el registro
            self.ram[d] = res & 0xff
        #AND
        elif opcstr == "and":
            #calculo del resultado
            res = self.ram[d] & self.ram[r]

            #calculo de v
            self.set_flag(self.V,0)

            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))

            #calculo de s
            self.set_flag(self.S, self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff == 0:
                self.set_flag(self.Z,1)
            else:
                self.set_flag(self.Z,0)

            #guardado del resultado en el registro
            self.ram[d] = res & 0xff
        #CP
        elif opcstr == "cp":
            #calculo del resultado
            res = self.ram[d] - self.ram[r]

            #calculo de h
            d3 = self.get_bit(self.ram[d], 3)
            r3 = self.get_bit(self.ram[r], 3)
            res3 = self.get_bit(res, 3)

            self.set_flag(self.H, (~d3) & r3 | r3 & res3 | res3 & (~d3))
            #calculo de v
            d7 = self.get_bit(self.ram[d], 7)
            r7 = self.get_bit(self.ram[r], 7)
            res7 = self.get_bit(res, 7)

            self.set_flag(self.V, d7 & (~r7) & (~res7) | (~d7) & r7 & res7)

            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))

            #calculo de s
            self.set_flag(self.S, self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff == 0:
                self.set_flag(self.Z,1)
            else:
                self.set_flag(self.Z,0)

            #calculo de c
            d7 = self.get_bit(self.ram[d], 7)
            r7 = self.get_bit(self.ram[r], 7)
            res7 = self.get_bit(res, 7)

            self.set_flag(self.C, (~d7) & r7 | r7 & res7 | res7 & (~d7))
        #CPC
        elif opcstr == "cpc":
            #calculo del resultado
            res = self.ram[d] - self.ram[r] - self.get_flag(7)

            #calculo de h
            d3 = self.get_bit(self.ram[d], 3)
            r3 = self.get_bit(self.ram[r], 3)
            res3 = self.get_bit(res, 3)

            self.set_flag(self.H, (~d3) & r3 | r3 & res3 | res3 & (~d3))

            #calculo de v
            d7 = self.get_bit(self.ram[d], 7)
            r7 = self.get_bit(self.ram[r], 7)
            res7 = self.get_bit(res, 7)

            self.set_flag(self.V, d7 & (~r7) & (~res7) | (~d7) & r7 & res7)

            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))

            #calculo de s
            self.set_flag(self.S, self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff == 0:
                self.set_flag(self.Z,1)
            else:
                self.set_flag(self.Z,0)

            #calculo de c
            d7 = self.get_bit(self.ram[d], 7)
            r7 = self.get_bit(self.ram[r], 7)
            res7 = self.get_bit(res, 7)

            self.set_flag(self.C, (~d7) & r7 | r7 & res7 | res7 & (~d7))
        #CPSE
        elif opcstr == "cpse":
            #calculo del resultado
            if self.ram[d] == self.ram[r]:
                opc = self.flash.get_word(self.pc)
                entry = self.find_opcode(opc)
                if entry.opcstr[0] == "!":
                    self.pc += 4        #Saltar una instruccion
                else:
                    self.pc +=2
        #EOR
        elif opcstr == "eor":
            #calculo del resultado
            res = self.ram[r] ^ self.ram[d]
            
            #calculo de v
            self.set_flag(self.V,0)
            
            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))

            #calculo de s
            self.set_flag(self.S,self.get_flag(self.N) ^ self.get_flag(self.V))
            
            #calculo de z
            if res & 0xff == 0:
                self.set_flag(self.Z,1)
            else:
                self.set_flag(self.Z,0)
            
            #guardado del resultado en el registro
            self.ram[d] = res & 0xff
        #MOV
        elif opcstr == "mov":
            #calculo del resultado
            self.ram[d] = self.ram[r]
        #OR
        elif opcstr == "or":
            #calculo del resultado
            res = self.ram[r] | self.ram[d]

            #calculo de v
            self.set_flag(self.V,0)
            
            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))
            
            #calculo de s
            self.set_flag(self.S,self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff == 0:
                self.set_flag(self.Z,1)
            else:
                self.set_flag(self.Z,0)
    
            #guardado del resultado en el registro
            self.ram[d] = res & 0xff
        #SBC
        elif opcstr == "sbc":
            #calculo del resultado
            res = self.ram[d] - self.ram[r] - self.get_flag(7)

            #calculo de h
            d3 = self.get_bit(self.ram[d], 3)
            r3 = self.get_bit(self.ram[r], 3)
            res3 = self.get_bit(res, 3)

            self.set_flag(self.H, (~d3) & r3 | r3 & res3 | res3 & (~d3))

            #calculo de v
            d7 = self.get_bit(self.ram[d], 7) 
            r7 = self.get_bit(self.ram[r], 7)
            res7 = self.get_bit(res, 7)
    
            self.set_flag(self.V, d7 & (~r7) & (~res7) | (~d7) & r7 & res7)

            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))

            #calculo de s
            self.set_flag(self.S,self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff != 0:
                self.set_flag(self.Z, 0)
            
            #calculo de c
            d7 = self.get_bit(self.ram[d], 7) 
            r7 = self.get_bit(self.ram[r], 7)
            res7 = self.get_bit(res, 7)

            self.set_flag(self.C, (~d7) & r7 | r7 & res7 | res7 & (~d7))

            #guardado del resultado en el registro
            self.ram[d] = res & 0xff
        #SUB
        elif opcstr == "sub":
            #calculo del resultado
            res = self.ram[d] - self.ram[r]

            #calculo de h
            d3 = self.get_bit(self.ram[d], 3) 
            r3 = self.get_bit(self.ram[r], 3)
            res3 = self.get_bit(res, 3)
    
            self.set_flag(self.H, (~d3) & r3 | r3 & res3 | res3 & (~d3))

            #calculo de v
            d7 = self.get_bit(self.ram[d], 7)
            r7 = self.get_bit(self.ram[r], 7)
            res7 = self.get_bit(res, 7)

            self.set_flag(self.V, d7 & (~r7) & (~res7) | (~d7) & r7 & res7)

            #calculo de n
            self.set_flag(self.N,self.get_bit(res, 7))

            #calculo de s
            self.set_flag(self.S,self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff == 0:
                self.set_flag(self.Z,1)
            else:
                self.set_flag(self.Z,0)
                
            #calculo de c
            d7 = self.get_bit(self.ram[d], 7)
            r7 = self.get_bit(self.ram[r], 7)
            res7 = self.get_bit(res, 7)

            self.set_flag(self.C, (~d7) & r7 | r7 & res7 | res7 & (~d7))

            #guardado del resultado en el registro
            self.ram[d] = res & 0xff
            
    #GRUPO N
    def f_reg3_reg3(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg4_reg4(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg4(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg_x(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg_mx(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg_xp(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg_y(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg_yp(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg_my(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg_yo(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg_z(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg_zp(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg_mz(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg_zo(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg_io(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_x_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_xp_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_mx_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_y_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_yp_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_my_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_yo_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_z_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_zp_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_mz_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_zo_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_dreg_imm(self, opcstr, opd_dict):
        d = opd_dict["d"][0]*2+24
        k = opd_dict["K"][0]

        #ADIW
        if opcstr == "adiw":
            #calculo del resultado
            res = self.ram[d] + k
            res1 = self.ram[d+1] + k
            
            #calculo de v
            dh7 = self.get_bit(self.ram[d+1], 7)
            r15 = self.get_bit(res1, 7)
            self.set_flag(self.V, ~dh7 & r15)

            #calculo de n
            self.set_flag(self.N, r15)

            #calculo de s
            self.set_flag(self.S, self.get_flag(self.N) ^ self.get_flag(self.V))

            #calculo de z
            if res & 0xff == 0 and res1 & 0xff == 0:
                self.set_flag(self.Z,1)
            else:
                self.set_flag(self.Z,0)

            #calculo de c
            self.set_flag(self.C, ~r15 & dh7)

            #guardado del resultado
            self.ram[d] = res  & 0xff
            self.ram[d+1] = res1  & 0xff
            
    #GRUPO N
    def f_dreg_dreg(self, opcstr, opd_dict):
        d = opd_dict["d"][0]*2
        r = opd_dict["r"][0]*2

        #MOVW
        if opcstr == "movw":
            #calculo del resultado
            self.ram[d] = self.ram[r]
            self.ram[d+1] = self.ram[r+1]

    #GRUPO N
    def f_rel_add(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_rel_add12(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_add17(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_bit_rel(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_no_opd(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_io_bit(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_io_reg(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_reg8_reg8(self, opcstr, opd_dict):
        pass

    #GRUPO N
    def f_just_zp(self, opcstr, opd_dict):
        pass

    #Grupos:
    #   1: Gomez-Pereyra
    #   2: Garijo-Perez
    #   3: Gueler-
    #   4:
    opcodes = (
        #A
        OPC(0xfc00, 0x1c00, "adc",    "r4d5r1",     reg_reg,    f_reg_reg),     # 1
        OPC(0xfc00, 0x0c00, "add",    "r4d5r1",     reg_reg,    f_reg_reg),     # 1
        OPC(0xff00, 0x9600, "adiw",   "K4d2K2",     dreg_imm,   f_dreg_imm),    # 1
        OPC(0xfc00, 0x2000, "and",    "r4d5r1",     reg_reg,    f_reg_reg),     # 1
        OPC(0xf000, 0x7000, "andi",   "K4d4K4",     reg8_imm,   f_reg8_imm),    # 1
        OPC(0xfe0f, 0x9405, "asr",    "-4d5",       reg,        f_reg),         # 3

        #B @12
        #OPC(0xff8f, 0x9488, "bclr",   "-4s3",      bit,        f_bit),
        OPC(0xfe08, 0xf800, "bld",    "b3-1d5",     reg_bit,    f_reg_bit),     # 4
        #OPC(0xfc00, 0xf400, "brbc",   "s3k7",      bit_rel,    f_bit_rel),
        #OPC(0xfc00, 0xf000, "brbs",   "s3k7",      bit_rel,    f_bit_rel),
        OPC(0xfc07, 0xf400, "brcc",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf000, "brcs",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xffff, 0x9598, "break",  "",           no_opd,     f_no_opd),      # 2
        OPC(0xfc07, 0xf001, "breq",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf404, "brge",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf405, "brhc",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf005, "brhs",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf407, "brid",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf007, "brie",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf000, "brlo",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf004, "brlt",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf002, "brmi",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf401, "brne",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf402, "brpl",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf400, "brsh",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf406, "brtc",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf006, "brts",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf403, "brvc",   "-3k7",       rel_add,    f_rel_add),     # 4
        OPC(0xfc07, 0xf003, "brvs",   "-3k7",       rel_add,    f_rel_add),     # 4
        #OPC(0xff8f, 0x9408, "bset",   "-4s3",      bit,        f_bit),
        OPC(0xfe08, 0xfa00, "bst",    "b3-1d5",     reg_bit,    f_reg_bit),     # 4

        #C
        OPC(0xfe0e, 0x940e, "call",   "!k17-3k5",   add17,      f_add17),       # 2
        OPC(0xff00, 0x9800, "cbi",    "b3A5",       io_bit,     f_io_bit),      # 4
        OPC(0xffff, 0x9488, "clc",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xffff, 0x94d8, "clh",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xffff, 0x94f8, "cli",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xffff, 0x94a8, "cln",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xfc00, 0x2400, "clr",    "r4d5r1",     reg,        f_reg),         # 2
        OPC(0xffff, 0x94c8, "cls",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xffff, 0x94e8, "clt",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xffff, 0x94b8, "clv",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xffff, 0x9498, "clz",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xfe0f, 0x9400, "com",    "-4d5",       reg,        f_reg),
        OPC(0xfe00, 0x1400, "cp",     "r4d5r1",     reg_reg,    f_reg_reg),     # 1
        OPC(0xfc00, 0x0400, "cpc",    "r4d5r1",     reg_reg,    f_reg_reg),     # 1
        OPC(0xf000, 0x3000, "cpi",    "K4d4K4",     reg8_imm,   f_reg8_imm),    # 1
        OPC(0xfc00, 0x1000, "cpse",   "r4d5r1",     reg_reg,    f_reg_reg),     # 1

        #D
        OPC(0xfe0f, 0x940a, "dec",    "-4d5",       reg,        f_reg),         # 3
        OPC(0xff0f, 0x940b, "des",    "-4K4",       imm_4,      f_imm_4),       # 3

        #E
        OPC(0xffff, 0x9519, "eicall", "",           no_opd,     f_no_opd),      # 2
        OPC(0xffff, 0x9419, "eijmp",  "",           no_opd,     f_no_opd),      # 2
        OPC(0xffff, 0x95d8, "elpm",   "",           no_opd,     f_no_opd),      # 2
        OPC(0xfe0f, 0x9006, "elpm",   "-4d5",       reg_z,      f_reg_z),       # 2
        OPC(0xfe0f, 0x9007, "elpm",   "-4d5",       reg_zp,     f_reg_zp),      # 2
        OPC(0xfc00, 0x2400, "eor",    "r4d5r1",     reg_reg,    f_reg_reg),     # 1

        #F
        OPC(0xff88, 0x0308, "fmul",   "r3-1d3",     reg8_reg8,  f_reg8_reg8),   # 3
        OPC(0xff88, 0x0380, "fmuls",  "r3-1d3",     reg8_reg8,  f_reg8_reg8),   # 3
        OPC(0xff88, 0x0388, "fmulsu", "r3-1d3",     reg8_reg8,  f_reg8_reg8),   # 3

        #G - No hay

        #H - No hay

        #I
        OPC(0xffff, 0x9509, "icall",  "",           no_opd,     f_no_opd),      # 2
        OPC(0xffff, 0x9409, "ijmp",   "",           no_opd,     f_no_opd),      # 2
        OPC(0xf800, 0xb000, "in",     "A4d5A2",     reg_io,     f_reg_io),      # 3
        OPC(0xfe0f, 0x9403, "inc",    "-4d5",       reg,        f_reg),         # 3

        #J
        OPC(0xfe0e, 0x940c, "jmp",    "!k17-3k5",   add17,      f_add17),       # 2

        #K - No hay

        #L
        OPC(0xfe0f, 0x9206, "lac",    "-4r5",       z_reg,      f_z_reg),
        OPC(0xfe0f, 0x9205, "las",    "-4r5",       z_reg,      f_z_reg),
        OPC(0xfe0f, 0x9207, "lat",    "-4r5",       z_reg,      f_z_reg),
        OPC(0xfe0f, 0x900c, "ld",     "-4d5",       reg_x,      f_reg_x),
        OPC(0xfe0f, 0x900d, "ld",     "-4d5",       reg_xp,     f_reg_xp),
        OPC(0xfe0f, 0x900e, "ld",     "-4d5",       reg_mx,     f_reg_mx),
        OPC(0xfe0f, 0x900c, "ld",     "-4d5",       reg_x,      f_reg_x),
        OPC(0xfe0f, 0x900d, "ld",     "-4d5",       reg_xp,     f_reg_xp),
        OPC(0xfe0f, 0x900e, "ld",     "-4d5",       reg_mx,     f_reg_mx),
        OPC(0xfe0f, 0x8008, "ld",     "-4d5",       reg_y,      f_reg_y),
        OPC(0xfe0f, 0x9009, "ld",     "-4d5",       reg_yp,     f_reg_yp),
        OPC(0xfe0f, 0x900a, "ld",     "-4d5",       reg_my,     f_reg_my),
        OPC(0xd208, 0x8008, "ldd",    "q3-1d5-1q2-1q1", reg_yo, f_reg_yo),
        OPC(0xfe0f, 0x8000, "ld",     "-4d5",       reg_z,      f_reg_z),
        OPC(0xfe0f, 0x9001, "ld",     "-4d5",       reg_zp,     f_reg_zp),
        OPC(0xfe0f, 0x9002, "ld",     "-4d5",       reg_mz,     f_reg_mz),
        OPC(0xd208, 0x8000, "ldd",    "q3-1d5-1q2-1q1", reg_zo, f_reg_zo),
        OPC(0xf000, 0xe000, "ldi",    "K4d4K4",     reg8_imm,   f_reg8_imm),
        OPC(0xfe0f, 0x9000, "lds",    "!k16-4d5",   reg_imm16,  f_reg_imm16),
        OPC(0xffff, 0x95c8, "lpm",    "",           no_opd,     f_no_opd),
        OPC(0xfe0f, 0x9004, "lpm",    "-4d5",       reg_z,      f_reg_z),
        OPC(0xfe0f, 0x9005, "lpm",    "-4d5",       reg_zp,     f_reg_zp),
        OPC(0xfc00, 0x0c00, "lsl",    "r4d5r1",     reg,        f_reg),         # 3
        OPC(0xfe0f, 0x9406, "lsr",    "-4d5",       reg,        f_reg),         # 3

        #M
        OPC(0xfc00, 0x2c00, "mov",    "r4d5r1",     reg_reg,    f_reg_reg),     # 1
        OPC(0xff00, 0x0100, "movw",   "r4d4",       dreg_dreg,  f_dreg_dreg),   # 1
        OPC(0xfc00, 0x9c00, "mul",    "r4d5r1",     reg_reg,    f_reg_reg),     # 3
        OPC(0xff00, 0x0200, "muls",   "r4d4",       reg4_reg4,  f_reg4_reg4),   # 3
        OPC(0xff88, 0x0300, "mulsu",  "r3-1d3",     reg3_reg3,  f_reg3_reg3),   # 3

        #N
        OPC(0xfe0f, 0x9401, "neg",    "-4d5",       reg,        f_reg),         # 3
        OPC(0xffff, 0x0000, "nop",    "",           no_opd,     f_no_opd),      # 2

        #O
        OPC(0xfc00, 0x2800, "or",     "r4d5r1",     reg_reg,    f_reg_reg),     # 1
        OPC(0xf000, 0x6000, "ori",    "K4d4K4",     reg8_imm,   f_reg8_imm),    # 1
        OPC(0xf800, 0xb800, "out",    "A4r5A2",     io_reg,     f_io_reg),      # 3

        #P
        OPC(0xfe0f, 0x900f, "pop",    "-4d5",       reg,        f_reg),         # 2
        OPC(0xfe0f, 0x920f, "push",   "-4d5",       reg,        f_reg),         # 2

        #Q - No hay

        #R
        OPC(0xf000, 0xd000, "rcall",  "k12",        rel_add12,  f_rel_add12),   # 2
        OPC(0xffff, 0x9508, "ret",    "",           no_opd,     f_no_opd),      # 2
        OPC(0xffff, 0x9518, "reti",   "",           no_opd,     f_no_opd),      # 2
        OPC(0xf000, 0xc000, "rjmp",   "k12",        rel_add12,  f_rel_add12),   # 2
        OPC(0xfc00, 0x1c00, "rol",    "r4d5r1",     reg,        f_reg),         # 3
        OPC(0xfe0f, 0x9407, "ror",    "-4d5",       reg,        f_reg),         # 3

        #S - en proceso
        OPC(0xfc00, 0x0800, "sbc",    "r4d5r1",     reg_reg,    f_reg_reg),     # 1
        OPC(0xf000, 0x4000, "sbci",   "K4d4K4",     reg8_imm,   f_reg8_imm),    # 1
        OPC(0xff00, 0x9a00, "sbi",    "b3A5",       io_bit,     f_io_bit),      # 4
        OPC(0xff00, 0x9900, "sbic",   "b3A5",       io_bit,     f_io_bit),      # 4
        OPC(0xff00, 0x9b00, "sbis",   "b3A5",       io_bit,     f_io_bit),      # 4
        OPC(0xff00, 0x9700, "sbiw",   "K4d2K2",     dreg_imm,   f_dreg_imm),    # 4
        OPC(0xf000, 0x6000, "sbr",    "K4d4K4",     reg_imm,    f_reg_imm),     # 4
        OPC(0xfe00, 0xfc00, "sbrc",   "b3-1d5",     reg_bit,    f_reg_bit),     # 4
        OPC(0xfe08, 0xfe00, "sbrs",   "b3-1d5",     reg_bit,    f_reg_bit),     # 4
        OPC(0xffff, 0x9408, "sec",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xffff, 0x9458, "seh",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xffff, 0x9478, "sei",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xffff, 0x9428, "sen",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xff0f, 0xef0f, "ser",    "-4d4",       reg4,       f_reg4),
        OPC(0xffff, 0x9448, "ses",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xffff, 0x9468, "set",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xffff, 0x9438, "sev",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xffff, 0x9418, "sez",    "",           no_opd,     f_no_opd),      # 4
        OPC(0xffff, 0x9588, "sleep",  "",           no_opd,     f_no_opd),      # 2
        OPC(0xffff, 0x95e8, "spm",    "",           no_opd,     f_no_opd),
        OPC(0xffff, 0x95f8, "spm",    "",           just_zp,    f_just_zp),
        OPC(0xfe0f, 0x920c, "st",     "-4r5",       x_reg,      f_x_reg),
        OPC(0xfe0f, 0x920d, "st",     "-4r5",       xp_reg,     f_xp_reg),
        OPC(0xfe0f, 0x920e, "st",     "-4r5",       mx_reg,     f_mx_reg),
        OPC(0xfe0f, 0x8208, "st",     "-4r5",       y_reg,      f_y_reg),
        OPC(0xfe0f, 0x9209, "st",     "-4r5",       yp_reg,     f_yp_reg),
        OPC(0xfe0f, 0x920a, "st",     "-4r5",       my_reg,     f_my_reg),
        OPC(0xd208, 0x8208, "std",    "q3-1r5-1q2-1q1", yo_reg, f_yo_reg),
        OPC(0xfe0f, 0x8200, "st",     "-4d5",       z_reg,      f_z_reg),
        OPC(0xfe0f, 0x9201, "st",     "-4d5",       zp_reg,     f_zp_reg),
        OPC(0xfe0f, 0x9202, "st",     "-4d5",       mz_reg,     f_mz_reg),
        OPC(0xd208, 0x8200, "std",    "q3-1d5-1q2-1q1", zo_reg, f_zo_reg),
        OPC(0xfe0f, 0x9200, "sts",    "!k16-4d5",   imm16_reg,  f_imm16_reg),
        OPC(0xf800, 0xa800, "sts",    "k4d4k3",     imm7_reg,   f_imm7_reg),
        OPC(0xfc00, 0x1800, "sub",    "r4d5r1",     reg_reg,    f_reg_reg),     # 1
        OPC(0xf000, 0x5000, "subi",   "K4d4K4",     reg8_imm,   f_reg8_imm),    # 3
        OPC(0xfe0f, 0x9402, "swap",   "-4d5",       reg,        f_reg),         # 2

        #T
        OPC(0xfc00, 0x2000, "tst",    "r4d5r1",     reg,        f_reg),         # 1

        #U - No hay

        #V - No hay

        #W
        OPC(0xffff, 0x95a8, "wdr",    "",           no_opd,     f_no_opd),      # 2

        #X
        #~ OPC(0xfe0f, 0x9204, "xch",    "-4d5",    reg,        f_reg)    # Not for atmega328

        # Y - No hay

        # Z - No hay
    )

    def __init__(self, symtable):
        self.flash = Memory(32768, Memory.FLASH)
        self.symtable = symtable
        self.pc = 0
        self.sp = 0x7fff
        self.ram = [0] * 32
        self.flags = 0

    def get_bit(self, reg, bit):
        return (reg >> bit) & 0x01

    def get_flag(self, flag):
        return self.get_bit(self.flags, flag)

    def set_flag(self, flag , value):
        if value == 1:
            self.flags = self.flags | (1 << flag)
        else:
            self.flags = self.flags & (~(1 << flag))

    def reset(self):
        self.pc = 0
        self.sp = 0x7fff
        self.flags = 0

    def load_flash(self, fname):
        self.flash.load_intel_hex(fname)


    def find_opcode(self, opc):
        for entry in self.opcodes:
            if (opc & entry.mask) == entry.remainder:
                break
        else:
            print("Instruccion no decodificada: {:04x}".format(opc))
            return None
        return entry


    def decode_operands(self, entry, pc, opc):
        opd_dict = {"pc": pc}   # para calcular direcciones relativas
        cmd = entry.opdcmd
        if (cmd != "") and (cmd[0] == '!'):             # Instruccion de 32 bits?
            opc = (opc << 16) | self.flash.get_word(pc)
            cmd = cmd[1:]
            pc += 2
                                                        # Ej.: r4d5r1 (para ADC)
                                                        # decodificar 0x1da5
        while cmd != "":                                #  paso 1  paso 2  paso 3
            r = re.match("([a-zA-Z-])(\d+)", cmd)       #  r, 4    d, 5    r, 1
            if r == None:
                print("error en expresion en la table")
            field_name = r.group(1)                     #  r       d       r
            field_len = int(r.group(2))                 #  4       5       1

            if field_name not in opd_dict:
                opd_dict[field_name] = [0, 0]
            step = opd_dict[field_name]

            temp = opc & (1 << field_len) - 1           #  5       26      0
            opc >>= field_len                           #  0x01da  0x000e  0x0007
            step[0] |= temp << step[1]                  #  [r]=5   [d]=26  [r]=5
            step[1] += field_len                        #  4       5       5

            cmd = cmd[len(r.group(0)):]                 #  r4d5r1  d5r1    r1
                                                        #  ->d5r1  -> r1   -> ""

        return opd_dict


    def disassemble_one_instruction(self, pc, symtable = None):
        opc = self.flash.get_word(pc)
        pc += 2
        if opc == None:
            return None

        entry = self.find_opcode(opc)
        if entry == None:
            return None

        opd_dict = self.decode_operands(entry, pc, opc)

        s= "{:8s}{:8s}".format("", entry.opcstr)
        if entry.fmt in [Atmega328.add17, Atmega328.rel_add, Atmega328.rel_add12]:
            sym = int(entry.fmt(opd_dict, self), 0)
            self.symtable.add(self.symtable.create_label(sym), sym)
            s += "{:s}".format(self.symtable.create_label(sym))
        else:
            s += entry.fmt(opd_dict, self)
        return (s, pc)


    def single_step(self, pc = None, symtable = None):
        if pc != None:
            self.pc = pc

        opc = self.flash.get_word(self.pc)
        self.pc += 2
        if opc == None:
            return None

        entry = self.find_opcode(opc)
        if entry == None:
            return None

        opd_dict = self.decode_operands(entry, pc, opc)

        entry.sim_instr(self, entry.opcstr, opd_dict)


#Clase para probar simulacion
class Test():
    def __init__(self):
        #Instanciar cpu a probar
        self.cpu = Atmega328(None)
        #Cargar instrucciones a probar en memoria
        self.cpu.flash.load_intel_hex("validate_hex.hex")

        #Tabla de valores esperados
        #Partimos de flags en 0 y los registros en 0
        #(Instruccion, Reg1, ValorInicial1, ValorEsperado1, Reg2, ValorInicial2, ValorEsperado2, Banderas, PCIni, SPIni, PCFin, SPFin)
        self.compare = (("tst", 11, 0x01, 0x01, None, None, None, 0b0000010, 0x0114, 0x7fff, 0x0116, 0x7fff),
                        ("sub", 7, 0x01, 0x00, 8, 0x01, 0x01, 0b00000010, 0x010e, 0x7fff, 0x0110, 0x7fff),
                        ("sbci", 16, 34, 0x00, None, None, None, 0b00000000, 0x00cc, 0x7fff, 0x00ce, 0x7fff),
                        ("sbc", 4, 0x01, 0x00, 5, 0x01, 0x01, 0b00000000, 0x00ca, 0x7fff, 0x00cc, 0x7fff),
                        ("ori", 16, 0x01, 0x81, None, None, None, 0b00000100, 0x00b6, 0x7fff, 0x00b8, 0x7fff),
                        ("or", 16, 0x01, 0x81, 17, 0x80, 0x80, 0b00000100, 0x00b4, 0x7fff, 0x00b6, 0x7fff),
                        ("movw", 4,0x00, 0x01, 8, 0x01, 0x01, 0b00000000, 0x00a8, 0x7fff, 0x00aa, 0x7fff),        #OJO: No probamos que se cambien los dos pares
                        ("mov", 31, 0x00, 0x01, 1, 0x01, 0x01, 0b00000000, 0x00a6, 0x7fff, 0x00a8, 0x7fff),
                        ("eor", 4, 0x00, 0x80, 14, 0x80, 0x80, 0b00000100, 0x006c, 0x7fff, 0x006e, 0x7fff))


    def run(self):

        for test in self.compare:
            print("Instruccion: ", test[0])
            #Colocar PC
            self.cpu.pc = test[8]
            #Obtener el opc
            opc = self.cpu.flash.get_word(self.cpu.pc)

            entry = self.cpu.find_opcode(opc)
            opd_dict = self.cpu.decode_operands(entry, test[8], opc)

            #Ejecutar la instruccion
            self.cpu.flags = 0
            self.cpu.ram[test[1]] = test[2]
            if test[4] is not None:
                self.cpu.ram[test[4]] = test[5]
            entry.sim_instr(self.cpu, entry, opd_dict)

            #Verificar resultado
            print("Estado registros: ")
            if self.cpu.ram[test[1]] == test[3] :
                if test[4] is not None:
                    if self.cpu.ram[test[4]] == test[6]:
                        print("    Correcto.")
                    else:
                        print("    Error, r", test[4], " != r", test[4], " (", self.cpu.ram[test[4]],"!=", test[6], ")")
            else:
                print("    Error, r", test[1], " != r", test[1], " (", self.cpu.ram[test[1]],"!=", test[3], ")")
            print("Estado banderas: ")
            if test[7] == self.cpu.flags:
                print("    Correcto")
            else:
                print("    Error, ", self.cpu.flags," !=", test[7])
            print("Estado PC:")
            if self.cpu.pc == test[10]:
                print("    Correcto")
            else:
                print("Error, PC(", self.cpu.pc,") != ", test[10])
            print("Estado SP:")
            if self.cpu.sp == test[11]:
                print("    Correcto")
            else:
                print("Error, SP(", self.cpu.sp,") != ", test[11])


def main(args):
    #Correr test 9 ultimas instrucciones
    test = Test()
    test.run()

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
