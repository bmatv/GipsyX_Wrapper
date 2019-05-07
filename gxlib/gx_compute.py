import os as _os
import numpy as _np
import pandas as _pd
import tqdm as _tqdm
from subprocess import Popen as _Popen, PIPE as _PIPE
from multiprocessing import Pool as _Pool
from shutil import rmtree as _rmtree

from .gx_aux import _dump_write

def _gd2e(gd2e_set):
    
    if not _os.path.exists(gd2e_set['output']):_os.makedirs(gd2e_set['output'])
    process = _Popen([  'gd2e.py',
                        '-drEditedFile', gd2e_set['filename'],
                        '-recList', gd2e_set['station'],
                        '-runType', 'PPP',
                        '-orbClk', gd2e_set['orbClk_path'], #used to be '-GNSSproducts', gd2e_set['gnss_products_dir'],
                        '-treeSequenceDir', gd2e_set['tree_path'],
                        '-tdpInput', gd2e_set['tdp'],
                        '-staDb', gd2e_set['staDb_path']], cwd=gd2e_set['output'],stdout=_PIPE)
    # Do we really need a -gdCov option?
    out, err = process.communicate()

    solutions = _get_tdps_pn(gd2e_set['output'])
    residuals = _get_residuals(gd2e_set['output'])
    debug_tree = _get_debug_tree(gd2e_set['output'])
    runAgain = 'gd2e.py -drEditedFile {0} -recList {1} -runType PPP -orbClk {2} -treeSequenceDir {3} -tdpInput {4} -staDb {5} -gdCov'.format(
        gd2e_set['filename'],gd2e_set['station'],gd2e_set['orbClk_path'], gd2e_set['tree_path'],gd2e_set['tdp'],gd2e_set['staDb_path'])
    rtgx_log = _get_rtgx_log(gd2e_set['output'])
    rtgx_err = _get_rtgx_err(gd2e_set['output'])

    _rmtree(path=gd2e_set['output']);_os.makedirs(gd2e_set['output'])
    _dump_write(data = [solutions,residuals,debug_tree,runAgain,rtgx_log,rtgx_err,out,err],
                            filename=gd2e_set['output']+'/gipsyx_out.zstd',cname='zstd')
   
def gd2e(trees_df,stations_list,merge_tables,tmp_dir,tropNom_type,project_name,years_list,num_cores,gnss_products_dir,staDb_path,tqdm):
    '''trees_df is the output of gen_trees. merge_tables = get_merge_table'''

    gd2e_table = _np.ndarray((len(stations_list)),dtype=object)

    #loading list of analysed stations from drinfo npz file
    drinfo_file = _np.load(file=tmp_dir+'/rnx_dr/drinfo.npz')
    drinfo_stations_list = drinfo_file['stations_list']

    print('---{}---'.format(project_name))

    for i in range(len(stations_list)):
        tmp = _gen_gd2e_table_station(trees_df,drinfo_stations_list, stations_list[i], years_list, merge_tables,tmp_dir,tropNom_type,project_name,gnss_products_dir,staDb_path)

        if tmp[tmp['file_exists']==0].shape[0] ==0:
            gd2e_table[i] = None
            print('{} is already processed'.format(stations_list[i]))
        else:
            gd2e_table[i] = tmp[tmp['file_exists']==0].to_records()#converting to records in order for mp to work properly as it doesn't work with pandas Dataframe
            num_cores = num_cores if len(gd2e_table[i]) > num_cores else len(gd2e_table[i])
            print('Processing {}... | # files left: {} | Adj. # of threads: {}'.format(stations_list[i],gd2e_table[i].shape[0],num_cores))

            with _Pool(processes = num_cores) as p:
                if tqdm: list(_tqdm.tqdm_notebook(p.imap(_gd2e, gd2e_table[i]), total=gd2e_table[i].shape[0]))
                else: p.imap(_gd2e, gd2e_table[i])

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


def _gen_gd2e_table_station(trees_df,drinfo_stations_list, station, years_list, merge_tables,tmp_dir,tropNom_type,project_name,gnss_products_dir,staDb_path):
    '''Generates an np recarray that is used as sets for _gd2e
    station is the member of station_list
    gd2e(trees_df,stations_list,merge_tables,tmp_dir,tropNom_type,project_name,years_list,num_cores,gnss_products_dir,staDb_path)
    '''

    tmp = _pd.DataFrame()
                        
    station_index_in_drinfo = _np.where(drinfo_stations_list==station)[0][0]
    tmp_merge_table = merge_tables[station_index_in_drinfo]
    
    filename = _pd.Series(tmp_merge_table[:,4])#<============== Here correct for real station name i in drinfo main table
    filename[tmp_merge_table[:,0]==3] = filename[tmp_merge_table[:,0]==3].str.slice(start=None, stop=-6) + '_30h.dr.gz'
                
    tmp['filename'] = filename
    tmp['class'] = tmp_merge_table[:,0]
    tmp['year'] = _pd.Series(tmp_merge_table[:,1]).dt.year.astype(str)
    tmp['dayofyear'] = _pd.Series(tmp_merge_table[:,1]).dt.dayofyear.astype(str).str.zfill(3)
    tmp = tmp.join(other=trees_df,on='year')
    tmp['tdp'] = tmp_dir+'/tropNom/' + tmp['year'] + '/' + tmp['dayofyear'] + '/' + tropNom_type
    tmp['output'] = tmp_dir+'/gd2e/'+project_name +'/'+station+'/'+tmp['year']+ '/' + tmp['dayofyear']

    # tmp['gnss_products_dir'] = gnss_products_dir
    tmp['orbClk_path'] = gnss_products_dir + '/' + tmp['year'] + '/' + tmp['dayofyear'] + '/'
    tmp['staDb_path'] = staDb_path

    tmp['station'] = station
    
    tmp['year'] = _pd.to_numeric(tmp['year'])
    
    tmp = tmp[tmp['year'].isin(years_list)&tmp['class']!=0] #cleaning unused years (loaded from npz!!!)
    
    #Check if files exist (from what left):
    file_exists = _np.zeros(tmp.shape[0],dtype=int)
    for j in range(tmp.shape[0]):
        file_exists[j] = _os.path.isfile(tmp['output'].iloc[j]+'/gipsyx_out.zstd')
    tmp['file_exists']=file_exists
    return tmp