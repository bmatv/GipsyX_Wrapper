#All on options

penna_k_randomwalk_m8 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e-8 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_m7 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e-7 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_m6 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_m5 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e-5 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_m5_325 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 3.25e-5 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_m5_550 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 5.50e-5 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_m5_775 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 7.75e-5 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_m4_325 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 3.25e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_m4_550 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 5.50e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_m4_775 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 7.75e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_m3 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e-3 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_m2 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e-2 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_m1 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e-1 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_0 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e0 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_1 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e1 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_2 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e2 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]
penna_k_randomwalk_3 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e3 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj',]]


penna_k_randomwalk_m4_static = [[   
    # Stochastic Adjustment State
        # ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Tides section
        ['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
        # ['GRN_STATION_CLK_WHITE:Tides:OceanLoad', '$OCEANLOAD'], #not needed as "all on"
        ['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile', '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],



        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:PostSmoothEdit','2e5 2e4 0.25 0.2 0.1 .05'],    
        ['Global:DataTypes:IonoFreePhaseC1C5:DataLinkSpec_LC_BDS:SignalPath:Platforms','.* C.*'],

        ['Global:DataTypes:IonoFreePhaseP1P2:DataLinkSpec_LC_GPS:PostSmoothEdit','2e5 2e4 0.125 0.1 0.05 .025'],

        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:PostSmoothEdit','2e5 2e4 25 20 10 5'],    
        ['Global:DataTypes:IonoFreeRangeC1C5:DataLinkSpec_PC_BDS:SignalPath:Platforms','.* C.*'],     

        ['Global:DataTypes:IonoFreeRangeP1P2:DataLinkSpec_PC_GPS:PostSmoothEdit','2e5 2e4 12.5 10 5 2.5'],     
        ],
        #Pop values. Values that will be elemenated
        []]


penna_k_randomwalk_m4 = [[   
    # Stochastic Adjustment State
        ['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj', '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        # Trop section    
        ['GRN_STATION_CLK_WHITE:Trop:GradEast', '0.0'],

        ['GRN_STATION_CLK_WHITE:Trop:GradNorth', '0.0'],

        ['GRN_STATION_CLK_WHITE:Trop:Mapping', 'VMF1'],
        ['GRN_STATION_CLK_WHITE:Trop:Model', 'On'],
        ['GRN_STATION_CLK_WHITE:Trop:WetZ', '0.1'],
        #adjustment of troposphere
        ['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e-4 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradNorth:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],
        ['GRN_STATION_CLK_WHITE:Trop:GradEast:StochasticAdj', '1.0 5e-6 $GLOBAL_DATA_RATE RANDOMWALK'],

        # Station properties. e.g. CAMB. So we will get wetz etc in the output. Highly important!!!
        ['Station', '`cat $STATIONLIST`'+'\nStation `staDb2TreeIn.py -s $STATIONLIST -y2kSecs $GLOBAL_EPOCH -d $STA_DB`'],
        # VMF1dataDir path  
        ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
        # Ion2nd
        ['Global:Ion2nd','On'],
        ['Global:Ion2nd:MagneticModel','IGRF'],
        ['Global:Ion2nd:MagneticModel:IgrfCoefficientsFile', '$GOA_VAR/etc/igrf/igrf11coeffs.txt'],
        ['Global:Ion2nd:StecModel', 'IONEX'],
        ['Global:Ion2nd:StecModel:IonexFile:ShellHeight', '600.0e3'],
        # GPS_BlockII as it is missing from default tree file
        ['GPS_BlockII_Model', '=='],
        ['GPS_BlockII_Model:AttitudeModel', 'gpsBlockII'],
        # Satellite section needed for Gipsy to be able to extract satellite properties. Highly important!!!
        ['Satellite','`cat $GNSSLIST`'+ '\nSatellite `pcm.py -file $GNSS_ANT_OFF_PCM -epoch $GLOBAL_EPOCH -sat $GNSSLIST -param Antenna1`'],

        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Degree','0'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:MaxFormalError','0.4'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict','On'],
        ['Global:Input:TimeDepParms:NameFilter:Satellite\.[C]\w*.*\.Clk\.Bias:Strict:MaxDx','1.0e-6'],
        # Section with namefilter for state
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.State\.Pos\..*',' '],
        ['Global:Input:TimeDepParms:NameFilter:Station\..*\.Trop.*',' '],
    
        ],
        #Pop values. Values that will be eliminated
        ['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj']]

#Pseudorange
pseudo_range_glo = [['Global:DataTypes:IonoFreeC_1P_2P', ''],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GLO', ''],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GLO:DataBias', ''],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GLO:DataBias:DataBiasReference', 'GLONASS'],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GLO:DataBias:StochasticAdj', '1.0e4 3.40e-4 DATADRIVEN RANDOMWALK'],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GLO:DataBias:StochasticAdj:UseItOrLoseItInterval', '3600'],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GLO:ElDepWeight', 'SqrtSin'],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GLO:PostSmoothEdit', '2e5 2e4 25 20 10 5'],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GLO:SignalPath', ''],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GLO:SignalPath:Platforms', '.* R.*']]

pseudo_range_gps = [['Global:DataTypes:IonoFreeC_1P_2P', ''],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GPS', ''],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GPS:ElDepWeight', 'SqrtSin'],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GPS:PostSmoothEdit', '2e5 2e4 12.5 10 5 2.5'],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GPS:SignalPath', ''],
['Global:DataTypes:IonoFreeC_1P_2P:DataLinkSpec_PC_GPS:SignalPath:Platforms', '.* GPS.*']]
                    
#Carrier Phase                  
carrier_phase_glo = [['Global:DataTypes:IonoFreeL_1P_2P', ''],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GLO', ''],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GLO:DataBias', ''],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GLO:DataBias:StochasticAdj', '3.0e8 3.0e8 DATADRIVEN WHITENOISE'],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GLO:DataBias:StochasticAdj:UseItOrLoseItInterval', '3600'],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GLO:ElDepWeight', 'SqrtSin'],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GLO:PostSmoothEdit', '2e5 2e4 0.25 0.2 0.1 .05'],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GLO:SignalPath', ''],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GLO:SignalPath:Platforms', '.* R.*']]

carrier_phase_gps = [['Global:DataTypes:IonoFreeL_1P_2P', ''],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GPS', ''],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GPS:DataBias', ''],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GPS:DataBias:StochasticAdj', '3.0e8 3.0e8 DATADRIVEN WHITENOISE'],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GPS:DataBias:StochasticAdj:UseItOrLoseItInterval', '3600'],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GPS:ElDepWeight', 'SqrtSin'],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GPS:PostSmoothEdit', '2e5 2e4 0.125 0.1 0.05 .025'],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GPS:SignalPath', ''],
['Global:DataTypes:IonoFreeL_1P_2P:DataLinkSpec_LC_GPS:SignalPath:Platforms', '.* GPS.*']]

# Tides section
tides_all_on = [['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
['GRN_STATION_CLK_WHITE:Tides:SolidTide', 'On'],
['GRN_STATION_CLK_WHITE:Tides:PoleTide', 'On'],
['GRN_STATION_CLK_WHITE:Tides:OceanLoad', 'On']] #turning all components on manually

tides_otl_off = [['GRN_STATION_CLK_WHITE:Tides:All', 'On'],
['GRN_STATION_CLK_WHITE:Tides:SolidTide', 'On'],
['GRN_STATION_CLK_WHITE:Tides:PoleTide', 'On'],
['GRN_STATION_CLK_WHITE:Tides:OceanLoad', 'Off']]#turning all components on manually

#gps_sv_del = [['Satellite:Delete','GPS01 GPS02 GPS03 GPS04 GPS05 GPS06 GPS08 GPS09 GPS10 GPS11 GPS13 GPS14 GPS15 GPS16 GPS17 GPS18 GPS19 GPS20 GPS21 GPS22 GPS23 GPS24 GPS25 GPS26 GPS27 GPS28 GPS29 GPS30 GPS31 GPS32 GPS33 GPS34 GPS35 GPS36 GPS37 GPS38 GPS39 GPS40 GPS41 GPS43 GPS44 GPS45 GPS46 GPS47 GPS48 GPS49 GPS50 GPS51 GPS52 GPS53 GPS54 GPS55 GPS56 GPS57 GPS58 GPS59 GPS60 GPS61 GPS62 GPS63 GPS64 GPS65 GPS66 GPS67 GPS68 GPS69 GPS71 GPS72 GPS73 GPS70']]

#glo_sv_del = [['Satellite:Delete','R701 R802 R711 R712 R713 R714 R715 R716 R717 R718 R719 R720 R721 R722 R723 R724 R725 R726 R727 R728 R729 R730 R731 R732 R733 R734 R735 R736 R737 R738 R742 R743 R744 R745 R746 R747 R851 R852 R853 R856 R754 R854 R755 R855 R783 R787 R788 R789 R791 R792 R793 R794 R795 R796 R797 R798 R801']]

tree_glo_only = [tides_all_on + penna_k_randomwalk_m4[0],penna_k_randomwalk_m4[1]]

tree_gps_only = [tides_all_on + penna_k_randomwalk_m4[0],penna_k_randomwalk_m4[1]]

tree_gps_only_no_otl = [tides_otl_off + penna_k_randomwalk_m4[0],penna_k_randomwalk_m4[1]]

tree_gps_glo = [tides_all_on + penna_k_randomwalk_m4[0],penna_k_randomwalk_m4[1]]