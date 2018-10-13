import numpy as _np
import pandas as _pd
import glob as _glob
from multiprocessing import Pool as _Pool 
from .gx_aux import J2000origin

def extract_tdps(tmp_dir,project_name,stations_list,years_list,num_cores):
    '''Runs _gather_tdps for each station in the stations_list of the project.
    After update gathers [value] [nomvalue] [sigma] and outputs MultiIndex DataFrame
    Extraction of residuals added'''
    project_files_list = _np.ndarray((len(stations_list)),dtype=object)
    tdps = _np.ndarray((len(stations_list)),dtype=object)

    #convert years_list to ndarray
    years = np.asarray(years_list)

    for i in range(len(stations_list)):
        station_list_all_years = sorted(_glob.glob(tmp_dir + '/gd2e/' + project_name + '/' + stations_list[i] + '/*/*/*.npz'))
        tmp = _pd.DataFrame()
        tmp[['Project','Station', 'Year', 'DOY']] = _pd.Series(station_list_all_years).str.split('/',expand = True).iloc[:, [-5,-4,-3,-2]]
        tmp['Path'] = station_list_all_years
        project_files_list[i] = tmp[tmp['Year'].isin(years.astype(str))]

        tmp_records = _gather_tdps(project_files_list[i]['Path'],num_cores)
        
        # Read header array of tuples correctly with dtype and convert to array of arrays 
        header = _np.load(project_files_list[i]['Path'].iloc[0])['tdp_header']
        dt=_np.dtype([('type', _np.unicode_, 8), ('name',  _np.unicode_,30)])
        header_array = _np.asarray(header,dtype=dt)
        # Creating MultiIndex from header arrays
        m_index = [header_array['type'],header_array['name']]
        # Stacking list of tmp tdps into one np array
        stacked_tdp = _np.vstack(tmp_records)
        # Creating a MultiIndex DataFrame of transposed array. Transposing back and adding time index
        tdps[i] = _pd.DataFrame(data=stacked_tdp[:,1:].T,index=m_index).T.set_index(stacked_tdp[:,0])
    
    return tdps

def _gather_tdps(station_files,num_cores):
    '''Processing extraction in parallel 
    get_tdps_pandas,numpy'''
    num_cores = num_cores if len(station_files) > num_cores else len(station_files)
#         chunksize = int(np.ceil(len(station_files) / num_cores)) #20-30 is the best
    chunksize = 20
    try:
        pool = _Pool(num_cores)
        data_tdp = pool.map(_get_tdps_npz, station_files,chunksize=chunksize)
    finally:
        pool.close()
        pool.join()
    return data_tdp

def _get_tdps_npz(file):
    tmp = _np.load(file=file)['tdp']
    time = tmp[:,0].astype(int)
    #chekcking the total length of the record
    if (time[-1] - time[0])/3600 > 3:
        #clipping to 24 hours on the fly
        start_timeframe = ((time[0] + J2000origin + _np.timedelta64(3,'h')).astype('datetime64[D]')- J2000origin).astype(int)
        end_timeframe = start_timeframe + 86400
        
        return tmp[(time >= start_timeframe) & (time < end_timeframe)]
    else:
#             print('file too short ', file) 
        #normally shouldn't happened as files were filtered after conversion and short files won't be here
        return tmp