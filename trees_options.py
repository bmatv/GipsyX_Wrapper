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
penna_k_randomwalk_m4 = [[   
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