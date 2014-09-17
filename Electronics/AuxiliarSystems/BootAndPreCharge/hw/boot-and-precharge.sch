EESchema Schematic File Version 2  date 17.9.2014 2:25:53
LIBS:power,.\boot-and-precharge.cache
EELAYER 24  0
EELAYER END
$Descr A4 11700 8267
Sheet 1 1
Title ""
Date "17 sep 2014"
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text Notes 7550 7525 0    43   ~ 0
System boot and power bridges pre-charge
Text Notes 10725 7650 0    43   ~ 0
2
Text Notes 7525 7400 0    43   ~ 0
1  1
Text Notes 4200 1700 0    43   ~ 0
20..30V
Text Notes 6125 3925 0    43   ~ 0
Flip ON/OFF siwtch to OFF
Text Notes 6025 3800 0    43   ~ 10
System turn off:
Text Notes 6125 3650 0    43   ~ 0
Press START
Text Notes 6125 3550 0    43   ~ 0
Flip ON/OFF switch to ON
Text Notes 6025 3425 0    43   ~ 10
System turn ON:
Text Notes 2975 2050 0    39   ~ 0
blade auto fuse
$Comp
L GND #PWR4
U 1 1 5418E052
P 6075 2650
F 0 "#PWR4" H 6075 2650 30  0001 C CNN
F 1 "GND" H 6075 2580 30  0001 C CNN
	1    6075 2650
	1    0    0    -1  
$EndComp
Wire Wire Line
	6075 2650 6075 2275
Wire Wire Line
	6075 2275 5900 2275
Wire Wire Line
	3900 2270 3900 2470
Wire Wire Line
	3900 2470 3900 2570
Wire Wire Line
	6700 4350 6450 4350
Wire Wire Line
	6450 4350 5550 4350
Wire Wire Line
	5550 4350 5300 4350
Wire Wire Line
	5550 3900 5550 3750
Wire Notes Line
	4000 3900 4000 4550
Connection ~ 5550 4350
Connection ~ 4600 3750
Wire Wire Line
	4600 3750 4850 3750
Wire Wire Line
	3350 4300 3500 4300
Wire Wire Line
	4600 5150 4600 4800
Wire Wire Line
	4250 4950 4250 5050
Wire Wire Line
	4250 5050 4150 5050
Wire Wire Line
	4150 5050 4000 5050
Wire Wire Line
	4000 5050 4000 4950
Connection ~ 4000 4700
Wire Wire Line
	4000 4750 4000 4700
Connection ~ 4600 4050
Wire Wire Line
	4600 4050 4400 4050
Wire Wire Line
	4400 4050 4400 4150
Wire Wire Line
	4600 4300 4600 4450
Wire Wire Line
	4600 4450 4600 4600
Wire Wire Line
	3900 3575 3900 3625
Wire Wire Line
	3900 3375 3900 3325
Wire Wire Line
	3900 1770 3900 1670
Connection ~ 5350 2270
Wire Wire Line
	5350 2320 5350 2270
Connection ~ 3900 2470
Connection ~ 5150 2570
Wire Wire Line
	3900 3025 4600 3025
Wire Wire Line
	4600 3025 5150 3025
Wire Wire Line
	5150 3025 5150 2570
Wire Wire Line
	5150 2570 5150 2370
Wire Wire Line
	5150 2370 5100 2370
Wire Wire Line
	3900 2470 4300 2470
Wire Wire Line
	5350 2520 5350 2570
Wire Wire Line
	5350 2570 5150 2570
Wire Wire Line
	5150 2570 5100 2570
Connection ~ 4600 3025
Wire Wire Line
	3900 2850 3900 3025
Wire Wire Line
	3900 3025 3900 3125
Connection ~ 3900 3025
Wire Wire Line
	4600 3025 4600 3250
Wire Wire Line
	4600 3250 4600 3750
Wire Wire Line
	4600 3750 4600 4050
Wire Wire Line
	4600 4050 4600 4200
Wire Wire Line
	5300 4150 5300 3500
Wire Wire Line
	4400 4350 4400 4450
Wire Wire Line
	4400 4450 4600 4450
Connection ~ 4600 4450
Wire Wire Line
	4250 4750 4250 4700
Connection ~ 4250 4700
Wire Wire Line
	4150 5150 4150 5050
Connection ~ 4150 5050
Wire Wire Line
	3700 4300 4000 4700
Wire Wire Line
	4000 4700 4250 4700
Wire Wire Line
	4250 4700 4450 4700
Wire Wire Line
	3150 4300 3050 4300
Wire Wire Line
	3050 4300 3050 4050
Wire Wire Line
	5550 3750 5050 3750
Wire Notes Line
	4000 3900 2950 3900
Wire Notes Line
	2950 3900 2950 4550
Wire Notes Line
	2950 4550 4000 4550
Wire Wire Line
	5100 2270 5350 2270
Wire Wire Line
	5350 2270 5700 2270
Wire Wire Line
	4600 3250 5100 3250
Connection ~ 4600 3250
Wire Wire Line
	5550 4100 5550 4350
Wire Wire Line
	6450 4350 6450 4900
Connection ~ 6450 4350
Wire Wire Line
	6450 4900 6700 4900
Wire Wire Line
	3900 2570 3900 2650
Text Notes 6525 4650 0    39   ~ 0
blade auto fuses
$Comp
L FUSE F3
U 1 1 5418DC58
P 6950 4900
F 0 "F3" H 7050 4950 40  0000 C CNN
F 1 "FUSE" H 6850 4850 40  0000 C CNN
	1    6950 4900
	-1   0    0    1   
$EndComp
$Comp
L FUSE F2
U 1 1 5418DC3C
P 6950 4350
F 0 "F2" H 7050 4400 40  0000 C CNN
F 1 "FUSE" H 6850 4300 40  0000 C CNN
	1    6950 4350
	-1   0    0    1   
$EndComp
Text Notes 5325 2100 0    47   ~ 11
Main ON/OFF switch
$Comp
L SPST SW2
U 1 1 5418DA44
P 5800 2275
F 0 "SW2" H 5800 2355 39  0000 C CNN
F 1 "ON/OFF" H 5800 2205 39  0000 C CNN
	1    5800 2275
	1    0    0    -1  
$EndComp
$Comp
L DIODE D5
U 1 1 4FD4D4D1
P 5550 4000
F 0 "D5" H 5550 4100 40  0000 C CNN
F 1 "1N4148" H 5550 3900 40  0000 C CNN
	1    5550 4000
	0    1    1    0   
$EndComp
Text Notes 4700 3225 0    47   ~ 0
to 5V DC-DC converter
Text Notes 2850 2800 0    47   ~ 11
Press to START
Text Notes 3000 3900 0    47   ~ 0
from main ctrl
Text Notes 5500 4475 0    47   ~ 0
power to bridges
Text Label 5900 4350 0    47   ~ 0
Vpwr
Text Notes 4700 3600 0    47   ~ 0
precharge
$Comp
L RX R4
U 1 1 4F589471
P 4950 3750
F 0 "R4" H 4950 3795 43  0000 C BNN
F 1 "RX" H 4950 3680 43  0000 C CNN
	1    4950 3750
	1    0    0    -1  
$EndComp
$Comp
L RX R1
U 1 1 4F58945B
P 3250 4300
F 0 "R1" H 3250 4345 43  0000 C BNN
F 1 "RX" H 3250 4230 43  0000 C CNN
	1    3250 4300
	1    0    0    -1  
$EndComp
$Comp
L DIODE_SCHOTTKY D1
U 1 1 4F589428
P 3600 4300
F 0 "D1" H 3600 4400 40  0000 C CNN
F 1 "BAT54" H 3600 4200 40  0000 C CNN
	1    3600 4300
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR2
U 1 1 4F58940C
P 4150 5150
F 0 "#PWR2" H 4150 5150 30  0001 C CNN
F 1 "GND" H 4150 5080 30  0001 C CNN
	1    4150 5150
	1    0    0    -1  
$EndComp
$Comp
L CX C1
U 1 1 4F5893F5
P 4250 4850
F 0 "C1" H 4300 4930 39  0000 L CNN
F 1 "CX" H 4300 4770 39  0000 L CNN
	1    4250 4850
	1    0    0    -1  
$EndComp
$Comp
L RX R3
U 1 1 4F5893EB
P 4000 4850
F 0 "R3" H 4000 4895 43  0000 C BNN
F 1 "RX" H 4000 4780 43  0000 C CNN
	1    4000 4850
	0    1    1    0   
$EndComp
$Comp
L GND #PWR3
U 1 1 4F5893E1
P 4600 5150
F 0 "#PWR3" H 4600 5150 30  0001 C CNN
F 1 "GND" H 4600 5080 30  0001 C CNN
	1    4600 5150
	1    0    0    -1  
$EndComp
$Comp
L DIODE D3
U 1 1 4F5893CA
P 4400 4250
F 0 "D3" H 4400 4350 40  0000 C CNN
F 1 "1N4148" H 4400 4150 40  0000 C CNN
	1    4400 4250
	0    -1   -1   0   
$EndComp
Text Label 5300 3500 0    47   ~ 0
VBATF
$Comp
L CONTACTOR K2
U 1 1 4F58937C
P 4950 4250
F 0 "K2" H 4950 4450 47  0000 C CNN
F 1 "RELAY" H 4950 4050 47  0000 C CNN
	1    4950 4250
	1    0    0    -1  
$EndComp
$Comp
L RELAY_1P2S K1
U 1 1 4F588BD7
P 4700 2470
F 0 "K1" H 4650 2770 70  0000 C CNN
F 1 "LATCH" H 4700 2120 55  0000 C CNN
	1    4700 2470
	-1   0    0    1   
$EndComp
$Comp
L NPN_BJT Q1
U 1 1 4F58914B
P 4500 4700
F 0 "Q1" H 4650 4750 47  0000 L CNN
F 1 "NPN_BJT" H 4650 4650 47  0000 L CNN
	1    4500 4700
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR1
U 1 1 4F5890D6
P 3900 3625
F 0 "#PWR1" H 3900 3625 30  0001 C CNN
F 1 "GND" H 3900 3555 30  0001 C CNN
	1    3900 3625
	1    0    0    -1  
$EndComp
$Comp
L RX R2
U 1 1 4F5890CA
P 3900 3475
F 0 "R2" H 3900 3520 43  0000 C BNN
F 1 "RX" H 3900 3405 43  0000 C CNN
	1    3900 3475
	0    1    1    0   
$EndComp
$Comp
L LED D2
U 1 1 4F5890C0
P 3900 3225
F 0 "D2" H 3825 3350 40  0000 L CNN
F 1 "POWER ON" V 3900 2950 40  0000 C CNN
	1    3900 3225
	0    1    1    0   
$EndComp
Text Label 4600 3025 0    47   ~ 0
V+
Text Label 3900 1670 0    47   ~ 0
Vbat
$Comp
L FUSE F1
U 1 1 4F589035
P 3900 2020
F 0 "F1" H 4000 2070 40  0000 C CNN
F 1 "FUSE" H 3800 1970 40  0000 C CNN
	1    3900 2020
	0    1    1    0   
$EndComp
Text Label 3950 2470 0    47   ~ 0
VBATF
$Comp
L DIODE D4
U 1 1 4F588EE1
P 5350 2420
F 0 "D4" H 5350 2520 40  0000 C CNN
F 1 "1N4148" H 5350 2320 40  0000 C CNN
	1    5350 2420
	0    1    1    0   
$EndComp
$Comp
L PB SW1
U 1 1 4F588E3D
P 3900 2750
F 0 "SW1" H 3900 2850 39  0000 C CNN
F 1 "START" H 3910 2680 39  0000 C CNN
	1    3900 2750
	0    -1   -1   0   
$EndComp
NoConn ~ 4300 2670
$EndSCHEMATC
