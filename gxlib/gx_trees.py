import pandas as _pd
import glob as _glob
import os as _os, sys as _sys

_sys.path.append('..')

from trees_options import carrier_phase_glo, carrier_phase_gps, pseudo_range_glo, pseudo_range_gps

_PYGCOREPATH="{}/lib/python{}.{}".format(_os.environ['GCOREBUILD'],
                            _sys.version_info[0], _sys.version_info[1])
if _PYGCOREPATH not in _sys.path:
    _sys.path.insert(0,_PYGCOREPATH)

import gcore.treeUtils as _treeUtils

def gen_trees(tmp_dir, ionex_type, tree_options,blq_file, mode):
    '''Creates trees based on tree_options array and yearly IONEX merged files. Returns DataFrame with trees' details
    Options: GPS and GLO are booleans that will come from the main class and affect the specific DataLink blocks in the tree file.
    Together with this drInfo files with specific properties will be filtered
    Expects mode to be one of the following: [None, 'GPS', 'GLONASS','GPS+GLONASS']. Will be fetched by gd2e_wrap automatically'''

    modes = ['GPS', 'GLONASS','GPS+GLONASS']
    if mode not in modes:
        raise ValueError("Invalid mode. Expected one of: %s" % modes)

    #Modifying tree_optins[0] according to mode selected. Mode cannot be None here as DataLink paraeters should be present at least for one constellation
    GPS_DataLink = pseudo_range_gps + carrier_phase_gps
    GLONASS_DataLink = pseudo_range_glo + carrier_phase_glo
    if mode == 'GPS':
        DataLink = GPS_DataLink
    elif mode == 'GLONASS':
        DataLink = GLONASS_DataLink
    elif mode == 'GPS+GLONASS':
        DataLink = (GPS_DataLink + GLONASS_DataLink)
    
    tree_options[0] += DataLink


    # reading ionex filenames
    out_df = _pd.DataFrame()
#         default_tree = '/home/bogdanm/Desktop/GipsyX_trees/Trees_kinematic_VMF1_IONEX/ppp_0.tree'
    default_tree = '/apps/gipsyx/beta/GipsyX-Beta/share/gd2e/DefaultTreeSeries/PPP/ppp_0.tree'
    input_tree = _treeUtils.tree(default_tree)
    ionex_files = _pd.Series(sorted(_glob.glob(tmp_dir+'/IONEX_merged/' + ionex_type + '*')))
    ionex_basenames = ionex_files.str.split('/', expand=True).iloc[:, -1]

    out_df['year'] = ionex_basenames.str.slice(3, 7)
    out_df['tree_path'] = tmp_dir + '/Trees/' + ionex_basenames + '/'  # where to save tree file

    for i in range(len(ionex_files)):

        if not _os.path.exists(out_df['tree_path'].iloc[i]):
            _os.makedirs(out_df['tree_path'].iloc[i])

        #Removing options from default tree. These options are stored as tree_options[1]
        for option in tree_options[1]:
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
        for option in tree_options[0]:
            input_tree.entries[option[0]] = _treeUtils.treevalue(option[1])  # write standard parameters
        #Add blq file location manually. At this step will override any tree option
        input_tree.entries['GRN_STATION_CLK_WHITE:Tides:OceanLoadFile'] =  _treeUtils.treevalue(blq_file)

        input_tree.save(out_df['tree_path'][i] + 'ppp_0.tree')
    # return year type path_trees

    return out_df.set_index(['year']) 