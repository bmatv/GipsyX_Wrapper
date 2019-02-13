import numpy as _np
import os as _os
from subprocess import Popen as _Popen
from multiprocessing import Pool as _Pool

from .gx_aux import J2000origin


def get_merge_table(tmp_dir):
    ''' tmp_dir is expected to have drinfo.npz file produced by get_drinfo function
    Analyses the properties of dr files and outputs classified dataset where class 3 files can be meged to 30 hours files centerd on the midday.
    Currently there are no special cases for the very first and last files of the station as if merged non-symmetrically won't be centred'''
    drinfo_file = _np.load(file=tmp_dir+'/rnx_dr/drinfo.npz')
    drinfo = drinfo_file['drinfo']
    
    #function for gps records. Othervise no-gps files won't be processed and will always be present in gd2e output
    def hasGPS(arr):
        return _np.max(_np.isin(arr,'G')) 
    

    '''Creating classes according to record length'''
    dr_classes = _np.ndarray((len(drinfo)),dtype=object)
    for i in range(len(drinfo)):
        
        gps_transmitter = _np.ndarray((len(drinfo[i])),dtype=bool)
        for j in range(len(drinfo[i])):
            gps_transmitter[j] = hasGPS(drinfo[i][j][-2])
        gps_drinfo = drinfo[i][gps_transmitter]
        
        
        station_record = gps_drinfo #filtered station record
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

        # start_c - start_p         <=24h & > 2h        # end_n   - start_c + 24h   <=48h & > 26h
        #  day      hour                                #  hour     day

        # start_c - end_p           <1h   & >=0h        # start_n - start_c + 24h   <25h  & >=24h
        #  day      hour                                #  hour     day
        #-----------------------------------------------------------------------


        start_c=station_record[:,2]
        start_p=_np.roll(station_record[:,2],1)
        start_n=_np.roll(station_record[:,2],-1)

        end_c=station_record[:,3]
        end_p=_np.roll(station_record[:,3],1)
        end_n=_np.roll(station_record[:,3],-1)

        B1c1 = (start_c.astype('datetime64[D]')-start_p.astype('datetime64[h]') <= _np.timedelta64(24,'[h]'))\
        &(start_c.astype('datetime64[D]')-start_p.astype('datetime64[h]') > _np.timedelta64(2,'[h]'))

        B1c2 = (start_c.astype('datetime64[D]')-end_p.astype('datetime64[m]') < _np.timedelta64(1,'[h]'))\
        &(start_c.astype('datetime64[D]')-end_p.astype('datetime64[m]') >= _np.timedelta64(0,'[m]'))

        B2c1 = (end_n.astype('datetime64[h]')-end_c.astype('datetime64[D]') <= _np.timedelta64(48,'[h]'))\
        &(end_n.astype('datetime64[h]')-end_c.astype('datetime64[D]') > _np.timedelta64(26,'[h]'))

        B2c2 = (start_n.astype('datetime64[h]')-end_c.astype('datetime64[D]') < _np.timedelta64(25,'[h]'))\
        &(start_n.astype('datetime64[h]')-end_c.astype('datetime64[D]') >= _np.timedelta64(24,'[h]'))


#             completeness[(B1c1 & B1c2 & B2c1 & B2c2 & completeness==2)] = 3

        completeness[B1c1 & B1c2 & B2c1 & B2c2 & (completeness==2)] = 3
        dr_classes[i] = _np.column_stack((completeness,
                                            station_record[:,2], #record start time
                                            station_record[:,3], #record end time
                                            _np.roll(station_record[:,7],1),
                                            station_record[:,7],
                                            _np.roll(station_record[:,7],-1)
                                        ))
        #     return dataRecordInfo
    return dr_classes

def _merge(merge_set):
    '''Expects a merge set of 3 files [class,time,file0,file1,file2]. Merges all files into file1_30h. file1 must be a class 3 file
    Constructs 30h arcs with drMerge.py.
    Sample input:
    drMerge.py -i isba0940.15o.dr ohln0940.15o.dr -start 2015-04-04 00:00:00 -end 2015-04-04 04:00:00
    '''
    if not _os.path.isfile((merge_set[4])[:-6]+'_30h.dr.gz'):
        #Computing time boundaries of the merge
        merge_begin = ((merge_set[1].astype('datetime64') - _np.timedelta64( 3,'[h]'))-J2000origin).astype('timedelta64[s]').astype(int).astype(str)
        merge_end =   ((merge_set[1].astype('datetime64') + _np.timedelta64(27,'[h]'))-J2000origin).astype('timedelta64[s]').astype(int).astype(str)

        drMerge_proc = _Popen(['drMerge', merge_begin, merge_end,\
                    _os.path.basename(merge_set[4])[:-6]+'_30h.dr.gz',\
                    merge_set[3], merge_set[4], merge_set[5] ],\
                    cwd=_os.path.dirname(merge_set[4]))
        drMerge_proc.wait()

def dr_merge(merge_table,stations_list,num_cores):
    '''merge_table is the output of get_merge_table()'''
    num_cores = int(num_cores) #safety precaution if str value is specified


    for i in range(len(stations_list)):
        num_cores = num_cores if len(merge_table[i]) > num_cores else len(merge_table[i])
        chunksize = int(_np.ceil(len(merge_table[i]) / num_cores))
        merge_table_class3 = merge_table[i][merge_table[i][:,0]==3]

        print(stations_list[i],'station binary files merging (class_3 only)...')
        print ('Number of files to process:', len(merge_table_class3),'| Adj. num_cores:', num_cores,'| Chunksize:', chunksize,end=' ')
        pool = _Pool(processes=num_cores)

        pool.map_async(func=_merge, iterable=merge_table_class3, chunksize=chunksize)
        pool.close()
        pool.join()
        print('| Done!')