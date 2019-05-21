import os as _os,sys as _sys
import numpy as _np
import pandas as _pd
import tqdm as _tqdm
import multiprocessing as _mp
from multiprocessing import Pool as _Pool
from shutil import rmtree as _rmtree

from .gx_aux import J2000origin as _J2000origin

_sys.path.insert(0, "{}/lib/python{}.{}".format(_os.environ['GCOREBUILD'], \
                _sys.version_info[0], _sys.version_info[1]))

import gcore.IgsGcoreConversions as _IgsGcoreConversions

_DEFAULT_COEFF=_os.path.expandvars('$GOA_VAR/sta_info/otide_cmcoeff_got48ac')

from gcore.GNSSproducts import FetchGNSSproducts

'''Function to convert date to gps week and day number
Expects single value of date to convert or an array of dates.
Outputs string ndarray of igs type week numbers where day number (Sunday is 0) is concatanated to the gps week number
Available products (GNSS CDDIS) = ['mit', 'ngs', 'igr', 'gfz', 'jpl', 'sio', 'igs', 'esa', 'grg','emr', 'igl']

products_igs2gipsyx
Repro2 products should be used. IGS08b.
GipsyX gcore.IgsGcoreConversions doesn't support IGS05 conversion

For GFZ products: ftp://ftp.gfz-potsdam.de/GNSS/products/repro2

CDDIS ftp:
rclone sync cddis:/gnss/products /mnt/Data/bogdanm/Products/IGS_GNSS_Products/ -vv --transfers 10 --checkers 10 --include "/15[6-9][0-9]/repro2/es2*{.sp3.Z,.clk.Z}"
rclone sync cddis:/gnss/products /mnt/Data/bogdanm/Products/IGS_GNSS_Products/ -vv --transfers 10 --checkers 10 --include "/16[0-9][0-9]/repro2/es2*{.sp3.Z,.clk.Z}"
'''
_GPSorigin = _np.datetime64('1980-01-06 00:00:00')
_seconds_week = 604800

def _date2igs(date):
    gps_seconds = (date - _GPSorigin).astype(_np.int)
    gps_week = gps_seconds//_seconds_week
    day_in_week = ((gps_seconds%_seconds_week)/86400).astype(_np.int)
    return gps_week.astype(_np.str).astype(object), day_in_week.astype(_np.str).astype(object)

def _gen_sets(begin,end,products_type,products_dir):
    '''Generates filenames list'''
    products_dir = _os.path.abspath(products_dir)
    
    begin64 = _np.datetime64(begin).astype('datetime64[D]') #Explicitly rounding to days as we don't care about hours,minutes etc.
    end64 = _np.datetime64(end).astype('datetime64[D]')
    date_array = _np.arange(begin64,end64)
    date_array_J2000 = (date_array - _J2000origin).astype('timedelta64[s]').astype(_np.int)
    
    gps_week,day_in_week = _date2igs(date_array)
    igs_days = gps_week+day_in_week

    years = date_array.astype('datetime64[Y]').astype(_np.str).astype(object)
#     return igs_days+years+'cod'
    if products_type == 'esa':
        sp3_path = products_dir + '/' + gps_week+ '/' + products_type +igs_days +'.sp3.Z'
        clk_path = products_dir + '/' + gps_week+ '/' + products_type +igs_days +'.clk.Z'
    elif products_type == 'es2':
        sp3_path = products_dir + '/' + gps_week+ '/repro2/' + products_type +igs_days +'.sp3.Z'
        clk_path = products_dir + '/' + gps_week+ '/repro2/' + products_type +igs_days +'.clk.Z'
    elif products_type == 'co2':
        sp3_path = products_dir + '/' + gps_week+ '/repro2/' + products_type +igs_days +'.eph.Z'
        clk_path = products_dir + '/' + gps_week+ '/repro2/' + 'es2' +igs_days +'.clk.Z' #taking clocks from esa reprocessed
    elif products_type == 'co2015':
        products_type=products_type.upper()
        #We expect the clk files to be corrected for the message
        sp3_path = products_dir + '/' + years+ '/' + products_type  +igs_days +'.EPH.Z'

        clk_path = products_dir + '/' + years+ '/'+ products_type + igs_days +'.CLK.Z'
    else:
        raise Exception('Product type not understood. Please check.')
        
    #checking if files are locally available
    sp3_path_avail_mask = _np.asarray([_os.path.isfile(f) for f in sp3_path])
    clk_path_avail_mask = _np.asarray([_os.path.isfile(f) for f in clk_path])
    
    sp3_avail= sp3_path[sp3_path_avail_mask].shape[0]/igs_days.shape[0]
    sp3_unavail = sp3_path[~sp3_path_avail_mask].shape[0]/igs_days.shape[0]
    
    clk_avail = clk_path[clk_path_avail_mask].shape[0]/igs_days.shape[0]
    clk_unavail = clk_path[~clk_path_avail_mask].shape[0]/igs_days.shape[0]


    print('sp3: found {}%. missing {}%'.format(sp3_avail*100,sp3_unavail*100))
    print('clk: found {}%. missing {}%'.format(clk_avail*100,clk_unavail*100))
    if clk_unavail>0:
        return(clk_unavail)
    
    if (sp3_avail == 1) & (clk_avail ==1):
        print('All files located. Starting conversion...')
        out_dir = _os.path.abspath(_os.path.join(products_dir,_os.pardir,'igs2gipsyx','products_type'))
        out_array = _np.ndarray((date_array.shape),dtype=object)
        out_array.fill(out_dir) #filling with default values
        out_array = out_array + '/' + date_array.astype('datetime64[Y]').astype(str) #updating out paths with year folders

        tmp_dir = _os.path.join(out_dir,'tmp') #creating tmp directory processes will work in
        if not _os.path.isdir(tmp_dir): _os.makedirs(tmp_dir) #this should automatically create out and tmp dirs

        [_os.makedirs(out_path) for out_path in out_array if not _os.path.exists(out_path)] #creating unique year directories
        return _pd.DataFrame(_np.column_stack((sp3_path,clk_path,date_array,date_array_J2000,out_array)),columns = ['sp3','clk', 'date', 'dateJ','out'])
    
def _sp3ToPosTdp(np_set):
    
    process = _mp.current_process()

    tmp_dir = _os.path.abspath(_os.path.join(np_set['out'],_os.pardir,_os.pardir,'tmp',str(process._identity[0])))
    #creates tmp dirs in igs2gipsyx directory
    if not _os.path.isdir(tmp_dir): _os.makedirs(tmp_dir)
    _os.chdir(tmp_dir)
    
    
    frame = _IgsGcoreConversions.sp3ToPosTdp(np_set['sp3'], 
                                    _os.path.join(np_set['out'], str(np_set['date'])+'.pos.gz'), 
                                    _DEFAULT_COEFF,igsCm=True, workDir=tmp_dir, 
                                    tdpOut=None)
    
    refClk = _IgsGcoreConversions.clkToTdp(np_set['clk'], 
                                    _os.path.join(np_set['out'], str(np_set['date'])+'.tdp.gz'), 
                                    stationClk=False)
    
    miscProducts = _IgsGcoreConversions.ConvertedGcoreProds(np_set['dateJ'], np_set['out'], refClk, frame )
    miscProducts.make()

def igs2jpl(begin,end,products_type,products_dir,tqdm,num_cores=None):
    sets = _gen_sets(begin,end,products_type,products_dir).to_records()
    
    with _Pool(num_cores) as p:
        if tqdm: list(_tqdm.tqdm_notebook(p.imap(_sp3ToPosTdp, sets), total=sets.shape[0]))
        else: p.map(_sp3ToPosTdp, sets)
    
    tmp_dir = _os.path.abspath(_os.path.join(products_dir,_os.pardir,'igs2gipsyx','tmp'))
    _rmtree(tmp_dir) #cleaning tmp directory as newer instances of process_id will create mess


def jpl2merged_orbclk(begin,end,GNSSproducts_dir,num_cores=None,h24_bool=True,makeShadow_bool=True,tqdm=True):
    begin64 = _np.datetime64(begin).astype('datetime64[D]')
    end64 = _np.datetime64(end).astype('datetime64[D]')
    products_day = _np.arange(begin64,end64)
    products_begin = ((products_day - _np.timedelta64(3,'h')) - _J2000origin).astype(int)
    products_end = (products_day + _np.timedelta64(27,'h') - _J2000origin).astype(int)
    
    
    dayofyear_str = (_pd.Series(products_day).dt.dayofyear).astype(str).str.zfill(3)
    year_str =  (_pd.Series(products_day).dt.year).astype(str).str.zfill(3)
    
    output_merged_dir = _os.path.abspath(GNSSproducts_dir)
    target_dir = _os.path.abspath(_os.path.join(output_merged_dir,_os.pardir,'init')) +'/' + year_str + '/'+ dayofyear_str
    

    
    repository = _np.ndarray((products_day.shape),object)
    h24 = _np.ndarray((products_day.shape),bool)
    makeShadow = _np.ndarray((products_day.shape),bool)
    
    repository.fill(GNSSproducts_dir)
    h24.fill(h24_bool)
    makeShadow.fill(makeShadow_bool)
    
    input_sets = _np.column_stack([products_begin,products_end,repository,target_dir,h24,makeShadow])
#     return input_sets
    with _Pool(processes = num_cores) as p:
        if tqdm: list(_tqdm.tqdm_notebook(p.imap(_gen_orbclk, input_sets), total=input_sets.shape[0]))
        else: p.map(_gen_orbclk, input_sets)


def _gen_orbclk(input_set):
    startTime = input_set[0]
    endTime = input_set[1]
    GNSSproducts = input_set[2]
    targetDir = input_set[3]
    h24 = input_set[4]
    makeShadow = input_set[5]
    
    #check if target folder exists and create one if not
    if not _os.path.exists(targetDir):
        _os.makedirs(targetDir)
        
    args = ['/home/bogdanm/Desktop/GipsyX_Wrapper/fetchGNSSproducts_J2000.py',
                      '-startTime',str(startTime),
                      '-endTime', str(endTime),
                      '-GNSSproducts', GNSSproducts,
                      '-targetDir', targetDir+'/']
    args.append( '-hr24') if h24 else None
    args.append ('-makeShadowFile') if makeShadow else None

    
    process = _Popen(args,stdout=_PIPE)
    out, err = process.communicate()
    return out,err