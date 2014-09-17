EESchema Schematic File Version 2  date 17.9.2014 3:22:59
LIBS:power,device,.\5V-dc-dc-converter.cache
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
Text Notes 3000 1600 0    87   ~ 21
DC-DC converter 5V upto 3A output
Text Notes 7550 7525 0    47   ~ 0
20-30V to 5V DC-DC switching converter
Text Notes 10700 7650 0    47   ~ 0
2
Text Notes 7500 7400 0    47   ~ 0
1  1
Text Notes 3200 2150 0    47   ~ 0
20-30V
Text Notes 7300 2800 0    47   ~ 0
5V
$Comp
L RX R2
U 1 1 5418EB41
P 6750 2600
F 0 "R2" H 6750 2645 43  0000 C BNN
F 1 "10K" H 6750 2530 43  0000 C CNN
	1    6750 2600
	0    1    1    0   
$EndComp
Wire Wire Line
	7150 2450 5600 2450
Connection ~ 6150 3100
Wire Wire Line
	6150 3100 6150 2850
Wire Wire Line
	6150 2450 6150 2650
Connection ~ 6150 2450
Wire Wire Line
	4950 2250 6500 2250
Wire Wire Line
	6500 2250 6500 2750
Wire Wire Line
	6500 2750 6750 2750
Wire Wire Line
	4350 3200 4350 2650
Connection ~ 6750 3100
Wire Wire Line
	7150 2650 7150 3100
Wire Wire Line
	4050 2350 3300 2350
Wire Wire Line
	4650 3100 4650 2650
Connection ~ 4350 3100
Connection ~ 5100 3100
Wire Wire Line
	3700 3100 3700 2850
Connection ~ 5100 2450
Wire Wire Line
	5100 2650 5100 2450
Connection ~ 5700 3100
Wire Wire Line
	5700 3100 5700 2850
Connection ~ 6750 2750
Wire Wire Line
	6750 2700 6750 2850
Wire Wire Line
	6750 2500 6750 2450
Wire Wire Line
	6750 3100 6750 3050
Wire Wire Line
	5100 3100 5100 2850
Wire Wire Line
	5700 2450 5700 2650
Connection ~ 5700 2450
Connection ~ 4650 3100
Wire Wire Line
	5200 2450 4950 2450
Connection ~ 6750 2450
Wire Wire Line
	3300 2550 3300 3100
Connection ~ 3700 3100
Wire Wire Line
	3700 2650 3700 2350
Connection ~ 3700 2350
Wire Wire Line
	3300 3100 7150 3100
$Comp
L CX C3
U 1 1 4D2F8F0D
P 6150 2750
F 0 "C3" H 6200 2830 39  0000 L CNN
F 1 "100nF" H 6200 2670 39  0000 L CNN
	1    6150 2750
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR01
U 1 1 4D2BC181
P 4350 3200
F 0 "#PWR01" H 4350 3200 30  0001 C CNN
F 1 "GND" H 4350 3130 30  0001 C CNN
	1    4350 3200
	1    0    0    -1  
$EndComp
$Comp
L CONN_2 J1
U 1 1 4D2BC149
P 3100 2450
F 0 "J1" H 3100 2450 40  0000 C CNN
F 1 "Vin" H 3100 2260 40  0000 C CNN
	1    3100 2450
	-1   0    0    1   
$EndComp
$Comp
L CONN_2 J2
U 1 1 4D2BC140
P 7350 2550
F 0 "J2" H 7350 2550 40  0000 C CNN
F 1 "Vout" H 7350 2360 40  0000 C CNN
	1    7350 2550
	1    0    0    1   
$EndComp
$Comp
L LX L1
U 1 1 4D2BC11F
P 5400 2450
F 0 "L1" V 5350 2450 40  0000 C CNN
F 1 "100uH" V 5500 2450 40  0000 C CNN
	1    5400 2450
	0    -1   -1   0   
$EndComp
$Comp
L RX R1
U 1 1 4D2BBC19
P 6750 2950
F 0 "R1" H 6750 2995 43  0000 C BNN
F 1 "3K3" H 6750 2880 43  0000 C CNN
	1    6750 2950
	0    1    1    0   
$EndComp
$Comp
L DIODE_SCHOTTKY D1
U 1 1 4D2BBBB3
P 5100 2750
F 0 "D1" H 5100 2850 40  0000 C CNN
F 1 "1N5822" H 5100 2650 40  0000 C CNN
	1    5100 2750
	0    -1   -1   0   
$EndComp
$Comp
L CX C2
U 1 1 4D2BBB91
P 5700 2750
F 0 "C2" H 5750 2830 39  0000 L CNN
F 1 "1000uF" H 5750 2670 39  0000 L CNN
	1    5700 2750
	1    0    0    -1  
$EndComp
$Comp
L CX C1
U 1 1 4D2BBB89
P 3700 2750
F 0 "C1" H 3750 2830 39  0000 L CNN
F 1 "100uF" H 3750 2670 39  0000 L CNN
	1    3700 2750
	1    0    0    -1  
$EndComp
$Comp
L LM257X U1
U 1 1 4D2BBB60
P 4500 2350
F 0 "U1" H 4300 2550 60  0000 C CNN
F 1 "LM2576ADJ" H 4510 2350 51  0000 C CNN
	1    4500 2350
	1    0    0    -1  
$EndComp
$EndSCHEMATC
