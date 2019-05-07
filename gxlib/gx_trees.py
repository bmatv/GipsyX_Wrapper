import pandas as _pd
import glob as _glob
import os as _os, sys as _sys

_sys.path.append('..')

from trees_options import _carrier_phase_glo, _carrier_phase_gps, _pseudo_range_glo, _pseudo_range_gps

_PYGCOREPATH="{}/lib/python{}.{}".format(_os.environ['GCOREBUILD'],
                            _sys.version_info[0], _sys.version_info[1])
if _PYGCOREPATH not in _sys.path:
    _sys.path.insert(0,_PYGCOREPATH)

import gcore.treeUtils as _treeUtils

def gen_trees(tmp_dir, ionex_type, tree_options,blq_file, mode, ElMin, pos_s, wetz_s, PPPtype,VMF1_dir):
    '''Creates trees based on tree_options array and yearly IONEX merged files. Returns DataFrame with trees' details
    Options: GPS and GLO are booleans that will come from the main class and affect the specific DataLink blocks in the tree file.
    Together with this drInfo files with specific properties will be filtered
    Expects mode to be one of the following: [None, 'GPS', 'GLONASS','GPS+GLONASS']. Will be fetched by gd2e_wrap automatically
    
    BOS TEST
    Bos' test cutoff angle (ElMin). If differs from default - updates all *ElMin keys with value specified

    PANNA TEST
    For penna's tests coordinate process noise of:
    COORDINATE PROCESS NOISE (RANDOMWALK)
    Default expression for trees script is GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj = '1.0 5.7e-4 $GLOBAL_DATA_RATE RANDOMWALK'
    [0.0032, 0.01,0.032,0.1,0.18,0.32, 0.57, 1, 1.8, 3.2, 10,32,100,320] mm/sqrt(s)
    were used. The most important values are [0.1,0.18,0.32, 0.57, 1, 1.8, 3.2] from the center of the list. 0.57 mm/sqrt(s) is the one used for processing

    ([['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj','1.0 {:.1E} $GLOBAL_DATA_RATE RANDOMWALK'.format(float(wetz_s)/1000)]])

    ZENITH WET DELAY (RANDOMWALK) 
    Default expression for trees script is 'GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj', '0.5 1e-4 $GLOBAL_DATA_RATE RANDOMWALK'
    ZWD values of [0.00001, 0.0001,0.001,0.0032, 0.057, 0.1,0.18,0.32,1,10,100] mm/sqrt(s). 
    Most important are: [0.001,0.0032, 0.057, 0.1,0.18,0.32,1] mm/sqrt(s)

    ([['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj','0.5 {:.1E} $GLOBAL_DATA_RATE RANDOMWALK'.format(float(wetz_s)/1000)]])

    VMF1 dir is also expected ['Station:VMF1dataDir', '/mnt/Data/bogdanm/Products/VMF1_Products'],
    '''

    modes = ['GPS', 'GLONASS','GPS+GLONASS']
    if mode not in modes:
        raise ValueError("Invalid mode. Expected one of: %s" % modes)

    PPPtypes = ['static','kinematic']
    if PPPtype not in PPPtypes:
        raise ValueError("Invalid PPP type. Expected one of: %s" % PPPtypes)

    tmp_options_add = tree_options[0].copy(); tmp_options_remove = tree_options[1].copy() #Adding tmp vars to prevent original options from overwriting
    
    '''Static or Kinematic PPP. Kinematic is default'''
    if PPPtype == 'kinematic':
        # adding coordinate process noise
        tmp_options_add += [['GRN_STATION_CLK_WHITE:State:Pos:StochasticAdj','1.0 {:.1e} $GLOBAL_DATA_RATE RANDOMWALK'.format(float(pos_s)/1000)]]
        # adding zenith wet delay process noise
        tmp_options_add += [['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj','0.5 {:.1e} $GLOBAL_DATA_RATE RANDOMWALK'.format(float(wetz_s)/1000)]]


    if PPPtype == 'static':
        wetz_s = 0.05 #mm/sqrt(s) is the value Penna used for static processing. Only one solution is needed for no_synth and synth
        tmp_options_add += [['GRN_STATION_CLK_WHITE:State:Pos:ConstantAdj','1.0']]
        tmp_options_add += [['GRN_STATION_CLK_WHITE:Trop:WetZ:StochasticAdj','0.5 {:.1e} $GLOBAL_DATA_RATE RANDOMWALK'.format(float(wetz_s)/1000)]]

    #adding VMF1 dir parameter that can change
    tmp_options_add += [['Station:VMF1dataDir', _os.path.abspath(VMF1_dir)]]


    #Modifying tree_optins[0] according to mode selected. Mode cannot be None here as DataLink paraeters should be present at least for one constellation
    GPS_DataLink = _pseudo_range_gps + _carrier_phase_gps
    GLONASS_DataLink = _pseudo_range_glo + _carrier_phase_glo
    if mode == 'GPS':
        DataLink = GPS_DataLink
    elif mode == 'GLONASS':
        DataLink = GLONASS_DataLink
    elif mode == 'GPS+GLONASS':
        DataLink = (GPS_DataLink + GLONASS_DataLink)
    
    tmp_options_add += DataLink
    


    # reading ionex filenames
    out_df = _pd.DataFrame()
#         default_tree = '/home/bogdanm/Desktop/GipsyX_trees/Trees_kinematic_VMF1_IONEX/ppp_0.tree'
    default_tree = _os.path.join(_os.environ['GCORE'], 'share/gd2e/DefaultTreeSeries/PPP/ppp_0.tree')
    input_tree = _treeUtils.tree(default_tree)

    products_dir = _os.path.join(tmp_dir,_os.pardir,_os.pardir,'Products')

    ionex_files = _pd.Series(sorted(_glob.glob(products_dir+'/IONEX_merged/' + ionex_type + '*')))
    ionex_basenames = ionex_files.str.split('/', expand=True).iloc[:, -1]

    out_df['year'] = ionex_basenames.str.slice(3, 7)
    out_df['tree_path'] = tmp_dir + '/Trees/' + ionex_basenames + '/'  # where to save tree file

    for i in range(len(ionex_files)):

        if not _os.path.exists(out_df['tree_path'].iloc[i]):
            _os.makedirs(out_df['tree_path'].iloc[i])

        #Removing options from default tree. These options are stored as tree_options[1]
        for option in tmp_options_remove:
            input_tree.entries.pop(option, None)

        #Removing all 'Global:DataTypes:IonoFree' options from default tree
        #Selecting them first:
        ion_entries=[]
        for key in input_tree.entries:
            if key.startswith('Global:DataTypes:IonoFree'):
                ion_entries.append(key)
        # ion_entries.sort()

        #Removing all selected datalink keys
        for option in ion_entries:
            input_tree.entries.pop(option, None)

        #Add IONEX_merged file dynamically based on IONEX basename (year and type)
        input_tree.entries['Global:Ion2nd:StecModel:IonexFile'] = _treeUtils.treevalue(ionex_files[i])

        #Adding options to default tree. These options are stored as tree_options[0]
        for option in tmp_options_add:
            input_tree.entries[option[0]] = _treeUtils.treevalue(option[1])  # write standard parameters
        #Add blq file location manually. At this step will override any tree option
        input_tree.entries['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile'] =  _treeUtils.treevalue(blq_file)

        #ElMin parameter change, default is 7
        if ElMin != 7:
            #find all ElMin entries
            keys_series = _pd.DataFrame(input_tree.entries.keys()).squeeze() # for efficient .contains ElMin
            ElMin_keys = keys_series[keys_series.str.contains('ElMin')].values # object ndarray of keys to update

            for key in ElMin_keys:
                input_tree.entries[key] = _treeUtils.treevalue(str(ElMin)) # updating all ElMin keys with new angle value

        input_tree.save(out_df['tree_path'][i] + 'ppp_0.tree')
    # return year type path_trees

    return out_df.set_index(['year']) 