import numpy as _np
import pandas as _pd
import glob as _glob
import os as _os
import tqdm as _tqdm
from subprocess import Popen as _Popen
from multiprocessing import Pool as _Pool

def select_rnx(stations_list,years_list,rnx_dir,tmp_dir,cddis=False):
    '''rnx_dir is path to daily folder that has year-like structure. e.g. /mnt/data/bogdanm/GNSS_data/CDDIS/daily/ with subfolders 2010 2011 ...
    It is a single array of paths to raw RNX files with all properties needed for the file
    Outputs df wi columns: year (int) | station_name (caps) | doy (int) | rnx_path (object) | dr_path (object)'''
    
    rnx_dir = _os.path.abspath(rnx_dir)+'/'
    tmp_dir = _os.path.abspath(tmp_dir)
    
    station_files = []
    for i in range(len(stations_list)):
        for j in range(0, len(years_list)):
            if cddis:
                j_year_files = _glob.glob(rnx_dir+str(years_list[j])+'/*/*/'+ _np.str.lower(stations_list[i])+'*'+str(years_list[j])[2:]+'d.Z')
            else:    
                j_year_files = _glob.glob(rnx_dir+str(years_list[j])+'/*/'+ _np.str.lower(stations_list[i])+'*'+str(years_list[j])[2:]+'d.Z')
            
            
            if len(j_year_files) > 0:
                
                station_files.append(_np.sort(_np.asarray(j_year_files)))
            else:
                print('gx_convert.select_rnx: No RNX files found for', str(stations_list[i]), str(years_list[j]) +'. Please check rnx_in folder')
    paths_series = _pd.Series(_np.sort(_np.concatenate(station_files)))
    extracted_df = paths_series.str.extract(r'\/(\d{4})\/\d{3}(?:\/\d{2}d|)\/((\w{4})(\d{3}).+)').astype({0:int,1:object,2:'category',3:int})
    extracted_df.columns = ['year','filename','station_name','doy']
    extracted_df['station_name'].cat.rename_categories(_pd.Series(extracted_df['station_name'].cat.categories).str.upper().to_list(),inplace=True)
    
    extracted_df['rnx_path'] = paths_series
    extracted_df['dr_path'] = (tmp_dir +'/rnx_dir/' + extracted_df['station_name'].astype(str) 
                               + '/' + extracted_df['year'].astype(str) +'/' + extracted_df['doy'].astype(str).str.zfill(3) 
                               + '/' + extracted_df['filename'] +'.dr.gz')
    
    return extracted_df

def _2dr(rnx2dr_path):
    '''Opens process rxEditGde.py to convert specified rnx to dr file for GipsyX. The subprocess is used in order to run multiple instances at once.
    If converted file is already present, nothing happens
    We might want to dump and kill service tree files and stats'''
    out_dir = _os.path.dirname(rnx2dr_path[1])
    if not _os.path.exists(out_dir):
        _os.makedirs(out_dir)
    process = _Popen(['rnxEditGde.py', '-dataFile', rnx2dr_path[0], '-o', _os.path.basename(rnx2dr_path[1])],cwd = out_dir)
    process.wait()
    #here goes section on cleaning service info
    stats_file = _glob.glob(out_dir+'/*stats')
    tree_files = _glob.glob(out_dir+'/*tree')
    files2rm = stats_file + tree_files
    for file in files2rm:
        if _os.path.isfile(file):
            _os.remove(file)

def rnx2dr(selected_df,num_cores,tqdm,cddis=False):
    '''Runs rnxEditGde.py for each file in the class object in multiprocessing'''
    #Checking files that are already in place so not to overwrite
    if_exists_array = _np.ndarray((selected_df.shape[0]),dtype=bool)
    for i in range(if_exists_array.shape[0]):
        if_exists_array[i] = not _os.path.exists(selected_df['dr_path'][i])

    selected_df2convert = selected_df[['rnx_path','dr_path']].values[if_exists_array]

    if selected_df2convert.shape[0] > 0:
        num_cores = num_cores if selected_df2convert.shape[0] > num_cores else selected_df2convert.shape[0]
        chunksize = int(_np.ceil(selected_df2convert.shape[0] / num_cores))
        print ('Number of files to process:', selected_df2convert.shape[0],'| Adj. num_cores:', num_cores,'| Chunksize:', chunksize,end=' ')

        with _Pool(processes = num_cores) as p:
            if tqdm: list(_tqdm.tqdm_notebook(p.imap(_2dr, selected_df2convert), total=selected_df2convert.shape[0]))
            else: p.map(_2dr, selected_df2convert)
    else:
        #In case length of unconverted files array is 0 - nothing will be converted
        print('RNX files converted.\nNothing to convert. All available rnx files are already converted')