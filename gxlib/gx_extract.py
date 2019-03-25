import numpy as _np
import pandas as _pd
import glob as _glob
import os as _os
from multiprocessing import Pool as _Pool 
from .gx_aux import J2000origin, _dump_read, _dump_write
import tqdm as _tqdm

'''Extraction of solutions from npz'''
def gather_solutions(tmp_dir,project_name,stations_list,num_cores):

    stations_list = _np.core.defchararray.upper(stations_list)

    #check if station from input is in the folder
    gd2e_stations_list = _os.listdir(tmp_dir + '/gd2e/'+project_name)
    station_exists = _np.isin(stations_list,gd2e_stations_list)

    checked_stations = stations_list[station_exists==True]

    n_stations = len(checked_stations)
    #Create a list of paths to get data from
    paths_tmp = tmp_dir + '/gd2e/'+ project_name + '/' + _np.asarray(checked_stations,dtype=object) + '/solutions.lz4'

    gather = _np.ndarray((n_stations), dtype=object)
    '''This loader can be multithreaded'''

    for i in range(n_stations):
        if not _os.path.exists(paths_tmp[i]):
            print('No gather file for {} station in {}.\n Running extract_tdps for the dataset.'.format(checked_stations[i],project_name))
            extract_tdps(tmp_dir,project_name,checked_stations[i],num_cores)

        print('Found', paths_tmp[i], 'Loading...')
        gather[i] = _dump_read(paths_tmp[i])
    return gather

def rm_solutions_gathers(tmp_dir,project_name):
    gathers = _glob.glob(_os.path.join(tmp_dir,'gd2e',project_name) + '/*/solutions.pickle')
    for gather in gathers: _os.remove(gather)
def rm_residuals_gathers(tmp_dir,project_name):
    gathers = _glob.glob(_os.path.join(tmp_dir,'gd2e',project_name) + '/*/residuals.pickle')
    for gather in gathers: _os.remove(gather)


def gather_residuals(tmp_dir,project_name,stations_list,num_cores):
    stations_list = _np.core.defchararray.upper(stations_list)

    #check if station from input is in the folder
    gd2e_stations_list = _os.listdir(tmp_dir + '/gd2e/'+project_name)
    station_exists = _np.isin(stations_list,gd2e_stations_list)

    checked_stations = stations_list[station_exists==True]

    n_stations = len(checked_stations)
    #Create a list of paths to get data from
    paths_tmp = tmp_dir + '/gd2e/'+ project_name + '/' + _np.asarray(checked_stations,dtype=object) + '/residuals.lz4'

    gather = _np.ndarray((n_stations), dtype=object)
    '''This loader can be multithreaded'''

    for i in range(n_stations):
        if not _os.path.exists(paths_tmp[i]):
            print('No gather file for {} station in {}.\n Running extract_tdps for the dataset.'.format(checked_stations[i],project_name))
            extract_tdps(tmp_dir,project_name,checked_stations[i],num_cores)

        print('Found', paths_tmp[i], 'Loading...')
        gather[i] = _dump_read(paths_tmp[i])
    return gather

def extract_tdps(tmp_dir,project_name,station_name,num_cores):
    '''Runs _gather_tdps for each station in the stations_list of the project.
    After update gathers [value] [nomvalue] [sigma] and outputs MultiIndex DataFrame
    Extraction of residuals moved to extract_residuals
    
    Extracted data is saved in the project directory name_of_project.npz with
    [solutions] and [residuals] datasets inside.
    If file doesn't exist, will run the script and save the file as it should.
    Rolling back to the version where solutions and residuals were collected simultaneously.

    Creates folder "gather" and puts station-named files in it.
    All stations all years.
    '''

    station_files = _np.asarray(sorted(_glob.glob(tmp_dir + '/gd2e/' + project_name + '/' + station_name + '/*/*/*.zstd')))
    tmp_data = _np.asarray(_gather_tdps(station_files, num_cores))

    # Stacking list of tmp tdps and residuals into one np array
    stacked_solutions = _pd.concat(tmp_data[:,0])
    stacked_residuals = _pd.concat(tmp_data[:,1])
    # For residuals trans column should be converted to category again
    stacked_residuals['trans'] = stacked_residuals['trans'].astype('category')
    # print(station_name, 'extraction finished')

    solutions_file = tmp_dir + '/gd2e/' + project_name + '/' +  station_name + '/solutions.lz4'
    _dump_write(data=stacked_solutions,filename=solutions_file,cname='lz4')
    # print(station_name, 'solutions successfully saved')

    residuals_file = tmp_dir + '/gd2e/' + project_name + '/' +  station_name + '/residuals.lz4'
    _dump_write(data=stacked_residuals,filename=residuals_file,cname='lz4')
    # print(station_name, 'residuals successfully saved')

def _gather_tdps(station_files,num_cores):
    '''Processing extraction in parallel 
    get_tdps_pandas,numpy'''
    num_cores = num_cores if station_files.shape[0] > num_cores else station_files.shape[0]
    #  chunksize = int(np.ceil(len(station_files) / num_cores)) #20-30 is the best
    chunksize = 20
 
    with _Pool(processes = num_cores) as p:
        data = list(_tqdm.tqdm_notebook(p.imap(_get_tdps_npz, station_files,chunksize=chunksize), total=station_files.shape[0]))
    return data

def _get_tdps_npz(file):
    '''Extracts smoothFinal data and finalResiduals data from npz file supplied.
    Clips data to 24 hours of the same day if the file is bigger'''
    tmp_solution,tmp_residuals = _dump_read(file)[:2]

    #begin_timeframe as file time median should always work
    begin_timeframe = ((_np.median(tmp_solution.index).astype(int)+ J2000origin).astype('datetime64[D]')- J2000origin).astype(int)
    end_timeframe = begin_timeframe + 86400
        
    solution = tmp_solution[(tmp_solution.index >= begin_timeframe) & (tmp_solution.index < end_timeframe)]
    residuals = tmp_residuals[(tmp_residuals.index.get_level_values(1) >= begin_timeframe) & (tmp_residuals.index.get_level_values(1) < end_timeframe)]

    return solution,residuals