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
    solutions = _np.ndarray((len(stations_list)),dtype=object)
    residuals = _np.ndarray((len(stations_list)),dtype=object)

    #convert years_list to ndarray
    years = _np.asarray(years_list)

    for i in range(len(stations_list)):
        station_list_all_years = sorted(_glob.glob(tmp_dir + '/gd2e/' + project_name + '/' + stations_list[i] + '/*/*/*.npz'))
        tmp = _pd.DataFrame()
        tmp[['Project','Station', 'Year', 'DOY']] = _pd.Series(station_list_all_years).str.split('/',expand = True).iloc[:, [-5,-4,-3,-2]]
        tmp['Path'] = station_list_all_years
        project_files_list[i] = tmp[tmp['Year'].isin(years.astype(str))]

        tmp_data = _np.asarray(_gather_tdps(project_files_list[i]['Path'],num_cores))
        
        # Read header array of tuples correctly with dtype and convert to array of arrays 
        raw_solution_header = _np.load(project_files_list[i]['Path'].iloc[0])['tdp_header']
        dt=_np.dtype([('type', _np.unicode_, 8), ('name',  _np.unicode_,30)])
        solution_header = _np.asarray(raw_solution_header,dtype=dt)
        # Creating MultiIndex from header arrays
        solution_m_index = [solution_header['type'],solution_header['name']]

        residuals_header = ['Time','T/R Antenna No','DataType','PF Residual (m)','Elevation from receiver (deg)',\
                            ' Azimuth from receiver (deg)','Elevation from transmitter (deg)',' Azimuth from transmitter (deg)','Status']

        # Stacking list of tmp tdps and residuals into one np array
        stacked_solution = _np.vstack(tmp_data[:,0])
        stacked_residuals = _np.vstack(tmp_data[:,1])

        # Creating a MultiIndex DataFrame of transposed array. Transposing back and adding time index
        solutions[i] = _pd.DataFrame(data=stacked_solution[:,1:].T,index=solution_m_index).T.set_index(stacked_solution[:,0])
        residuals[i] = _pd.DataFrame(data=stacked_residuals, columns = residuals_header).set_index(['DataType','Time'])
    
    return solutions,residuals

def _gather_tdps(station_files,num_cores):
    '''Processing extraction in parallel 
    get_tdps_pandas,numpy'''
    num_cores = num_cores if len(station_files) > num_cores else len(station_files)
#         chunksize = int(np.ceil(len(station_files) / num_cores)) #20-30 is the best
    chunksize = 20
    try:
        pool = _Pool(num_cores)
        data = pool.map(_get_tdps_npz, station_files,chunksize=chunksize)
    finally:
        pool.close()
        pool.join()
    return data

def _get_tdps_npz(file):
    '''Extracts smoothFinal data and finalResiduals data from npz file supplied.
    Clips data to 24 hours of the same day if the file is bigger'''
    tmp_solution = _np.load(file=file)['tdp']
    tmp_residuals = _np.load(file=file)['finalResiduals']

    time_solution = tmp_solution[:,0].astype(int)
    time_residuals = tmp_residuals[:,0].astype(int)

    
    if (time_solution[-1] - time_solution[0])/3600 > 3:
        #checking the total length of the record. In case total length is less than 3 hours, when adding 3 hours it can return wrong day.
        
        #clipping to 24 hours on the fly. Solution and Residuals are cut with the same mask
        begin_timeframe = ((time_solution[0] + J2000origin + _np.timedelta64(3,'h')).astype('datetime64[D]')- J2000origin).astype(int)
        end_timeframe = begin_timeframe + 86400
        
        solution = tmp_solution[(time_solution >= begin_timeframe) & (time_solution < end_timeframe)]
        residuals = tmp_residuals[(time_residuals >= begin_timeframe) & (time_residuals < end_timeframe)]

        return solution,residuals
    else:
        #print('file too short ', file) 
        #normally shouldn't happened as files were filtered after conversion and short files won't be here
        return tmp_solution,tmp_residuals