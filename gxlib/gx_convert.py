import numpy as _np
import pandas as _pd
import glob as _glob
import os as _os
import tqdm as _tqdm
from subprocess import Popen as _Popen
from multiprocessing import Pool as _Pool
from shutil import rmtree as _rmtree, copy as _copy

def prepare_dir_struct(begin_year, end_year,tmp_dir):
    timeline = _pd.Series(_np.arange(_np.datetime64(str(begin_year)),_np.datetime64(str(end_year+1)),_np.timedelta64(1,'D')))
    dayofyear = timeline.dt.dayofyear.astype(str).str.zfill(3)
    year = timeline.dt.year.astype(str)
    dirs = tmp_dir +'/rnx_dr/' + year +'/'+ dayofyear

    for path in dirs:
        if not _os.path.exists(path):
            _os.makedirs(path)

def select_rnx(stations_list,years_list,rnx_dir,tmp_dir,hatanaka,cddis=False):
    '''rnx_dir is path to daily folder that has year-like structure. e.g. /mnt/data/bogdanm/GNSS_data/CDDIS/daily/ with subfolders 2010 2011 ...
    It is a single array of paths to raw RNX files with all properties needed for the file
    Outputs df wi columns: year (int) | station_name (caps) | doy (int) | rnx_path (object) | dr_path (object)
    If hatanaka => select d.Z files, else: o.gz
    /scratch/bogdanm/GNSS_data/geonet_nz_ogz/2014/001/anau0010.14o.gz
    /scratch/bogdanm/GNSS_data/geonet_nz/2014/001/anau0010.14d.Z'''
    
    rnx_dir = _os.path.abspath(rnx_dir)+'/'
    tmp_dir = _os.path.abspath(tmp_dir)
    
    extension = 'd.Z' if hatanaka else 'o.gz'
    station_files = []
    for i in range(len(stations_list)):
        for j in range(0, len(years_list)):
            if cddis:
                j_year_files = _glob.glob(rnx_dir+str(years_list[j])+'/*/*/'+ _np.str.lower(stations_list[i])+'*'+str(years_list[j])[2:]+extension)
            else:    
                j_year_files = _glob.glob(rnx_dir+str(years_list[j])+'/*/'+ _np.str.lower(stations_list[i])+'*'+str(years_list[j])[2:]+extension)
            
            
            if len(j_year_files) > 0:
                
                station_files.append(_np.sort(_np.asarray(j_year_files)))
            else:
                print('gx_convert.select_rnx: No RNX files found for', str(stations_list[i]), str(years_list[j]) +'. Please check rnx_in folder')
    paths_series = _pd.Series(_np.sort(_np.concatenate(station_files)))
    extracted_df = paths_series.str.extract(r'\/(\d{4})\/\d{3}(?:\/\d{2}d|)\/((\w{4})(\d{3}).+)').astype({0:int,1:object,2:'category',3:int})
    extracted_df.columns = ['year','filename','station_name','doy']
    extracted_df['station_name'].cat.rename_categories(_pd.Series(extracted_df['station_name'].cat.categories).str.upper().to_list(),inplace=True)
    
    extracted_df['rnx_path'] = paths_series
    extracted_df['dr_path'] = (tmp_dir +'/rnx_dr/' + extracted_df['year'].astype(str) +'/'+extracted_df['doy'].astype(str).str.zfill(3)
    +'/'+extracted_df['station_name'].astype(str).str.lower()+extracted_df['doy'].astype(str).str.zfill(3)+'0.'\
    +extracted_df['year'].astype(str).str.slice(2)+extension[0]+'.dr.gz')
    #{tmp_dir}/rnx_dr/2010/doy/xxxxddd0.ext.dr.gz <1st symbol of ext (o or d)
    # preparing dir structure
    prepare_dir_struct(begin_year=extracted_df['year'].min(), end_year=extracted_df['year'].max(),tmp_dir=tmp_dir)
    return extracted_df

def _2dr(rnx2dr_path):
    '''Opens process rxEditGde.py to convert specified rnx to dr file for GipsyX. The subprocess is used in order to run multiple instances at once.
    If converted file is already present, nothing happens
    We might want to dump and kill service tree files and stats'''
    in_file_path = rnx2dr_path[0]
    out_file_path = rnx2dr_path[1]
    cache_path = rnx2dr_path[2]
    out_dir = _os.path.dirname(rnx2dr_path[1])

    cache_dir = _os.path.join(cache_path,_os.path.basename(out_file_path)) #smth like /cache/anau2350.10d.dr.gz/
    if not _os.path.exists(cache_dir):
        _os.makedirs(cache_dir)
    _copy(src = in_file_path, dst = cache_dir) #copy 
    in_file_cache_path = _os.path.join(cache_dir,_os.path.basename(in_file_path))
    out_file_cache_path = _os.path.join(cache_dir,_os.path.basename(out_file_path))

    process = _Popen(['rnxEditGde.py', '-dataFile', in_file_cache_path, '-o', out_file_cache_path],cwd = cache_dir)
    process.wait()
    _copy(src = out_file_cache_path, dst = out_dir) #copy result to destination
    #clear folder in ram
    _rmtree(cache_dir)



def rnx2dr(selected_df,num_cores,tqdm,cache_path,cddis=False):
    '''Runs rnxEditGde.py for each file in the class object in multiprocessing'''
    #Checking files that are already in place so not to overwrite
    if_exists_array = _np.ndarray((selected_df.shape[0]),dtype=bool)
    for i in range(if_exists_array.shape[0]):
        if_exists_array[i] = not _os.path.exists(selected_df['dr_path'][i])
    selected_df = selected_df[if_exists_array]


    selected_df2convert = selected_df[['rnx_path','dr_path']].copy()
    selected_df2convert['cache_path'] = cache_path #populating df with cache path value
    selected_df2convert = selected_df2convert.values
     
    if selected_df2convert.shape[0] > 0:
        num_cores = num_cores if selected_df2convert.shape[0] > num_cores else selected_df2convert.shape[0]
        print ('Number of files to process:', selected_df2convert.shape[0],'| Adj. num_cores:', num_cores,end=' ')

        with _Pool(processes = num_cores) as p:
            if tqdm: list(_tqdm.tqdm_notebook(p.imap(_2dr, selected_df2convert), total=selected_df2convert.shape[0]))
            else: p.map(_2dr, selected_df2convert)
    else:
        #In case length of unconverted files array is 0 - nothing will be converted
        print('RNX files converted.\nNothing to convert. All available rnx files are already converted')