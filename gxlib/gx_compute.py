import os as _os
import numpy as _np
import pandas as _pd
import tqdm as _tqdm
from subprocess import Popen as _Popen, PIPE as _PIPE
from multiprocessing import Pool as _Pool
from shutil import rmtree as _rmtree
from .gx_aux import _dump_read,_dump_write


def _gd2e(gd2e_set):
    
    if not _os.path.exists(gd2e_set['output']):_os.makedirs(gd2e_set['output'])
    process = _Popen([  'gd2e.py',
                        '-drEditedFile', gd2e_set['filename'],
                        '-recList', gd2e_set['station_name'],
                        '-runType', 'PPP',
                        '-orbClk', gd2e_set['orbClk_path'], #used to be '-GNSSproducts', gd2e_set['gnss_products_dir'],
                        '-treeSequenceDir', gd2e_set['tree_path'],
                        '-tdpInput', gd2e_set['tdp'],
                        '-staDb', gd2e_set['staDb_path'],
                        '-selectGnss', gd2e_set['selectGnss']], cwd=gd2e_set['output'],stdout=_PIPE)
    # Do we really need a -gdCov option?
    out, err = process.communicate()

    solutions = _get_tdps_pn(gd2e_set['output'])
    residuals = _get_residuals(gd2e_set['output'])
    debug_tree = _get_debug_tree(gd2e_set['output'])
    runAgain = 'gd2e.py -drEditedFile {0} -recList {1} -runType PPP -orbClk {2} -treeSequenceDir {3} -tdpInput {4} -staDb {5} -selectGnss {6} -gdCov'.format(
        gd2e_set['filename'],gd2e_set['station_name'],gd2e_set['orbClk_path'], gd2e_set['tree_path'],gd2e_set['tdp'],gd2e_set['staDb_path'],gd2e_set['selectGnss'])
    rtgx_log = _get_rtgx_log(gd2e_set['output'])
    rtgx_err = _get_rtgx_err(gd2e_set['output'])

    _rmtree(path=gd2e_set['output']);_os.makedirs(gd2e_set['output'])
    _dump_write(data = [solutions,residuals,debug_tree,runAgain,rtgx_log,rtgx_err,out,err],
                            filename=gd2e_set['output']+'/gipsyx_out.zstd',cname='zstd')
   
def gd2e(gd2e_table,project_name,num_cores,tqdm):
    '''We should ignore stations_list as we already selected stations within merge_table'''

    if gd2e_table[gd2e_table['file_exists']==0].shape[0] ==0:
        print('{} already processed'.format(project_name))
    else:
        gd2e_table = gd2e_table[gd2e_table['file_exists']==0].to_records() #converting to records in order for mp to work properly as it doesn't work with pandas Dataframe
        num_cores = num_cores if gd2e_table.shape[0] > num_cores else gd2e_table.shape[0]
        print('Processing {} |  # files left: {} | Adj. # of threads: {}'.format(project_name,gd2e_table.shape[0],num_cores))

        with _Pool(processes = num_cores) as p:
            if tqdm: list(_tqdm.tqdm_notebook(p.imap(_gd2e, gd2e_table), total=gd2e_table.shape[0]))
            else: p.map(_gd2e, gd2e_table) #investigate why list is needed.

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


def _gen_gd2e_table(trees_df, merge_table,tmp_dir,tropNom_type,project_name,gnss_products_dir,staDb_path,years_list,mode):
    '''Generates an np recarray that is used as sets for _gd2e
    station is the member of station_list
    gd2e(trees_df,stations_list,merge_tables,tmp_dir,tropNom_type,project_name,years_list,num_cores,gnss_products_dir,staDb_path)
    '''
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
    tmp['output'] = tmp_dir+'/gd2e/'+project_name +'/'+merge_table['station_name'].astype(str)+'/'+tmp['year']+ '/' + tmp['dayofyear']

    # tmp['gnss_products_dir'] = gnss_products_dir
    tmp['orbClk_path'] = gnss_products_dir + '/' + tmp['year']+ '/' + tmp['dayofyear'] + '/'
    tmp['staDb_path'] = staDb_path
  
    tmp['year'] = _pd.to_numeric(tmp['year'])
    tmp['selectGnss'] = re_df.loc[mode]

    #cleaning unused years and class 0 as merge_table is not filtering by year to stay consistent withib merged timeframe
    tmp = tmp[ (tmp['year'].isin(years_list)) & (tmp['class']!=0)] 
    
    #Check if files exist (from what left):
    file_exists = _np.zeros(tmp.shape[0],dtype=int)
    for j in range(tmp.shape[0]):
        file_exists[j] = _os.path.isfile(tmp['output'].iloc[j]+'/gipsyx_out.zstd') #might be useful to update this name to a dynamically generated
    tmp['file_exists']=file_exists

    return tmp.sort_values(by=['station_name','year','dayofyear']).reset_index(drop=True) #resetting index just so the view won't change while debugging columns