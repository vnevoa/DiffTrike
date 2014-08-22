EESchema Schematic File Version 2  date 22.8.2014 9:11:08
LIBS:ed,conn,linear,contrib,.\bridge-ctrller.cache
EELAYER 24  0
EELAYER END
$Descr A4 11700 8267
Sheet 1 1
Title ""
Date "20 oct 2011"
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text Notes 6850 3800 0    20   ~ 0
pci
Text Notes 5250 3750 0    20   ~ 0
pci
Text Notes 5150 3650 0    20   ~ 0
pci
Text Notes 5150 3550 0    20   ~ 0
pci
Text Notes 6700 3900 0    20   ~ 0
pci
Text Label 6850 6600 0    39   ~ 0
NC1
Text Label 5450 3750 2    39   ~ 0
NC1
Wire Wire Line
	5550 3750 5450 3750
Wire Wire Line
	7150 5250 6850 5250
Wire Wire Line
	6950 5050 6950 5150
Wire Wire Line
	6950 5150 6850 5150
Wire Wire Line
	8050 5450 8050 5350
Wire Wire Line
	8050 5350 7950 5350
Wire Wire Line
	6750 3350 7400 3350
Wire Wire Line
	7150 3250 6750 3250
Wire Wire Line
	5450 5100 5100 5100
Wire Wire Line
	5450 5300 5100 5300
Connection ~ 8200 3950
Wire Wire Line
	8550 3900 8550 3950
Wire Wire Line
	8550 3950 7850 3950
Connection ~ 8200 3650
Wire Wire Line
	8550 3700 8550 3650
Wire Wire Line
	1800 3650 2000 3650
Wire Wire Line
	1800 3950 2000 3950
Wire Wire Line
	1800 4050 1900 4050
Wire Wire Line
	1900 4050 1900 4150
Connection ~ 7850 3650
Wire Wire Line
	7850 3900 7850 4000
Wire Wire Line
	6250 2200 6100 2200
Wire Wire Line
	5100 3850 5550 3850
Wire Wire Line
	5450 3350 5550 3350
Wire Wire Line
	5050 3450 5550 3450
Wire Wire Line
	6750 3050 6850 3050
Wire Wire Line
	5550 3650 5450 3650
Wire Wire Line
	5450 3250 5550 3250
Wire Wire Line
	5450 3050 5550 3050
Wire Wire Line
	7100 3850 6750 3850
Wire Wire Line
	7450 4000 7450 3850
Wire Wire Line
	7450 3850 7300 3850
Wire Wire Line
	7450 4200 7450 4300
Wire Wire Line
	6750 3550 6850 3550
Wire Wire Line
	5450 2950 5550 2950
Wire Wire Line
	5450 3150 5550 3150
Wire Wire Line
	5450 3550 5550 3550
Wire Wire Line
	6750 2950 6850 2950
Wire Wire Line
	6750 3150 6850 3150
Wire Wire Line
	6750 3450 6850 3450
Wire Wire Line
	4800 3850 4900 3850
Wire Wire Line
	6450 2200 6600 2200
Wire Wire Line
	6600 2200 6600 2300
Wire Wire Line
	7850 3600 7850 3700
Wire Wire Line
	7850 3400 7850 3300
Wire Wire Line
	1800 3850 2000 3850
Wire Wire Line
	8200 3700 8200 3650
Wire Wire Line
	8200 3900 8200 3950
Connection ~ 7850 3950
Wire Wire Line
	5100 5500 5250 5500
Wire Wire Line
	5250 5500 5250 5600
Wire Wire Line
	5450 5400 5100 5400
Wire Wire Line
	5450 5200 5100 5200
Wire Wire Line
	7350 3250 7400 3250
Connection ~ 7400 3350
Wire Wire Line
	7400 3250 7400 3450
Wire Wire Line
	6850 5350 6950 5350
Wire Wire Line
	6950 5350 6950 5450
Wire Wire Line
	7950 5150 8050 5150
Wire Wire Line
	8050 5150 8050 5050
Wire Wire Line
	8250 5250 7950 5250
Wire Wire Line
	7350 3650 6750 3650
Wire Wire Line
	8550 3650 7550 3650
Wire Wire Line
	6750 3750 6850 3750
Wire Wire Line
	1800 3150 1900 3150
Wire Wire Line
	1900 3150 1900 3250
Wire Wire Line
	1800 2950 2000 2950
Wire Wire Line
	2750 3750 2600 3750
Wire Wire Line
	2950 3750 3100 3750
Wire Wire Line
	3100 3750 3100 3850
Wire Wire Line
	5250 6750 5250 6650
Wire Wire Line
	5250 6650 5150 6650
Wire Wire Line
	5150 6450 5250 6450
Wire Wire Line
	5250 6450 5250 6350
Wire Wire Line
	5450 6550 5150 6550
Wire Wire Line
	6850 6600 6850 6500
Wire Wire Line
	6850 6500 6750 6500
Wire Wire Line
	6750 6300 6850 6300
Wire Wire Line
	6850 6300 6850 6200
Wire Wire Line
	7050 6400 6750 6400
Text Label 6850 6200 0    39   ~ 0
HB1_H
Text Label 7050 6400 2    39   ~ 0
HB2_H
$Comp
L CONN_3 J8
U 1 1 53C71731
P 6550 6400
F 0 "J8" H 6550 6400 40  0000 C CNN
F 1 "HB_H" H 6550 6600 40  0000 C CNN
	1    6550 6400
	-1   0    0    -1  
$EndComp
Text Label 5250 6750 0    39   ~ 0
+5V
Text Label 5250 6350 0    39   ~ 0
Isns
Text Label 5450 6550 2    39   ~ 0
OCA
$Comp
L CONN_3 J7
U 1 1 53C7165B
P 4950 6550
F 0 "J7" H 4950 6550 40  0000 C CNN
F 1 "Isns" H 4950 6360 40  0000 C CNN
	1    4950 6550
	-1   0    0    1   
$EndComp
Text Label 2600 3750 2    39   ~ 0
+5V
$Comp
L GND #PWR01
U 1 1 4D5DC3DA
P 3100 3850
F 0 "#PWR01" H 3100 3850 30  0001 C CNN
F 1 "GND" H 3100 3780 30  0001 C CNN
	1    3100 3850
	1    0    0    -1  
$EndComp
$Comp
L CX C1
U 1 1 4D5DC3D9
P 2850 3750
F 0 "C1" H 2900 3830 39  0000 L CNN
F 1 "22u" H 2900 3670 39  0000 L CNN
F 4 "0,14" H 2850 3750 60  0001 C CNN "Cost"
F 5 "ED" H 2850 3750 60  0001 C CNN "Supplier"
	1    2850 3750
	0    1    1    0   
$EndComp
Text Notes 2300 3100 0    39   ~ 0
Motor Power Input, 9V to 30V
Text Label 2000 2950 0    39   ~ 0
Vcc
$Comp
L GND #PWR02
U 1 1 4C5606BB
P 1900 3250
F 0 "#PWR02" H 1900 3250 30  0001 C CNN
F 1 "GND" H 1900 3180 30  0001 C CNN
	1    1900 3250
	1    0    0    -1  
$EndComp
$Comp
L CONN_2 J1
U 1 1 4C56065C
P 1600 3050
F 0 "J1" H 1600 3050 40  0000 C CNN
F 1 "POWER" H 1600 2850 40  0000 C CNN
F 4 "0,5" H 1600 3050 60  0001 C CNN "Cost"
F 5 "ED" H 1600 3050 60  0001 C CNN "Supplier"
	1    1600 3050
	-1   0    0    1   
$EndComp
Text Label 6850 3750 0    39   ~ 0
Isens
Text Notes 6850 2950 0    28   ~ 0
I2C addr selector (2 possible addrs)
NoConn ~ 1800 3750
$Comp
L CONN_5 J2
U 1 1 4D5DE533
P 1600 3850
F 0 "J2" H 1600 3850 40  0000 C CNN
F 1 "CTRL" H 1600 3550 40  0000 C CNN
	1    1600 3850
	-1   0    0    1   
$EndComp
$Comp
L RX R3
U 1 1 4D5DC4E0
P 7450 3650
F 0 "R3" H 7450 3695 43  0000 C BNN
F 1 "3K3" H 7450 3580 43  0000 C CNN
	1    7450 3650
	1    0    0    -1  
$EndComp
Text Notes 7000 5650 0    28   ~ 0
MOSFET temperature sensors
Text Label 6850 3150 0    39   ~ 0
Tsens2
Text Label 6850 3050 0    39   ~ 0
Tsens1
Text Label 8250 5250 2    39   ~ 0
Tsens2
Text Label 7150 5250 2    39   ~ 0
Tsens1
Text Label 8050 5050 0    39   ~ 0
+5V
Text Label 6950 5050 0    39   ~ 0
+5V
$Comp
L GND #PWR03
U 1 1 4C60AAA9
P 8050 5450
F 0 "#PWR03" H 8050 5450 30  0001 C CNN
F 1 "GND" H 8050 5380 30  0001 C CNN
	1    8050 5450
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR04
U 1 1 4C60AA9E
P 6950 5450
F 0 "#PWR04" H 6950 5450 30  0001 C CNN
F 1 "GND" H 6950 5380 30  0001 C CNN
	1    6950 5450
	1    0    0    -1  
$EndComp
$Comp
L CONN_3 J5
U 1 1 4C60AA56
P 7750 5250
F 0 "J5" H 7750 5250 40  0000 C CNN
F 1 "TSENS2" H 7750 5060 40  0000 C CNN
	1    7750 5250
	-1   0    0    1   
$EndComp
$Comp
L CONN_3 J4
U 1 1 4C60AA43
P 6650 5250
F 0 "J4" H 6650 5250 40  0000 C CNN
F 1 "TSENS1" H 6650 5060 40  0000 C CNN
	1    6650 5250
	-1   0    0    1   
$EndComp
Text Notes 8050 3550 0    28   ~ 0
Measure power voltage
$Comp
L CX C3
U 1 1 4C575DA9
P 7250 3250
F 0 "C3" V 7300 3350 39  0000 L CNN
F 1 "100n" V 7300 3100 39  0000 L CNN
F 4 "0,14" H 7250 3250 60  0001 C CNN "Cost"
F 5 "ED" H 7250 3250 60  0001 C CNN "Supplier"
	1    7250 3250
	0    -1   -1   0   
$EndComp
Text Notes 1490 4310 0    39   ~ 0
H-Bridge module control interface
Text Notes 5500 5100 0    28   ~ 0
SCLK
Text Notes 5500 5200 0    28   ~ 0
MISO
Text Notes 5500 5300 0    28   ~ 0
MOSI
Text Label 5450 5100 2    39   ~ 0
SCL
Text Label 5450 5200 2    39   ~ 0
HB1_L
Text Label 5450 5300 2    39   ~ 0
SDA
Text Label 5450 5400 2    39   ~ 0
/RESET
Text Label 5200 3850 0    39   ~ 0
/RESET
$Comp
L GND #PWR05
U 1 1 4C572B3F
P 5250 5600
F 0 "#PWR05" H 5250 5600 30  0001 C CNN
F 1 "GND" H 5250 5530 30  0001 C CNN
	1    5250 5600
	1    0    0    -1  
$EndComp
$Comp
L CONN_5 J3
U 1 1 4C572AD8
P 4900 5300
F 0 "J3" H 4900 5300 40  0000 C CNN
F 1 "ISP" H 4900 5000 40  0000 C CNN
F 4 "0,2" H 4900 5300 60  0001 C CNN "Cost"
F 5 "ED" H 4900 5300 60  0001 C CNN "Supplier"
	1    4900 5300
	-1   0    0    1   
$EndComp
$Comp
L CX C4
U 1 1 4C561571
P 8550 3800
F 0 "C4" H 8600 3880 39  0000 L CNN
F 1 "10n" H 8600 3720 39  0000 L CNN
F 4 "0,12" H 8550 3800 60  0001 C CNN "Cost"
F 5 "ED" H 8550 3800 60  0001 C CNN "Supplier"
	1    8550 3800
	1    0    0    -1  
$EndComp
$Comp
L DIODE_ZENER D2
U 1 1 4C561568
P 8200 3800
F 0 "D2" H 8200 3900 40  0000 C CNN
F 1 "Z5V6" H 8200 3700 40  0000 C CNN
F 4 "0,1" H 8200 3800 60  0001 C CNN "Cost"
F 5 "ED" H 8200 3800 60  0001 C CNN "Supplier"
	1    8200 3800
	0    -1   -1   0   
$EndComp
Text Notes 1500 1150 0    98   ~ 0
H-Bridge Controller Module
Text Notes 10700 7650 0    43   ~ 0
0.1
Text Label 2000 3650 0    39   ~ 0
SCL
Text Label 2000 3850 0    39   ~ 0
SDA
Text Label 2000 3950 0    39   ~ 0
+5V
$Comp
L GND #PWR06
U 1 1 4C5606C2
P 1900 4150
F 0 "#PWR06" H 1900 4150 30  0001 C CNN
F 1 "GND" H 1900 4080 30  0001 C CNN
	1    1900 4150
	1    0    0    -1  
$EndComp
Text Label 7850 3300 0    28   ~ 0
Vcc
$Comp
L GND #PWR07
U 1 1 4C5604FD
P 7850 4000
F 0 "#PWR07" H 7850 4000 30  0001 C CNN
F 1 "GND" H 7850 3930 30  0001 C CNN
	1    7850 4000
	1    0    0    -1  
$EndComp
$Comp
L RX R5
U 1 1 4C5604F5
P 7850 3800
F 0 "R5" H 7850 3845 43  0000 C BNN
F 1 "1K" H 7850 3730 43  0000 C CNN
F 4 "0,01" H 7850 3800 60  0001 C CNN "Cost"
F 5 "ED" H 7850 3800 60  0001 C CNN "Supplier"
	1    7850 3800
	0    1    1    0   
$EndComp
$Comp
L RX R4
U 1 1 4C5604E8
P 7850 3500
F 0 "R4" H 7850 3545 43  0000 C BNN
F 1 "10K" H 7850 3430 43  0000 C CNN
F 4 "0,01" H 7850 3500 60  0001 C CNN "Cost"
F 5 "ED" H 7850 3500 60  0001 C CNN "Supplier"
	1    7850 3500
	0    1    1    0   
$EndComp
Text Notes 5900 2500 0    28   ~ 0
microcontroller decoupling cap
Text Label 6100 2200 2    39   ~ 0
+5V
$Comp
L GND #PWR08
U 1 1 4C560485
P 6600 2300
F 0 "#PWR08" H 6600 2300 30  0001 C CNN
F 1 "GND" H 6600 2230 30  0001 C CNN
	1    6600 2300
	1    0    0    -1  
$EndComp
$Comp
L CX C2
U 1 1 4C56046C
P 6350 2200
F 0 "C2" H 6400 2280 39  0000 L CNN
F 1 "100n" H 6400 2120 39  0000 L CNN
F 4 "0,14" H 6350 2200 60  0001 C CNN "Cost"
F 5 "ED" H 6350 2200 60  0001 C CNN "Supplier"
	1    6350 2200
	0    1    1    0   
$EndComp
NoConn ~ 6850 2950
Text Label 4800 3850 2    39   ~ 0
+5V
$Comp
L RX R1
U 1 1 4C5603EE
P 5000 3850
F 0 "R1" H 5000 3895 43  0000 C BNN
F 1 "22K" H 5000 3780 43  0000 C CNN
F 4 "0,01" H 5000 3850 60  0001 C CNN "Cost"
F 5 "ED" H 5000 3850 60  0001 C CNN "Supplier"
	1    5000 3850
	1    0    0    -1  
$EndComp
Text Label 5450 3350 2    39   ~ 0
+5V
Text Label 6850 3450 0    39   ~ 0
+5V
$Comp
L GND #PWR09
U 1 1 4C560377
P 7400 3450
F 0 "#PWR09" H 7400 3450 30  0001 C CNN
F 1 "GND" H 7400 3380 30  0001 C CNN
	1    7400 3450
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR010
U 1 1 4C56036D
P 5050 3450
F 0 "#PWR010" H 5050 3450 30  0001 C CNN
F 1 "GND" H 5050 3380 30  0001 C CNN
	1    5050 3450
	0    1    1    0   
$EndComp
Text Label 5450 3150 2    39   ~ 0
SCL
Text Label 5450 2950 2    39   ~ 0
SDA
Text Label 5450 3250 2    39   ~ 0
HB2_L
Text Label 5450 3650 2    39   ~ 0
HB2_H
Text Label 5450 3050 2    39   ~ 0
HB1_L
Text Label 5450 3550 2    39   ~ 0
HB1_H
$Comp
L GND #PWR011
U 1 1 4C55FB7E
P 7450 4300
F 0 "#PWR011" H 7450 4300 30  0001 C CNN
F 1 "GND" H 7450 4230 30  0001 C CNN
	1    7450 4300
	1    0    0    -1  
$EndComp
$Comp
L RX R2
U 1 1 4C55FB6E
P 7450 4100
F 0 "R2" H 7450 4145 43  0000 C BNN
F 1 "560" H 7450 4030 43  0000 C CNN
F 4 "0,01" H 7450 4100 60  0001 C CNN "Cost"
F 5 "ED" H 7450 4100 60  0001 C CNN "Supplier"
	1    7450 4100
	0    1    1    0   
$EndComp
$Comp
L LED D1
U 1 1 4C55FB64
P 7200 3850
F 0 "D1" H 7125 3935 40  0000 L CNN
F 1 "LED" H 7200 3760 40  0000 C CNN
F 4 "0,1" H 7200 3850 60  0001 C CNN "Cost"
F 5 "ED" H 7200 3850 60  0001 C CNN "Supplier"
	1    7200 3850
	1    0    0    -1  
$EndComp
Text Label 6850 3650 0    39   ~ 0
VccSens
Text Label 6850 3550 0    39   ~ 0
OCA
$Comp
L ATTINY26 U1
U 1 1 4C55F7BE
P 6150 3400
F 0 "U1" H 5650 2850 60  0000 L CNN
F 1 "ATTINY26" H 5910 3970 60  0000 C CNN
F 2 "20DIP" H 6525 2860 50  0001 C CNN
F 4 "1,88" H 6150 3400 60  0001 C CNN "Cost"
F 5 "ED" H 6150 3400 60  0001 C CNN "Supplier"
	1    6150 3400
	1    0    0    -1  
$EndComp
Text Notes 7525 7525 0    47   ~ 0
H-Bridge Controller Module
$EndSCHEMATC
