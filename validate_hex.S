#define __SFR_OFFSET 0
#include <avr/io.h>
#include <avr/eeprom.h>

        .text

main:
        adc     r2, r5
        add     r3, r16
        adiw    r26, 0x12
        and     r4, r24
        andi    r18, 0x55
        asr     r7
        
        bclr    5
        bset    7
        bld     r4, 4
        brbc    1, main
        brbs    2, main
        brcc    main
        brcs    main
        break
        breq    main
        brge    main
        brhc    main
        brhs    main
        brid    main
        brie    main
        brlo    main
        brlt    main
        brmi    main
        brne    main
        brpl    main
        brsh    main
        brtc    main
        brts    main
        brvc    main
        brvs    main
        bset    3
        bst     r2, 3

        call    main
        
        cbi     15, 6
        cbr     r25, 0xaa
        clc
        clh
        cli
        cln
        clr     r6
        cls
        clt
        clv
        clz
        com     r13
        cp      r14, r15
        cpc     r14, r15
        cpi     r18, 45
        cpse    r3, r9

        dec     r14
        
        elpm
        elpm    R4, Z
        elpm    R21, Z+
        eor     r4, r14

        fmul    r16, r17
        fmuls   r16, r17
        fmulsu  r17, r18

        icall
        ijmp
        in      r13, 31
        inc     r27

        jmp     main

        ld      r5, X
        ld      r5, X+
        ld      r5, -X

        ld      r6, Y
        ld      r6, Y+
        ld      r6, -Y
        ldd     r6, Y+6

        ld      r6, Z
        ld      r6, Z+
        ld      r6, -Z
        ldd     r6, Z+6

        ldi     r16, 123
        lds     r17, 12345
        lpm
        lpm     r5, Z
        lpm     r4, Z+
        lsl     r7
        lsr     r8

        mov     r31, r1
        movw    r4, r8
        mul     r18, r19
        muls    r20, r21
        mulsu   r22, r23

        neg     r9
        nop

        or      r16, r17
        ori     r16, 0x80
        out     0x31, r8

        pop     r7
        push    r9

        rcall   main
        ret
        reti
        rjmp    main
        ror     r29
        rol     r30

        sbc     r4, r5
        sbci    r16, 34
        sbi     0x14, 6
        sbic    0x14, 5
        sbis    0x14, 3
        sbiw    r24, 45
        sbr     r26, 0x44
        sbrs    r20, 3
        sec
        seh
        sei
        seh
        ser     r29
        ses
        set
        sev
        sez
        sleep
        spm     Z+
        st      X, r4
        st      X+, r4
        st      -X, R4
        st      Y, r4
        st      Y+, r4
        st      -Y, R4
        std     Y+4, R4
        st      Z, r4
        st      Z+, r4
        st      -Z, R4
        std     Z+4, R4
        sts     0x12345, r6
        sts     0x123, r8
        sub     r7, r8
        subi    r17, 123
        swap    r9

        tst     r11

        wdr

     
        .end
