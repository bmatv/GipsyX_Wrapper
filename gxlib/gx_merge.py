import numpy as _np
import os as _os
from subprocess import Popen as _Popen
from multiprocessing import Pool as _Pool
import tqdm as _tqdm
from .gx_aux import J2000origin


def get_merge_table(tmp_dir,mode=None):
    '''
    Reads drInfo file and outputs merge_table for all available stations in drInfo in the same order.

    Because of JPL's specific 30 hour products for GPS GipsyX is checking if centerd file is 30 hours and if so:
    fetch one product day even with 24 hours products as ESA. To make GipsyX fetch more product days - 32 hour files 
    should be created. In this case GipsyX will understand that 30h products are not enought and will extract three
    days of products. This completely solves the problem with products extrapolation and gives ability of proper 
    processing of 30 hour files as GPS as GLONASS successfully overcoming day-boundary effects.

    tmp_dir is expected to have drinfo.npz file produced by get_drinfo function
    Analyses the properties of dr files and outputs classified dataset where class 3 files can be meged to 32 hours files centered on the midday.
    Currently there are no special cases for the very first and last files of the station as if merged non-symmetrically won't be centred'''
    drinfo_file = _np.load(file=tmp_dir+'/rnx_dr/drinfo.npz',allow_pickle=True) #should overwrite to dump_zstd. This is a new security change inroduced to numpy
    drinfo = drinfo_file['drinfo']
    
    modes = [None, 'GPS', 'GLONASS','GPS+GLONASS']
    if mode not in modes:
        raise ValueError("Invalid mode. Expected one of: %s" % modes)


    '''Creating classes according to record length'''
    dr_classes = _np.ndarray((drinfo.shape[0]),dtype=object)
    for i in range(drinfo.shape[0]):
        if mode is None:
            station_record = drinfo[i]
        elif mode == 'GPS':
            station_record = drinfo[i][drinfo[i][:,-3] == True]
        elif mode == 'GLONASS':
            station_record = drinfo[i][drinfo[i][:,-2] == True]
        elif mode == 'GPS+GLONASS':
            station_record = drinfo[i][(drinfo[i][:,-3] == True)&(drinfo[i][:,-2] == True)]
        
        if len(station_record) == 0:
            raise ValueError("No data found for mode {} for station {}".format(mode,i))

#         station_record = gps_drinfo #filtered station record
        completeness = _np.zeros((len(station_record)),dtype=_np.int)
        drinfo_rec_time = (station_record[:,3].astype('datetime64[h]')-station_record[:,2].astype('datetime64[h]')).astype(_np.int)
        
        #-----------------------------------------------------------------------
        # Basic filtering module that uses total length of the datarecord.
        # records with more than 12 hours of data but less than 20 hours of data get 1
        completeness[((drinfo_rec_time>=12) & ((drinfo_rec_time)<20))]=1

        #records with more than 20 hours of data get 2
        completeness[(drinfo_rec_time>=20)]=2
        #-----------------------------------------------------------------------

        # BOUNDARY_1                                    # BOUNDARY_2

        # start_c - start_p         <=24h & >=4h        # end_n   - start_c  <=48h & >=28h
        #  day      hour                                #  hour     day

        # start_c - end_p           <=1h  & >=0m        # start_n - start_c  <=25h  & >=24h | Only gaps of up to 1h are accepted
        #  day      hour                                #  hour     day
        # Missing data of 1 hour is acceptable
        #-----------------------------------------------------------------------


        start_c_day=station_record[:,2].astype('datetime64[D]')
        start_p_hour=_np.roll(station_record[:,2],1).astype('datetime64[h]')
        start_n_hour=_np.roll(station_record[:,2],-1).astype('datetime64[h]')

        # end_c_day=station_record[:,3].astype('datetime64[D]')
        end_p_minute=_np.roll(station_record[:,3],1).astype('datetime64[m]')
        end_n_hour=_np.roll(station_record[:,3],-1).astype('datetime64[h]')


        B1c1 = (start_c_day-start_p_hour <= _np.timedelta64(24,'[h]'))&(start_c_day-start_p_hour >= _np.timedelta64(3,'[h]'))

        B1c2 = (start_c_day-end_p_minute <= _np.timedelta64(1,'[h]'))&(start_c_day-end_p_minute >= _np.timedelta64(0,'[m]')) #value should be positive

        B2c1 = (end_n_hour-start_c_day <= _np.timedelta64(48,'[h]'))&(end_n_hour-start_c_day >= _np.timedelta64(27,'[h]')) #start_c_day is the same as end_c_day
        
        B2c2 = (start_n_hour-start_c_day <= _np.timedelta64(25,'[h]'))&(start_n_hour-start_c_day >= _np.timedelta64(24,'[h]')) #check if next file is next day without missing days in between 
        
         
        completeness[B1c1 & B1c2 & B2c1 & B2c2 & (completeness==2)] = 3
        dr_classes[i] = _np.column_stack((completeness,
                                            station_record[:,2], #record start time
                                            station_record[:,3], #record end time
                                            _np.roll(station_record[:,-1],1), #filename previous
                                            station_record[:,-1], #filename
                                            _np.roll(station_record[:,-1],-1), #filename next
                                          
                                        ))
        #     return dataRecordInfo
    return dr_classes

def _merge(merge_set):
    '''Expects a merge set of 3 files [class,time,file0,file1,file2]. Merges all files into file1_20h. file1 must be a class 3 file
    Constructs 32h files with drMerge.py.
    Sample input:
    drMerge.py -i isba0940.15o.dr ohln0940.15o.dr -start 2015-04-04 00:00:00 -end 2015-04-04 04:00:00
    '''
    if not _os.path.isfile((merge_set[4])[:-6]+'_30h.dr.gz'):
        #Computing time boundaries of the merge. merge_set[1] is file begin time
        merge_begin = ((merge_set[1].astype('datetime64[D]') - _np.timedelta64( 3,'[h]'))-J2000origin).astype('timedelta64[s]').astype(int).astype(str)
        merge_end =   ((merge_set[1].astype('datetime64[D]') + _np.timedelta64(27,'[h]'))-J2000origin).astype('timedelta64[s]').astype(int).astype(str)

        drMerge_proc = _Popen(['drMerge', merge_begin, merge_end,\
                    _os.path.basename(merge_set[4])[:-6]+'_30h.dr.gz',\
                    merge_set[3], merge_set[4], merge_set[5] ],\
                    cwd=_os.path.dirname(merge_set[4]))
        drMerge_proc.wait()

def dr_merge(merge_table,stations_list,num_cores,tqdm):
    '''merge_table is the output of get_merge_table()'''
    num_cores = int(num_cores) #safety precaution if str value is specified


    for i in range(len(stations_list)):
        num_cores = num_cores if len(merge_table[i]) > num_cores else len(merge_table[i])
        merge_table_class3 = merge_table[i][merge_table[i][:,0]==3]

        print(stations_list[i],'station binary files merging (class_3 only)...')
        print ('Number of files to process:', len(merge_table_class3),'| Adj. num_cores:', num_cores)

        with _Pool(processes = num_cores) as p:
            if tqdm: list(_tqdm.tqdm_notebook(p.imap(_merge, merge_table_class3), total=merge_table_class3.shape[0]))
            else: p.map(_merge, merge_table_class3)