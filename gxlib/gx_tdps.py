import numpy as _np, pandas as _pd
import sys as _sys
import os as _os
import calendar as _calendar
from multiprocessing import Pool as _Pool
PYGCOREPATH="{}/lib/python{}.{}".format(_os.environ['GCOREBUILD'], _sys.version_info[0], _sys.version_info[1])
if PYGCOREPATH not in _sys.path:
    _sys.path.insert(0,PYGCOREPATH)

import gipsyx.tropNom as _tropNom
import gcore.StationDataBase as _StationDataBase

from .gx_aux import J2000origin

def _gen_VMF1_tropNom(tropnom_param):
    '''Reads the staDb, gets list of station in the staDb, reads input arguments'''
    
    begin,end,tropNom_out,staDb,rate,VMF1_dir,stns  = tropnom_param
    
    '''begin, end, station_name, tropNom_out
    begin = tropnom begin in J2000 seconds; end = tropnom end in J2000 seconds; station name as in staDb;  '''
    if not _os.path.isfile(tropNom_out):
        if not _os.path.exists(_os.path.dirname(tropNom_out)):
            _os.makedirs(_os.path.dirname(tropNom_out))

        #begin, end, tdp_PATH
        nominals=_tropNom.nominalTrops('VMF1', modelFile=VMF1_dir)
        nominals.makeTdp(begin, end, rate, stns, tropNom_out, append=False, staDb=staDb, dry=True, wet=True)

def gen_tropnom(tmp_dir,staDb_dir,rate,VMF1_dir,num_cores):
    '''
    Generating tropnominal file for valid stations in staDb file.Takes number of years from dr_info.npz
    Had to create additional for loop as file no 31 gives error, no matter what year it is (tropNom read error of VMF1 file). tdp file is created for each observation file
    '''
    num_cores = int(num_cores)

    #Creates a staDb object
    staDb=_StationDataBase.StationDataBase() #creating staDb object
    staDb.read(staDb_dir) #reading staDb into staDb object
    stns = staDb.getStationList() #creating array with available station names
    
    drinfo_file = _np.load(file=tmp_dir+'/rnx_dr/drinfo.npz')
    drinfo_years_list = drinfo_file['years_list']

    #creating folder and file structure taking into account leap year.
    #resulting paths look as follows: year/doy/30h_tropNominal.vmf1
    #data on next day needed to create current day tropnominal
    days_in_year=_np.ndarray((len(drinfo_years_list)),dtype=int)


    for i in range(len(drinfo_years_list)):
        
        days_in_year[i] = int(365 + (1*_calendar.isleap(drinfo_years_list[i])))
        date = (_np.datetime64(str(drinfo_years_list[i])) + (_np.arange(days_in_year[i]).astype('timedelta64[D]'))) - J2000origin
        #Now all works correctly. The bug with wrong timevalues was corrected.
        begin = (date - _np.timedelta64(3,'[h]')).astype(int) 
        end = (date + _np.timedelta64(27,'[h]')).astype(int) 

        tropNom_out = (tmp_dir +'/tropNom/'+ str(drinfo_years_list[i])+'/'+_pd.Series(_np.arange(1,days_in_year[i]+1)).astype(str).str.zfill(3)+'/30h_tropNominalOut_VMF1.tdp').values

        staDb_nd    = _np.ndarray((tropNom_out.shape),dtype=object)
        rate_nd     = _np.ndarray((tropNom_out.shape),dtype=object)
        VMF1_dir_nd = _np.ndarray((tropNom_out.shape),dtype=object)
        stns_nd     = _np.ndarray((tropNom_out.shape),dtype=object)

        staDb_nd.fill(staDb); rate_nd.fill(rate); VMF1_dir_nd.fill(VMF1_dir); stns_nd.fill(stns)

        tropnom_param = _np.column_stack((begin,end,tropNom_out,staDb_nd,rate_nd,VMF1_dir_nd,stns_nd))
        
            
        
        num_cores = num_cores if len(tropnom_param) > num_cores else len(tropnom_param)
        step_size = int(_np.ceil(len(tropnom_param) / num_cores))

        print(drinfo_years_list[i],'year tropnominals generation...',end=' ')
        print ('Number of files to process:', len(tropnom_param),'| Adj. num_cores:', num_cores)

        for i in range(step_size):
            try:
                pool = _Pool(num_cores)
                pool.map(_gen_VMF1_tropNom, tropnom_param[_np.arange(i, len(tropnom_param), step_size)])
            finally:
                pool.close()
                pool.join()
        print('| Done!')
    # return tropnom_param