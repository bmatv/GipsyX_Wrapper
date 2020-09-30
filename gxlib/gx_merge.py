import numpy as _np
import pandas as _pd
import os as _os
from subprocess import Popen as _Popen
from multiprocessing import Pool as _Pool
import tqdm as _tqdm
from .gx_aux import J2000origin, _dump_read, drInfo_lbl, rnx_dr_lbl

def get_merge_table(tmp_dir,stations_list,mode=None):
    '''
    Reads drInfo file and outputs merge_table for all available stations in drInfo in one single dataframe.
    tmp_dir is expected to have drinfo.npz file produced by get_drinfo function
    Analyses the properties of dr files and outputs classified dataset where class 3 files can be meged to 32 hours files centered on the midday.
    Currently there are no special cases for the very first and last files of the station as if merged non-symmetrically won't be centred'''

    tmp_dir = _os.path.abspath(tmp_dir)
    rnx_dir = _os.path.join(tmp_dir,rnx_dr_lbl)
    drinfo = _dump_read(filename='{}/{}.zstd'.format(rnx_dir,drInfo_lbl))  
    modes = [None, 'GPS', 'GLONASS','GPS+GLONASS']
    if mode not in modes:
        raise ValueError("Invalid mode. Expected one of: %s" % modes)


    '''Creating classes according to record length'''
    dr_classes = []

    if mode is None:
        complete_record = drinfo #all available files will be merged. Usually this is what I start with
    elif mode == 'GPS':
        complete_record = drinfo[drinfo['GPS']>=3] #need at least 3 satellites present in the file
    elif mode == 'GLONASS':
        complete_record = drinfo[drinfo['GLONASS']>=3] #need at least 3 satellites present in the file
    elif mode == 'GPS+GLONASS':
        complete_record = drinfo[(drinfo['GPS']>0)&(drinfo['GLONASS']>0)] #at least one satellite of each constellation for the processing
    
    for station in stations_list:
        station_record = complete_record[complete_record['station_name'] == station].sort_values(by='begin')
        if station_record.shape[0] == 0:
            raise ValueError("No data found for mode {} for station {}".format(mode,station)) #need to return a list of stations

        drinfo_rec_time = station_record['length'].values
        if (drinfo_rec_time>24).sum() != 0: print('Files longer than 24 hours detected in drInfo. Ignoring those as are possibly corrupted.')
        completeness = _np.zeros((drinfo_rec_time.shape),dtype=int)
        #-----------------------------------------------------------------------
        # Basic filtering module that uses total length of the datarecord.
        # records with more than 12 hours of data but less than 20 hours of data get 1
        completeness[((drinfo_rec_time>=12) & ((drinfo_rec_time)<20))]=1

        #records with more than 20 hours of data get 2
        
        completeness[(drinfo_rec_time>=20)& ((drinfo_rec_time)<24)]=2 # as we work with 24 daily files, we do not use files that are longer
        #-----------------------------------------------------------------------

        # BOUNDARY_1                                    # BOUNDARY_2

        # start_c - start_p         <=24h & >=4h        # end_n   - start_c  <=48h & >=28h
        #  day      hour                                #  hour     day

        # start_c - end_p           <=1h  & >=0m        # start_n - start_c  <=25h  & >=24h | Only gaps of up to 1h are accepted
        #  day      hour                                #  hour     day
        # Missing data of 1 hour is acceptable
        #-----------------------------------------------------------------------

        station_start64 = station_record['begin'].values
        station_end64 = station_record['end'].values

        start_c_day=station_start64.astype('datetime64[D]') #this values should overwrite begin, otherwise duplicates may appear as if begin YYYY-MM-DD 02:25:00 + 27 !!! 05:25:00
        start_p_hour=_np.roll(station_start64,1).astype('datetime64[h]')
        start_n_hour=_np.roll(station_start64,-1).astype('datetime64[h]')

        # end_c_day=station_record[:,3].astype('datetime64[D]')
        end_p_minute=_np.roll(station_end64,1).astype('datetime64[m]')
        end_n_hour=_np.roll(station_end64,-1).astype('datetime64[h]')


        B1c1 = (start_c_day-start_p_hour <= _np.timedelta64(24,'[h]'))&(start_c_day-start_p_hour >= _np.timedelta64(3,'[h]'))

        B1c2 = (start_c_day-end_p_minute <= _np.timedelta64(1,'[h]'))&(start_c_day-end_p_minute >= _np.timedelta64(0,'[m]')) #value should be positive

        B2c1 = (end_n_hour-start_c_day <= _np.timedelta64(48,'[h]'))&(end_n_hour-start_c_day >= _np.timedelta64(27,'[h]')) #start_c_day is the same as end_c_day
        
        B2c2 = (start_n_hour-start_c_day <= _np.timedelta64(25,'[h]'))&(start_n_hour-start_c_day >= _np.timedelta64(24,'[h]')) #check if next file is next day without missing days in between 
        
        
        completeness[B1c1 & B1c2 & B2c1 & B2c2 & (completeness==2)] = 3

        tmp_df = station_record.copy()
        tmp_df['completeness'] = completeness

        tmp_df['path_prev'] =  tmp_dir + _np.roll(station_record['path'].values,1) 
        tmp_df['path'] =  tmp_dir + station_record['path']
        tmp_df['path_next'] =  tmp_dir +_np.roll(station_record['path'].values,-1)

        dr_classes.append(tmp_df)
    return _pd.concat(dr_classes,axis=0)

def _merge(merge_set):
    '''Expects a merge set of 3 files [merge_start, merge_end,file_prev,file,file_next]. Merges all files into file120h. file1 must be a class 3 file
    Constructs 32h files with drMerge.py.
    Sample input:
    drMerge.py -i isba0940.15o.dr ohln0940.15o.dr -start 2015-04-04 00:00:00 -end 2015-04-04 04:00:00
    '''
    #Computing time boundaries of the merge. merge_set[1] is file begin time
    drMerge_proc = _Popen(['drMerge', str(merge_set['merge_begin']), str(merge_set['merge_end']), _os.path.basename(merge_set['path'])+'.30h',\
                merge_set['path_prev'], merge_set['path'], merge_set['path_next'] ],\
                cwd=_os.path.dirname(merge_set['path']))
    drMerge_proc.wait()

def dr_merge(merge_table,num_cores,tqdm):
    '''merge_table is the output of get_merge_table(). Merges all that is of class 3 as merge_table stores only files that are actual'''
    num_cores = int(num_cores) #safety precaution if str value is specified
    df_class3 =  merge_table[['begin','path_prev','path','path_next']][merge_table['completeness']==3].copy()
    
    df_class3['merge_begin'] = (df_class3['begin'].astype('datetime64[D]')  - _np.timedelta64( 3,'[h]') -J2000origin).astype('timedelta64[s]').astype(int)
    df_class3['merge_end'] = (df_class3['begin'].astype('datetime64[D]')  + _np.timedelta64( 27,'[h]') -J2000origin).astype('timedelta64[s]').astype(int)
    # merging to 2:55:00 df_class3['merge_end'] = (df_class3['begin'].astype('datetime64[D]')  + _np.timedelta64( 27,'[h]') - _np.timedelta64( 5,'[m]') -J2000origin).astype('timedelta64[s]').astype(int)

    merge_table_class3 = df_class3[['merge_begin','merge_end','path_prev','path','path_next']]

    
    # check if merged version already exists
    ifexists = _np.zeros((merge_table_class3.shape[0]))
    merged_paths = merge_table_class3['path']+'.30h'
    
    for i in range(merged_paths.shape[0]):
        ifexists[i] = _os.path.isfile(merged_paths.values[i])
    ifexists = ifexists.astype(bool)

    merge_table_class3_run = merge_table_class3[~ifexists]
    if  (merge_table_class3[~ifexists]).shape[0] == 0:
        print('All merge files present')

    else:
        num_cores = num_cores if merge_table_class3_run.shape[0] > num_cores else merge_table_class3_run.shape[0]
        
        print('Number of files to merge:', merge_table_class3_run.shape[0],'| Adj. num_cores:', num_cores)

        with _Pool(processes = num_cores) as p:
            if tqdm: list(_tqdm.tqdm_notebook(p.imap(_merge, merge_table_class3_run.to_records()), total=merge_table_class3_run.shape[0]))
            else: p.map(_merge, merge_table_class3_run.to_records())