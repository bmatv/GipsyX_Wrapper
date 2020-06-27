import os as _os,sys as _sys
import numpy as _np
import pandas as _pd
import tqdm as _tqdm
import glob as _glob
import multiprocessing as _mp
from subprocess import Popen as _Popen, PIPE as _PIPE
from multiprocessing import Pool as _Pool
from shutil import rmtree as _rmtree, move as _move, copy as _copy

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

def _gen_sets(begin,end,products_type,products_dir,run_dir):
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
    if (products_type == 'gfz')or(products_type == 'grg'):
        sp3_path = products_dir + '/' + gps_week+ '/' + products_type +igs_days +'.sp3.Z'
        clk_path = products_dir + '/' + gps_week+ '/' + products_type +igs_days +'.clk.Z'
    if (products_type == 'jxf'):
        sp3_path = products_dir + '/' + gps_week+ '/' + products_type +igs_days +'.sp3.Z'
        clk_path = products_dir + '/' + gps_week+ '/' + products_type +igs_days +'.clk_30s.Z' #only 30s clk files present
    elif (products_type == 'esa'):
        igs_days_num = igs_days.astype(int)
        boudary_date = 17696 # according to docu it should be 17726 : according to CNES recommendations to use rouutine grg after 28/12/2013
        reprocessed_bool = igs_days_num<=boudary_date      # 
        non_reprocessed_bool =  igs_days_num>boudary_date  #
        
        sp3_path_non_repro = products_dir + '/' + gps_week[non_reprocessed_bool]+ '/' + products_type +igs_days[non_reprocessed_bool] +'.sp3.Z'
        clk_path_non_repro = products_dir + '/' + gps_week[non_reprocessed_bool]+ '/' + products_type +igs_days[non_reprocessed_bool] +'.clk.Z'

        sp3_path_repro = products_dir + '/' + gps_week[reprocessed_bool]+ '/repro2/' + '{}2'.format(products_type[:2]) +igs_days[reprocessed_bool] +'.sp3.Z'
        clk_path_repro = products_dir + '/' + gps_week[reprocessed_bool]+ '/repro2/' + '{}2'.format(products_type[:2]) +igs_days[reprocessed_bool] +'.clk.Z'
        
        sp3_path = _np.concatenate([sp3_path_repro,sp3_path_non_repro])
        clk_path = _np.concatenate([clk_path_repro,clk_path_non_repro])

        # if (igs_days[reprocessed_bool].shape[0]>0)&(igs_days[non_reprocessed_bool].shape[0]>0):
        #     sp3_path = _np.concatenate([sp3_path_repro,sp3_path_non_repro])
        #     clk_path = _np.concatenate([clk_path_repro,clk_path_non_repro])
        # elif (igs_days[reprocessed_bool].shape[0]>0)&(igs_days[non_reprocessed_bool].shape[0]==0):
        #     sp3_path = sp3_path_repro
        #     clk_path = clk_path_repro
        # elif (igs_days[reprocessed_bool].shape[0]==0)&(igs_days[non_reprocessed_bool].shape[0]>0):
        #     sp3_path = sp3_path_non_repro
        #     clk_path = clk_path_non_repro
        # else:
        #     raise Exception('Something wrong. No files selected for conversion')

    # elif (products_type == 'cod')or(products_type == 'cof'):
    #     sp3_path = products_dir + '/' + gps_week+ '/' + products_type +igs_days +'.eph.Z'
    #     clk_path = products_dir + '/' + gps_week+ '/' + products_type +igs_days +'.clk.Z'
    elif (products_type == 'es2')or(products_type == 'ig2')or(products_type == 'jp2'): #es2 is complete with clk and sp3
        sp3_path = products_dir + '/' + gps_week+ '/repro2/' + products_type +igs_days +'.sp3.Z'
        clk_path = products_dir + '/' + gps_week+ '/repro2/' + products_type +igs_days +'.clk.Z'
    elif products_type == 'gr2': #es2 and gr2 are complete with clk and sp3
        igs_days_num = igs_days.astype(int)
        boudary_date = 17696 # according to docu it should be 17726 : according to CNES recommendations to use rouutine grg after 28/12/2013
        reprocessed_bool = igs_days_num<=boudary_date      # 
        non_reprocessed_bool =  igs_days_num>boudary_date  #
        
        sp3_path_repro = products_dir + '/' + gps_week[reprocessed_bool]+ '/repro2/' + products_type +igs_days[reprocessed_bool] +'.sp3.Z'
        clk_path_repro = products_dir + '/' + gps_week[reprocessed_bool]+ '/repro2/' + products_type +igs_days[reprocessed_bool] +'.clk.Z'

        sp3_path_non_repro = products_dir + '/' + gps_week[non_reprocessed_bool]+ '/' + 'grg' +igs_days[non_reprocessed_bool] +'.sp3.Z'
        clk_path_non_repro = products_dir + '/' + gps_week[non_reprocessed_bool]+ '/' + 'grg' +igs_days[non_reprocessed_bool] +'.clk.Z'

        if (igs_days[reprocessed_bool].shape[0]>0)&(igs_days[non_reprocessed_bool].shape[0]>0):
            sp3_path = _np.concatenate([sp3_path_repro,sp3_path_non_repro])
            clk_path = _np.concatenate([clk_path_repro,clk_path_non_repro])
        elif (igs_days[reprocessed_bool].shape[0]>0)&(igs_days[non_reprocessed_bool].shape[0]==0):
            sp3_path = sp3_path_repro
            clk_path = clk_path_repro
        elif (igs_days[reprocessed_bool].shape[0]==0)&(igs_days[non_reprocessed_bool].shape[0]>0):
            sp3_path = sp3_path_non_repro
            clk_path = clk_path_non_repro
        else:
            raise Exception('Something wrong. No files selected for conversion')
    elif (products_type == 'co2')or(products_type == 'cf2'): #cf2 and co2 have same paths except for type_name
        sp3_path = products_dir + '/' + gps_week+ '/repro2/' + products_type +igs_days +'.eph.Z'
        clk_path = products_dir + '/' + gps_week+ '/repro2/' + 'es2' +igs_days +'.clk.Z' #taking clocks from esa reprocessed
    elif products_type == 'co2015':
        #We expect the clk files to be corrected for the message
        sp3_path = products_dir + '/' + years+ '/' + 'COD'  +igs_days +'.EPH.Z'
        clk_path = products_dir + '/' + years+ '/'+ 'COD' + igs_days +'.CLK.Z'
    elif products_type == 'cod':
        #We expect the clk files to be corrected for the message
        sp3_path = products_dir + '/' + years+ '/' + 'COD'  +igs_days +'.EPH.Z'
        clk_path = products_dir + '/' + years+ '/'+ 'COD' + igs_days +'.CLK.Z'
    elif products_type == 'com':
        #We expect the clk files to be corrected for the message
        #Use COD operational parts of data before 2014-01-01
        products_type = products_type.upper()
        igs_days_num = igs_days.astype(int)
        boudary_date = 17733 # 2014-01-01
        reprocessed_bool = igs_days_num<boudary_date      # 
        non_reprocessed_bool =  igs_days_num>=boudary_date  #
        if reprocessed_bool.sum() >0: print('using COD type products to cover pre 2014-01-01')
        
        sp3_path_non_repro = products_dir + '/' + years[non_reprocessed_bool] + '/' + products_type + igs_days[non_reprocessed_bool] +'.EPH.Z'
        clk_path_non_repro = products_dir + '/' + years[non_reprocessed_bool] + '/' + products_type + igs_days[non_reprocessed_bool] +'.CLK.Z'

        products_dir_repro = _os.path.abspath(_os.path.join(products_dir,_os.path.pardir))
        sp3_path_repro = products_dir_repro + '/CODE/' + '/' + years[reprocessed_bool] + '/' + '{}D'.format(products_type[:2]) +igs_days[reprocessed_bool] +'.EPH.Z'
        clk_path_repro = products_dir_repro + '/CODE/' + '/' + years[reprocessed_bool] + '/' + '{}D'.format(products_type[:2]) +igs_days[reprocessed_bool] +'.CLK.Z'
        
        sp3_path = _np.concatenate([sp3_path_repro,sp3_path_non_repro])
        clk_path = _np.concatenate([clk_path_repro,clk_path_non_repro])

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
    if (sp3_path[~sp3_path_avail_mask].shape[0] != 0):
        
        return( sp3_path[~sp3_path_avail_mask],clk_path[~clk_path_avail_mask])

    
    if (sp3_avail == 1) & (clk_avail ==1):
        print('All files located. Starting conversion...')
        if (products_type.lower() == 'com') or (products_type.lower() == 'co2015') or (products_type.lower() == 'cod'):
            out_dir = _os.path.abspath(_os.path.join(products_dir,_os.pardir,_os.pardir,'igs2gipsyx',products_type.lower()))
            print(out_dir)
        else:
            out_dir = _os.path.abspath(_os.path.join(products_dir,_os.pardir,'igs2gipsyx',products_type.lower()))
        #'/mnt/data/bogdanm/Products/CODE/igs2gipsyx/com/'

        out_array = _np.ndarray((date_array.shape),dtype=object)
        out_array.fill(out_dir) #filling with default values
        out_array = out_array + '/' + date_array.astype('datetime64[Y]').astype(str) #updating out paths with year folders

        tmp_dir = _os.path.join(run_dir,'tmp_igs2jpl') #creating tmp directory processes will work in
        if _os.path.isdir(tmp_dir): _rmtree(tmp_dir) #clearing memory before processing
        _os.makedirs(tmp_dir) #this should automatically create out and tmp dirs
        tmp_array = _np.ndarray((date_array.shape),dtype=object)
        tmp_array.fill(tmp_dir) #filling with default values

        [_os.makedirs(out_path) for out_path in out_array if not _os.path.exists(out_path)] #creating unique year directories
        return _pd.DataFrame(_np.column_stack((sp3_path,clk_path,date_array,date_array_J2000,out_array,tmp_array)),columns = ['sp3','clk', 'date', 'dateJ','out','tmp'])
    
def _sp3ToPosTdp(np_set):
    
    process = _mp.current_process()

    tmp_dir = _os.path.abspath(_os.path.join(np_set['tmp'],str(process._identity[0])))
    #creates tmp dirs in igs2gipsyx directory #'/mnt/data/bogdanm/Products/CODE/igs2gipsyx/com/tmp'
                                              # /mnt/data/bogdanm/Products/CODE/igs2gipsyx/COM/tmp
    if not _os.path.isdir(tmp_dir): _os.makedirs(tmp_dir)
    _os.chdir(tmp_dir)
    
    # print(np_set['sp3'],np_set['out'])
    frame = _IgsGcoreConversions.sp3ToPosTdp(np_set['sp3'], 
                                    _os.path.join(np_set['out'], str(np_set['date'])+'.pos.gz'), 
                                    _DEFAULT_COEFF,igsCm=True, workDir=tmp_dir, 
                                    tdpOut=None)
    
    refClk = _IgsGcoreConversions.clkToTdp(np_set['clk'], 
                                    _os.path.join(np_set['out'], str(np_set['date'])+'.tdp.gz'), 
                                    stationClk=False)
    
    miscProducts = _IgsGcoreConversions.ConvertedGcoreProds(np_set['dateJ'], np_set['out'], refClk, frame)
    miscProducts.make()

def igs2jpl(begin,end,products_type,products_dir,tqdm,num_cores=None,run_dir = '/run/user/1017/'):
    #products_dir = '/mnt/data/bogdanm/Products/CODE/source/MGEX/'
    sets = _gen_sets(begin,end,products_type,products_dir,run_dir = run_dir)
    sets = sets.to_records()
    
    with _Pool(num_cores) as p:
        if tqdm: list(_tqdm.tqdm_notebook(p.imap(_sp3ToPosTdp, sets), total=sets.shape[0]))
        else: p.map(_sp3ToPosTdp, sets)
    

    tmp_dir = _os.path.join(run_dir,'tmp_igs2jpl') #creating tmp directory processes will work in
    try:_rmtree(tmp_dir) #clearing memory before processing
    except: print('Could not remove tmp')
    # tmp_dir = _os.path.abspath(_os.path.join(products_dir,_os.pardir,_os.pardir,'igs2gipsyx',products_type.lower(),'tmp'))
    #'/mnt/data/bogdanm/Products/CODE/igs2gipsyx/com/tmp'
    
    #cleaning tmp directory as newer instances of process_id will create mess


def jpl2merged_orbclk(begin,end,GNSSproducts_dir,num_cores=None,h24_bool=True,makeShadow_bool=True,tqdm=True,run_dir = '/run/user/1017/'):
    begin64 = _np.datetime64(begin).astype('datetime64[D]')
    end64 = _np.datetime64(end).astype('datetime64[D]')
    products_day = _np.arange(begin64,end64)
    products_begin = ((products_day - _np.timedelta64(3,'h')) - _J2000origin).astype(int)
    products_end = (products_day + _np.timedelta64(27,'h') - _J2000origin).astype(int)
    #rewriting 1st and last values. These are 27 hour products precisely according to boundaries specified
    products_begin[0] = (products_day[0] - _J2000origin).astype(int)
    products_end[-1] = (products_day[-1] + _np.timedelta64(24,'h') - _np.timedelta64(5,'m')- _J2000origin).astype(int)

    year_str =  (_pd.Series(products_day).dt.year).astype(str)
    
    output_merged_dir = _os.path.abspath(GNSSproducts_dir)
    target_path = _os.path.abspath(_os.path.join(output_merged_dir,_os.pardir,_os.pardir,'init',_os.path.basename(output_merged_dir)))
    if _os.path.exists(target_path):
        _rmtree(target_path)
        
    target_dir = target_path +'/' + year_str
    for dir in target_dir.unique(): #creating folder structure before conversion
        _os.makedirs(dir)
    
    repository = _np.ndarray((products_day.shape),object)
    h24 = _np.ndarray((products_day.shape),bool)
    makeShadow = _np.ndarray((products_day.shape),bool)
    
    tmp_merge_path = _os.path.abspath(run_dir)+ '/tmp_merge/'
    run = tmp_merge_path +_pd.Series(products_day).astype(str)
    # Need to clear run before new execution just in case
    if _os.path.exists(tmp_merge_path) : _rmtree(tmp_merge_path)
  
    repository.fill(GNSSproducts_dir)
    h24.fill(h24_bool)
    makeShadow.fill(makeShadow_bool)
    
    input_sets = _np.column_stack([products_begin,products_end,repository,target_dir,h24,makeShadow,products_day,run])

    with _Pool(processes = num_cores) as p:
        if tqdm: list(_tqdm.tqdm_notebook(p.imap(_gen_orbclk, input_sets), total=input_sets.shape[0]))
        else: p.map(_gen_orbclk, input_sets)
    _rmtree(tmp_merge_path) #cleaning


def _gen_orbclk(input_set):
    startTime = input_set[0]
    endTime = input_set[1]
    GNSSproducts = input_set[2]
    targetDir = input_set[3]
    h24 = input_set[4]
    makeShadow = input_set[5]
    products_day = input_set[6]
    run_dir = input_set[7]
    #check if target folder exists and create one if not

    if _os.path.exists(run_dir): _rmtree(run_dir) #cleaning ram if failed
    if not _os.path.exists(run_dir):
        _os.makedirs(run_dir)
    
    
    args = ['/home/bogdanm/Desktop/GipsyX_Wrapper/fetchGNSSproducts_J2000.py',
                      '-startTime',str(startTime),
                      '-endTime', str(endTime),
                      '-GNSSproducts', GNSSproducts,
                      '-targetDir', run_dir]
    args.append( '-hr24') if h24 else None
    args.append ('-makeShadowFile') if makeShadow else None


    process = _Popen(args,stdout=_PIPE)
    out, err = process.communicate()

    #rename
    files_ori = _glob.glob('{}/GNSS.*'.format(run_dir))

    try:
        files_ori_df = _pd.Series(files_ori).str.split('.',expand=True)
    except: print(str(products_day),'problem found')
        
    files_renamed = files_ori_df[0].str.slice(0,-4) + str(products_day) + '.' + files_ori_df[1]
    for i in range(files_renamed.shape[0]):
        _os.rename(files_ori[i],files_renamed[i])
    #gzip
    _Popen(['gzip *'],cwd=run_dir,shell=True).communicate()
    #move one level up
    if not _os.path.exists(targetDir):
        _os.makedirs(targetDir)
    for i in range(files_renamed.shape[0]):
        _move(src=files_renamed[i]+'.gz',dst=targetDir)
    _rmtree(run_dir)
    return out,err



# Do correction for satellite not present in the pcm files
# NOW we need to convert from CE frame to CM frame
# To do this we use orbitCmCorrection -s -i 2010-01-01.pos.gz -o 2010-01-01.cm.pos.gz
# -s is needed to remove CMC correction and convert from fixed to near-instantaneous frame (CE -> CM)
# if no -s flag is present: CM -> CE
# need to copy the init directory and to smth like init_cm and modify the pos files
# 1. copy the pos file into the RAM
# 2. modify having the output to cm_*pos.gz
# 3. copy output renaming it to the original

def ce2cm(init_ce_path,num_cores = 10,tqdm=True):
    cache='/run/user/1017/'
    cache_path = _os.path.join(cache,'ce2cm_cache')
    if not _os.path.exists(cache_path): _os.makedirs(cache_path)
    
    init_ce_path = _os.path.abspath(init_ce_path) 
    cm_dirname = _os.path.basename(init_ce_path)+'_cm'
    init_cm_path = _os.path.join(_os.path.dirname(init_ce_path),cm_dirname)
    if _os.path.exists(init_cm_path):
        print('CM folder exists. Removing.')
        _rmtree(init_cm_path)
    print('Copying {} to {}'.format(_os.path.basename(init_ce_path),cm_dirname))
    
    
#     dst = _copytree(src=init_ce_path,dst=init_cm_path)
    print('Finished copying to {}'.format(init_cm_path))
#     pos_files = _glob.glob(init_cm_path+'/*/*pos.gz')
#     print('Found {} pos files. Running'.format(len(pos_files)))
    
    #files to make symlinks
    product_files = _pd.Series(_glob.glob(init_ce_path+'/*/*.gz'))
    product_file_names_df = product_files.str.split('/',expand=True).iloc[:,-1].str.split('.',expand=True)
    symlink_files = product_files[product_file_names_df[1] != 'pos'].to_list()
    # files to copy (.pos)
    pos_files = product_files[product_file_names_df[1] == 'pos'].to_list()
    
    basedir = _os.path.abspath(_os.path.join(symlink_files[0],_os.pardir,_os.pardir,_os.pardir))
    files_symlinks = _pd.Series(symlink_files).str.split('/',expand=True).iloc[:,-3:]
    symlink_src = (basedir + '/' + files_symlinks.iloc[:,0]+'/'+files_symlinks.iloc[:,1]+'/'+files_symlinks.iloc[:,2])
    symlink_dst = (basedir + '/' + files_symlinks.iloc[:,0]+'_cm/'+files_symlinks.iloc[:,1]+'/'+files_symlinks.iloc[:,2])

    year_dirs = basedir + '/' + files_symlinks.iloc[:,0][0]+'_cm/' + files_symlinks.iloc[:,1].unique()
    for dir_path in year_dirs:
        if not _os.path.exists(dir_path): _os.makedirs(dir_path)
    print('creating symlinks for products files (except for *.pos.gz)')
    for i in range(len(symlink_src)):
        _os.symlink(src=_os.path.relpath(path=symlink_src[i],start=_os.path.dirname(symlink_dst[i])),dst=symlink_dst[i])
    
    files_pos = _pd.Series(pos_files).str.split('/',expand=True).iloc[:,-3:]
    pos_src = (basedir + '/' + files_pos.iloc[:,0]+'/'+files_pos.iloc[:,1]+'/'+files_pos.iloc[:,2])
    pos_dst = (basedir + '/' + files_pos.iloc[:,0]+'_cm/'+files_pos.iloc[:,1]+'/'+files_pos.iloc[:,2])
    cache_path_series = _np.ndarray(pos_src.shape,dtype=object)
    cache_path_series.fill(cache_path)
    pos_path_series = _pd.concat([pos_src,pos_dst,_pd.Series(cache_path_series)],axis=1).values
#     return pos_path_series
    with _Pool(processes = num_cores) as p:
        if tqdm: list(_tqdm.tqdm_notebook(p.imap(_ce2cm_single_thread, pos_path_series), total=len(pos_path_series)))
        else: p.map(_ce2cm_single_thread, pos_path_series)
    _rmtree(path=cache_path)
    

def _ce2cm_single_thread(pos_path_series):
    pos_src,pos_dst,cache_path = pos_path_series
    # fuction will rewrite the input pos file by cm corrected version
#     pos_src = _os.path.abspath(pos_src)
    
    #copy to cache. create single test folder
    _copy(src=pos_src,dst=cache_path)
    
    input_path = _os.path.join(cache_path,_os.path.basename(pos_src))

    process = _Popen(['orbitCmCorrection','-s','-i',input_path,'-o',pos_dst])
    process.wait()
    _os.remove(input_path)