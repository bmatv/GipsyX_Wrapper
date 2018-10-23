import numpy as _np
import glob as _glob
import numpy as _np
import pandas as _pd
import os as _os

def get_debug(tmp_dir, project_name):
    stations_list = sorted(next(_os.walk('{}/gd2e/{}'.format(tmp_dir,project_name)))[1])
    years_list_station_0 = sorted(next(_os.walk('{}/gd2e/{}/{}'.format(tmp_dir,project_name,stations_list[0])))[1])
    
    npz1_path =  sorted(_glob.glob(('{}/gd2e/{}/{}/{}/*/gipsyx_out.npz'.format(tmp_dir,project_name,stations_list[0],years_list_station_0[0]))))[0]
    debug_tree = _np.load(npz1_path)['debug_tree']
    tree = _pd.Series(debug_tree[:,0])

    wetz_apriori = tree[tree.str.contains(pat='WetZ ')]
    ZWD_proc_noise = float(tree[wetz_apriori.index+1].str.split(expand=True)[2].iloc[0])
    station_name = tree[tree.str.contains(pat=stations_list[0]+' ')]
    
    station_name_part = tree[station_name.index[0]:]
    state_line = station_name_part[station_name_part.str.contains(pat = 'State')]
    tides_line = station_name_part[station_name_part.str.contains(pat = 'Tides')]
    
    state_section = tree[state_line.index[0]:tides_line.index[0]]
    state_stoc_adj = state_section[state_section.str.contains(pat = 'StochasticAdj')]
    coordinate_processing = state_stoc_adj.str.split(expand=True)[[1,2,4]].rename(columns={1: 'coord_apriori_sigma', 2: 'coord_procnoise_sigma',4:'coord_mode'}).reset_index(drop=True)
    coordinate_processing['project_name'] =project_name
    coordinate_processing['ZWD_proc_noise'] = ZWD_proc_noise
        
    return coordinate_processing
    
def STD_Vert(envs):
    std_array = _np.ndarray((envs.shape))
    for i in range(envs.shape[0]):
        std_array[i] = envs[i]['value'].iloc[:,2].std()
    return std_array

def RMS_Res(residuals):
    rms_array = _np.ndarray((residuals.shape))
    for i in range(residuals.shape[0]):
        L_residuals = residuals[i][residuals[i]['Status'].isna()].loc['IonoFreeL_1P_2P']['PF Residual (m)']
        rms_array[i] = (((L_residuals**2).sum())/L_residuals.count())**0.5
    return rms_array

def penna_test(class_name):
    debug_df = get_debug(tmp_dir=class_name.tmp_dir,project_name=class_name.project_name)
    
    #check if station from input is in the folder
    gd2e_stations_list = sorted(next(_os.walk('{}/gd2e/{}'.format(class_name.tmp_dir, class_name.project_name)))[1])

    stdv_array = STD_Vert(class_name.envs())
    rms_res_array = RMS_Res(class_name.residuals())
    for i in range(len(gd2e_stations_list)):
        debug_df[gd2e_stations_list[i]+'.STD_Vert'] = stdv_array[i]
        debug_df[gd2e_stations_list[i]+'.RMS_Res'] = rms_res_array[i]       
    return debug_df