import numpy as _np
import pandas as _pd
import os as _os
from subprocess import Popen as _Popen
from multiprocessing import Pool as _Pool

def rnx2dr_gen_paths(rnx_files,stations_list,tmp_dir):
    '''Creates an array of output paths for input rnx files. Concatanates it to the input rnx paths [[input_path,output path],...]. 
    This array is used for rnx to dr conversion. Input is the result of in gx_lib.aux.select_rnx function'''
    rnx_in_out = _np.ndarray((len(stations_list)),dtype=object)
    for i in range(len(stations_list)):
        tmp = _pd.Series(rnx_files[i]).str.split('/',expand=True)
        rnx_in_out[i] = _np.column_stack((rnx_files[i], 
                                         (tmp_dir+'/rnx_dr/'+stations_list[i]+ '/' + tmp.iloc[:,-3]
                                          +'/'+ tmp.iloc[:,-2]+'/'+ tmp.iloc[:,-1]+'.dr.gz').values))
    return rnx_in_out

def _2dr(rnx2dr_path):
    '''Opens process rxEditGde.py to convert specified rnx to dr file for GipsyX. The subprocess is used in order to run multiple instances at once.
    If converted file is already present, nothing happens'''
    out_dir = _os.path.dirname(rnx2dr_path[1])
    if not _os.path.exists(out_dir):
        _os.makedirs(out_dir)
    if not _os.path.isfile(rnx2dr_path[1]):
        process = _Popen(['rnxEditGde.py', '-dataFile', rnx2dr_path[0], '-o', _os.path.basename(rnx2dr_path[1])],cwd = out_dir)
        process.wait() 

def rnx2dr(rnx_files,stations_list,tmp_dir,num_cores):
    '''Runs rnxEditGde.py for each file in the class object in multiprocessing'''
    rnx2dr_paths = rnx2dr_gen_paths(rnx_files,stations_list,tmp_dir)
    num_cores = int(num_cores) #safety precaution if str value is specified
#         display(self.analyse())
    for i in range(len(stations_list)):
        print(stations_list[i],'station conversion to binary...')

        #Checking files that are already in place so not to overwrite
        if_exists_array = _np.ndarray((len(rnx2dr_paths[i])),dtype=bool)
        for j in range(len(if_exists_array)):
            if_exists_array[j] = not _os.path.exists(rnx2dr_paths[i][j,0])

        rnx2dr_paths_2convert = rnx2dr_paths[i][if_exists_array]

        if len(rnx2dr_paths_2convert) > 0:
            num_cores = num_cores if len(rnx2dr_paths_2convert[i]) > num_cores else len(rnx2dr_paths_2convert[i])
            chunksize = int(_np.ceil(len(rnx2dr_paths_2convert[i]) / num_cores))
            print ('Number of files to process:', len(rnx2dr_paths_2convert),'| Adj. num_cores:', num_cores,'| Chunksize:', chunksize,end=' ')

            pool = _Pool(processes=num_cores)
            pool.map_async(func=_2dr, iterable=rnx2dr_paths_2convert, chunksize=chunksize)
            pool.close()
            pool.join()
            print('| Done!')
        else:
            #In case length of unconverted files array is 0 - nothing will be converted
            print('Nothing to convert. All available rnx files are already converted')