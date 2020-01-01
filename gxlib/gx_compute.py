import os as _os
import numpy as _np
import pandas as _pd
import tqdm as _tqdm
import glob as _glob
from subprocess import Popen as _Popen, PIPE as _PIPE
from multiprocessing import Pool as _Pool
from shutil import rmtree as _rmtree, copy as _copy
from .gx_aux import _dump_read,_dump_write


def _gd2e(gd2e_set):
    
    out_dir = _os.path.dirname(gd2e_set['output'])
    if not _os.path.exists(out_dir):_os.makedirs(out_dir) #creating out dir


    if not _os.path.exists(gd2e_set['cache']):_os.makedirs(gd2e_set['cache']) #creatign cache dir
    runAgain = 'gd2e.py -drEditedFile {0} -recList {1} -runType PPP -GNSSproducts {2} -treeSequenceDir {3} -tdpInput {4} -staDb {5} -selectGnss {6} -gdCov'.format(
        gd2e_set['filename'],gd2e_set['station_name'],gd2e_set['gnss_products_dir'], gd2e_set['tree_path'],gd2e_set['tdp'],gd2e_set['staDb_path'],gd2e_set['selectGnss'])
    print(runAgain)
    # try:
    process = _Popen([  'gd2e.py',
                        '-drEditedFile', gd2e_set['filename'],
                        '-recList', gd2e_set['station_name'],
                        '-runType', 'PPP',
                        '-GNSSproducts', gd2e_set['gnss_products_dir'], #used to be '-GNSSproducts', gd2e_set['gnss_products_dir'],
                        '-treeSequenceDir', gd2e_set['tree_path'],
                        '-tdpInput', gd2e_set['tdp'],
                        '-staDb', gd2e_set['staDb_path'],
                        '-selectGnss', gd2e_set['selectGnss']], cwd=gd2e_set['cache'],stdout=_PIPE)
    # Do we really need a -gdCov option?
    out, err = process.communicate()
    
    solutions = _get_tdps_pn(gd2e_set['cache'])
    residuals = _get_residuals(gd2e_set['cache'])
    debug_tree = _get_debug_tree(gd2e_set['cache'])
    
    rtgx_log = _get_rtgx_log(gd2e_set['cache'])
    rtgx_err = _get_rtgx_err(gd2e_set['cache'])
    _rmtree(path=gd2e_set['cache']) #clearing cache after run

    _dump_write(data = [solutions,residuals,debug_tree,runAgain,rtgx_log,rtgx_err,out,err],
                            filename=gd2e_set['output'],cname='zstd')
    # except:
    #     print('Problem found:',runAgain)
    # return out, err

def gd2e(gd2e_table,project_name,num_cores,tqdm,cache_path):
    '''We should ignore stations_list as we already selected stations within merge_table'''
    # try:
    if gd2e_table[gd2e_table['file_exists']==0].shape[0] ==0:
        print('{} already processed'.format(project_name))
    else:
        gd2e_table = gd2e_table[gd2e_table['file_exists']==0].to_records() #converting to records in order for mp to work properly as it doesn't work with pandas Dataframe
        num_cores = num_cores if gd2e_table.shape[0] > num_cores else gd2e_table.shape[0]
        print('Processing {} |  # files left: {} | Adj. # of threads: {}'.format(project_name,gd2e_table.shape[0],num_cores))

        with _Pool(processes = num_cores) as p:
            if tqdm: list(_tqdm.tqdm_notebook(p.imap(_gd2e, gd2e_table), total=gd2e_table.shape[0]))
            else: p.map(_gd2e, gd2e_table) #investigate why list is needed.
    
    # except:
    print('cleaning IONEX from RAM as exiting')
    #cleaning after execution            
    IONEX_cached_path = _os.path.join(cache_path,'IONEX_merged')
    _rmtree(IONEX_cached_path)

def _get_tdps_pn(path_dir):
    '''A completely new version. Faster selection of data types needed. Pivot is done on filtered selection.
    Header can be changed with [columns.levels[0].to_numpy(), columns.levels[1].to_numpy()] but no major effect expected'''
    file = path_dir + '/smoothFinal.tdp'
    # A working prototype for fast read and extract of tdp data
    tmp = _pd.read_csv(file, delim_whitespace=True, header=None, names=['time','nomvalue', 'value', 'sigma', 'type'])
    
    station_types = tmp['type'].str.contains(pat = 'Station',regex =False)
    df = tmp[station_types]
    df = df.pivot(index='time',columns='type')
    return df

def _get_debug_tree(path_dir):
    file = path_dir + '/debug.tree'
    debug_tree = _pd.read_csv(file,sep='#',header=None,error_bad_lines=True)[0]
    return debug_tree

    
def _get_residuals(path_dir):
    '''Reads finalResiduals.outComplete header: ['Time','T/R Antenna No','DataType','PF Residual (m)','Elevation from receiver (deg)',\
                    ' Azimuth from receiver (deg)','Elevation from transmitter (deg)',' Azimuth from transmitter (deg)','Status']'''
    finalResiduals_path = path_dir + '/finalResiduals.out'
    header = ['time','t_r_ant','datatype','pf_res','elev_rec','azim_rec','elev_tran','azimu_tran','status']
    #header has to be present to extract correct number of columns as status is often None
    
    dtypes = {'time':int,
          't_r_ant':object,
          'datatype':'category',
          'pf_res':'float64',
          'elev_rec':'float32',
          'azim_rec':'float32',
          'elev_tran':'float32',
          'azimu_tran':'float32',
          'status':'category'}
    
    finalResiduals = _pd.read_csv(finalResiduals_path,delim_whitespace=True,header=None,names=header,dtype=dtypes,na_filter=True)
    finalResiduals['rec'] = (finalResiduals['t_r_ant'].str.slice(1,5)).astype('category')
    finalResiduals['trans'] = (finalResiduals['t_r_ant'].str.slice(9,-4)).astype('category')
    finalResiduals['gnss'] = (finalResiduals['t_r_ant'].str.slice(9,10)).astype('category')
    finalResiduals.drop('t_r_ant',axis=1,inplace=True)
    return finalResiduals.set_index(['datatype','time'])

def _get_rtgx_log(path_dir):
    rtgx_log = _pd.read_csv(path_dir+'/rtgx_ppp_0.tree.log0_0',sep='\n',header=None,index_col=None).squeeze()
    return rtgx_log
def _get_rtgx_err(path_dir):
    rtgx_err = _pd.read_csv(path_dir+'/rtgx_ppp_0.tree.err0_0',sep='\n',header=None,index_col=None).squeeze()
    return rtgx_err

def cache_ionex_files(cache_path,IONEX_products_dir,ionex_type,years_list):
    #Copying IONEX maps to cache before execution-------------------------------------------------------------------------------------
    products_dir = _os.path.join(IONEX_products_dir,_os.pardir)
    ionex_files = _pd.Series(sorted(_glob.glob(products_dir+'/IONEX_merged/' + ionex_type + '*')))
    ionex_basenames = ionex_files.str.split('/', expand=True).iloc[:, -1]
    ionex_years = ionex_basenames.str.slice(-4).astype(int)
    ionex_files = ionex_files[ionex_years.isin(years_list)] #selecting only those ionex files that are needed according to years list

    IONEX_cached_path = _os.path.join(cache_path,'IONEX_merged') #need to remove when start
    if _os.path.exists(IONEX_cached_path): _rmtree(IONEX_cached_path)
    _os.makedirs(IONEX_cached_path)
    for ionex_file in ionex_files:
        _copy(src = ionex_file, dst = IONEX_cached_path)

def _gen_gd2e_table(trees_df, merge_table,tmp_dir,tropNom_type,project_name,gnss_products_dir,staDb_path,years_list,mode,cache_path,IONEX_products_dir,ionex_type): 
    '''Generates an np recarray that is used as sets for _gd2e
    station is the member of station_list
    gd2e(trees_df,stations_list,merge_tables,tmp_dir,tropNom_type,project_name,years_list,num_cores,gnss_products_dir,staDb_path)
    '''
    #IF current year -> get last day of products and filter files to process based on this day.
    # if last day != number of days => write a message and filter files
    current_year = _pd.Timestamp('today').year
    current_year = 2019 # temporary hack for several weeks
    if _np.max(years_list) == current_year: #if no current year present in the input year list -> do nothing (no products check needed)
        current_year_files_count = (merge_table['begin'].dt.year == current_year).sum()
        if  current_year_files_count > 0: #sum of True > 0 means cur year is present
            #check present files
            print('Found current year ({}) files ({})  present in drInfo. Checking last day of products present'.format(current_year,current_year_files_count))
            current_year_last_product = sorted(_glob.glob(_os.path.join(gnss_products_dir,str(current_year),'*')))[-1]
            last_products_date = _pd.Timestamp(_os.path.basename(current_year_last_product)[:10]) #we suppose that products are 30h always
            merge_table = merge_table[merge_table['begin'].dt.date<=last_products_date.date()].copy()
            print('Last products date is {}. Overriding list of files processed'.format(last_products_date))

    cache_ionex_files(cache_path,IONEX_products_dir,ionex_type,years_list)
    re_df = _pd.Series(index = ['GPS','GLONASS','GPS+GLONASS'],data=['^GPS\d{2}$','^R\d{3}$','^(GPS\d{2})|(R\d{3})$'])

    tmp = _pd.DataFrame()
                                          
    tmp['filename'] = merge_table['path']
    tmp['class'] =  merge_table['completeness']
    tmp['station_name'] = merge_table['station_name']
    tmp.loc[tmp['class'] == 3, 'filename'] += '.30h' # Using .loc[row_indexer,col_indexer] = value instead


    tmp['year'] = merge_table['begin'].dt.year.astype(str)
    tmp['dayofyear'] = merge_table['begin'].dt.dayofyear.astype(str).str.zfill(3)
    tmp = tmp.join(other=trees_df,on='year') #adds tree paths
    tmp['tdp'] = tmp_dir+'/tropNom/' + tmp['year'] + '/' + tmp['dayofyear'] + '/' + tropNom_type

    #real path to the output file. Advanced naming implemented to eiminate folder creation which is really slow to remove on HPC
    output_dirs = tmp_dir+'/gd2e/'+project_name +'/'+merge_table['station_name'].astype(str)+'/'+tmp['year'] #to calcel race condition with folder creation I need to create all first
    dir_structure =  output_dirs.unique()
    for dir in dir_structure:
        if not _os.path.isdir(dir): _os.makedirs(dir)

    tmp['output'] = output_dirs + '/'+tmp['station_name'].str.lower()+tmp['dayofyear']+'.'+tmp['year'].str.slice(-2)+'.zstd'

    if _os.path.exists(cache_path + '/tmp/'): _rmtree(cache_path + '/tmp/')
    tmp['cache'] = cache_path + '/tmp/'+merge_table['station_name'].astype(str)+tmp['year']+tmp['dayofyear'] #creating a cache path for executable directory
    tmp['gnss_products_dir'] = gnss_products_dir
    # tmp['orbClk_path'] = gnss_products_dir + '/' + tmp['year']+ '/' + tmp['dayofyear'] + '/'
    tmp['staDb_path'] = staDb_path
  
    tmp['year'] = _pd.to_numeric(tmp['year'])
    tmp['selectGnss'] = re_df.loc[mode]

    #cleaning unused years and class 0 as merge_table is not filtering by year to stay consistent withib merged timeframe
    tmp = tmp[ (tmp['year'].isin(years_list)) & (tmp['class']!=0)] 
    
    #Check if files exist (from what left):
    file_exists = _np.zeros(tmp.shape[0],dtype=int)
    for j in range(tmp.shape[0]):
        file_exists[j] = _os.path.isfile(tmp['output'].iloc[j]) #might be useful to update this name to a dynamically generated
    tmp['file_exists']=file_exists

    return tmp.sort_values(by=['station_name','year','dayofyear']).reset_index(drop=True) #resetting index just so the view won't change while debugging columns