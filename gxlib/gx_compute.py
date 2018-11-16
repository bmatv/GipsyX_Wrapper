import os as _os
import numpy as _np
import pandas as _pd
import tqdm as _tqdm
from subprocess import Popen as _Popen, PIPE as _PIPE
from multiprocessing import Pool as _Pool
from shutil import rmtree as _rmtree

def _gd2e(gd2e_set):
    
    if not _os.path.exists(gd2e_set['output']):_os.makedirs(gd2e_set['output'])
    process = _Popen([  'gd2e.py',
                        '-drEditedFile', gd2e_set['filename'],
                        '-recList', gd2e_set['station'],
                        '-runType', 'PPP',
                        '-GNSSproducts', gd2e_set['gnss_products_dir'],
                        '-treeSequenceDir', gd2e_set['tree_path'],
                        '-tdpInput', gd2e_set['tdp'],
                        '-staDb', gd2e_set['staDb_path'],
                        '-gdCov'], cwd=gd2e_set['output'],stdout=_PIPE)

    out, err = process.communicate()

    print(str(gd2e_set['year'])+'/'+gd2e_set['dayofyear'])
    #read tdp file (smooth0_0.tdp)
    tdp, tdp_header = _get_tdps_pn(gd2e_set['output'])
    #read tree file
    debug_tree_file = gd2e_set['output']+'/debug.tree'
    debug_tree = _pd.read_csv(debug_tree_file,sep='#',header=None,error_bad_lines=True).values
    
    runAgain = 'gd2e.py -drEditedFile {0} -recList {1} -runType PPP -GNSSproducts {2} -treeSequenceDir {3} -tdpInput {4} -staDb {5} -gdCov'.format(
        gd2e_set['filename'],gd2e_set['station'],gd2e_set['gnss_products_dir'], gd2e_set['tree_path'],gd2e_set['tdp'],gd2e_set['staDb_path'])
    
    rtgx_log = _pd.read_csv(gd2e_set['output']+'/rtgx_ppp_0.tree.log0_0',sep='\n',header=None).values
    rtgx_err = _pd.read_csv(gd2e_set['output']+'/rtgx_ppp_0.tree.err0_0',sep='\n',header=None).values

    finalResiduals = _read_finalResiduals(gd2e_set['output'])

    #Kill folder with all files after reading
    _rmtree(path=gd2e_set['output'])
    #create directory to store npz extracted data
    _os.makedirs(gd2e_set['output'])
    _np.savez_compressed(file=gd2e_set['output']+'/gipsyx_out',
                        tdp=tdp,
                        tdp_header=tdp_header,
                        debug_tree=debug_tree,
                        runAgain=runAgain,
                        rtgx_log=rtgx_log,
                        rtgx_err=rtgx_err,
                        out = _np.asarray(out),
                        err = _np.asarray(err),
                        finalResiduals = finalResiduals)
    
def gd2e(trees_df,stations_list,merge_tables,tmp_dir,tropNom_type,project_name,years_list,num_cores,gnss_products_dir,staDb_path):
    '''trees_df is the output of gen_trees. merge_tables = get_merge_table'''

    gd2e_table = _np.ndarray((len(stations_list)),dtype=object)

    #loading list of analysed stations from drinfo npz file
    drinfo_file = _np.load(file=tmp_dir+'/rnx_dr/drinfo.npz')
    drinfo_stations_list = drinfo_file['stations_list']
    
    for i in range(len(stations_list)):
        tmp = _gen_gd2e_table_station(trees_df,drinfo_stations_list, stations_list[i], years_list, merge_tables,tmp_dir,tropNom_type,project_name,gnss_products_dir,staDb_path)

        if tmp[tmp['file_exists']==0].shape[0] ==0:
            gd2e_table[i] = None
            print('Station', stations_list[i], 'is already processed')
        else:
            gd2e_table[i] = tmp[tmp['file_exists']==0].to_records()#converting to records in order for mp to work properly as it doesn't work with pandas Dataframe
            num_cores = num_cores if len(gd2e_table[i]) > num_cores else len(gd2e_table[i])

            print('\nStaion',stations_list[i],'processing starts...')
            print('Number of files to be processed:', len(gd2e_table[i]),
                    '\nAdjusted number of cores:', num_cores)

            with _Pool(processes = num_cores) as p:
                list(_tqdm.tqdm_notebook(p.imap(_gd2e, gd2e_table[i]), total=gd2e_table[i].shape[0]))
                print('Station',stations_list[i],'done')
    # return gd2e_table

def _get_tdps_pn(path_dir):
    '''Reads smoothFinal.tdp with pandas, pivots the data and converts to np array'''
    file = path_dir + '/smoothFinal.tdp'

    # A working prototype for fast read and extract of tdp data
    df = _pd.read_table(file, sep='\s+', header=None, usecols=[0, 1, 2, 3, 4], names=['time','nomvalue', 'value', 'sigma', 'type'])
    df = df.pivot_table(index='time', columns='type')
    
    # Create output through dictionary concat
    extracted_data = _pd.concat({
                                'sigma'  : df['sigma'].iloc[:,_np.arange(-12,-1)],
                                'nomvalue': df['nomvalue'].iloc[:,_np.arange(-12,-1)],
                                'value'   : df['value'].iloc[:,_np.arange(-12,-1)]
                                },axis=1)
    
    tdp = _np.column_stack((df.index.values,extracted_data.values))
    tdp_header = extracted_data.columns.values
    
    
    return tdp,tdp_header


def _read_finalResiduals(path_dir):
    '''Reads finalResiduals.outComplete header: ['Time','T/R Antenna No','DataType','PF Residual (m)','Elevation from receiver (deg)',\
                    ' Azimuth from receiver (deg)','Elevation from transmitter (deg)',' Azimuth from transmitter (deg)','Status']'''
    finalResiduals_path = path_dir + '/finalResiduals.out'
    header = ['Time','T/R_ant','DataType','PF_res','elev_rec','azim_rec','elev_tran',' azimu_tran','status']
    #header has to be present to extract correct number of columns as status is often None
    finalResiduals = _pd.read_table(finalResiduals_path,delim_whitespace=True,header=None,names=header)
    return finalResiduals.values


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
    tmp['gnss_products_dir'] = gnss_products_dir
    tmp['staDb_path'] = staDb_path

    tmp['station'] = station
    
    tmp['year'] = _pd.to_numeric(tmp['year'])
    
    tmp = tmp[tmp['year'].isin(years_list)&tmp['class']!=0] #cleaning unused years (loaded from npz!!!)
    
    #Check if files exist (from what left):
    file_exists = _np.zeros(tmp.shape[0],dtype=int)
    for j in range(tmp.shape[0]):
        file_exists[j] = _os.path.isfile(tmp['output'].iloc[j]+'/gipsyx_out.npz')
    tmp['file_exists']=file_exists
    return tmp