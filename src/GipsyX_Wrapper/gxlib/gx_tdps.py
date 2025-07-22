import glob as _glob
import os as _os
import sys as _sys
from multiprocessing import Pool as _Pool
import logging

import gcore.EarthCoordTrans as _eo
import gcore.StationDataBase as _StationDataBase
import gipsyx.tropNom as _tropNom
import numpy as _np
import pandas as _pd
import tqdm as _tqdm

from .gx_aux import _dump_read, datetime_to_j2000, drInfo_lbl, rnx_dr_lbl

PYGCOREPATH="{}/lib/python{}.{}".format(_os.environ['GCOREBUILD'], _sys.version_info[0], _sys.version_info[1])
if PYGCOREPATH not in _sys.path:
    _sys.path.insert(0,PYGCOREPATH)



def _gen_VMF1_tropNom(tropnom_param):
    '''Reads the staDb, gets list of station in the staDb, reads input arguments'''
    
    begin,end,tropNom_out,staDb,rate,VMF1_dir,stns  = tropnom_param
    
    '''begin, end, station_name, tropNom_out
    begin = tropnom begin in J2000 seconds; end = tropnom end in J2000 seconds; station name as in staDb;  '''
    if not _os.path.exists(_os.path.dirname(tropNom_out)):
        _os.makedirs(_os.path.dirname(tropNom_out))

    #begin, end, tdp_PATH
    nominals=_tropNom.nominalTrops('VMF1', modelFile=VMF1_dir)
    nominals.makeTdp(begin, end, rate, stns, tropNom_out, append=False, staDb=staDb, dry=True, wet=True)

def gen_tropnom(tmp_dir,stadb_path,rate,vmf1_dir,num_cores):
    """
    Generating tropnominal file for valid stations in staDb file.Takes number of years from dr_info.npz
    Had to create additional for loop as file no 31 gives error, no matter what year it is (tropNom read error of VMF1 file). tdp file is created for each observation file

    NOTE: have to add 18 seconds so that previous file will not be requested, similar for the last - subtract 18 seconds
    """

    logger = logging.getLogger(__name__)
    num_cores = int(num_cores)

    #Creates a staDb object
    stadb=_StationDataBase.StationDataBase(dataBase = stadb_path) #creating staDb object
    stns = stadb.getStationList() #creating array with available station names
    logger.info(len(stns),"sites found in staDb:",stns) #verbal output of stations that will be present in tropNom files
    drinfo_file: _pd.Dataframe = _dump_read(filename=f"{tmp_dir}/{rnx_dr_lbl}/{drInfo_lbl}.zstd")
    drinfo_years_list = drinfo_file.begin.dt.year.unique()
    drinfo_years_list.sort() # make sure the list is sorted so that year[0] is the edge case, same as year[-1]

    #creating folder and file structure taking into account leap year.
    #resulting paths look as follows: year/doy/30h_tropNominal.vmf1
    #data on next day needed to create current day tropnominal
    current_year = _np.datetime64("today").astype("datetime64[Y]").astype(str).astype(int)
    for year in drinfo_years_list:
        if year != current_year:
            date = _np.arange(f"{year}-01-01", f"{year + 1}-01-01", dtype="datetime64[D]").astype("datetime64[s]")
        else:
            # Handle current year with potentially incomplete VMF1 data
            current_year_vmf_ah_dir = _os.path.join(vmf1_dir, str(current_year), 'ah')
            ah_files = sorted(_glob.glob(f"{current_year_vmf_ah_dir}/*"))
            if not ah_files:
                msg = f"No VMF1 'ah' files found in {current_year_vmf_ah_dir}"
                raise FileNotFoundError(msg)
            last_ah_file = _os.path.basename(ah_files[-1])  # e.g., 'ah19315.h18.gz'
            last_day_used = int(last_ah_file[4:7]) - 1  # Subtract 1 to get 30h tropnominal range

            date = _np.datetime64(str(current_year)) + _np.arange(last_day_used).astype("timedelta64[D]")
            logger.info(f"Last VMF1 day in {current_year} is {last_ah_file[4:7]}. Generating up to {last_day_used}")
        begin = date - _np.timedelta64(3,"[h]")
        end = date + _np.timedelta64(27,"[h]")

        tropNom_out = (tmp_dir +'/tropNom/'+ str(year)+'/'+_pd.Series(date).dt.dayofyear.astype(str).str.zfill(3)+'/30h_tropNominalOut_VMF1.tdp').values

        staDb_nd    = _np.ndarray((tropNom_out.shape),dtype=object)
        rate_nd     = _np.ndarray((tropNom_out.shape),dtype=object)
        VMF1_dir_nd = _np.ndarray((tropNom_out.shape),dtype=object)
        stns_nd     = _np.ndarray((tropNom_out.shape),dtype=object)

        staDb_nd.fill(stadb); rate_nd.fill(rate); VMF1_dir_nd.fill(vmf1_dir); stns_nd.fill(stns)

        tropnom_param = _np.column_stack((datetime_to_j2000(begin),datetime_to_j2000(end),tropNom_out,staDb_nd,rate_nd,VMF1_dir_nd,stns_nd))
        num_cores = min(len(tropnom_param), num_cores)
        step_size = int(_np.ceil(len(tropnom_param) / num_cores))

        logger.info(f"{year} tropnominals generation...",end=" ")
        logger.info(f"Number of files to process: {len(tropnom_param)} | Adj. num_cores: {num_cores}")

        # tqdm implementation will produce lots of bars because of for loop pools
        for i in range(step_size):
            try:
                pool = _Pool(num_cores)
                pool.map(_gen_VMF1_tropNom, tropnom_param[_np.arange(i, len(tropnom_param), step_size)])
            finally:
                pool.close()
                pool.join()
        logger.info("| Done!")


'''
Creating tdp files with synth signal for X Y Z
penna values test. staDb NomValues | synth values | 1
outputs '_penna' files'''

def get_ref_xyz(staDb):
    '''Function reads staDb file provided and outputs datagrame with reference positions for each station that are specified in staDb file
    	Station      X               Y	             Z
    0	CAMB	4.071647e+06	-379677.1000	4.878479e+06
    1	BRAE	3.475467e+06	-206213.0000	5.326645e+06
    2	HERT	4.033461e+06	 23537.6625	    4.924318e+06
    3	LOFT	3.706041e+06	-55853.0000	    5.173496e+06
    4	WEAR	3.686877e+06	-143592.0000	5.185648e+06'''
    read = _pd.read_csv(staDb,delimiter=r'\s+',names=list(range(11)))
    positions = read[read.iloc[:,1]=='STATE']
    #refxyz = get_xyz_site(positions)
    xyz_table = positions[[0,4,5,6]]
    xyz_table.reset_index(inplace=True,drop=True)
    
    staDb_xyz = _pd.DataFrame()
    staDb_xyz['Station'] = xyz_table[0]
    staDb_xyz[['X','Y','Z']] = xyz_table[[4,5,6]].astype('float')
    return staDb_xyz

def write_tdp(output_file, tdp_concat):
    '''Function writes tdp data array to the output file with GipsyX tdp formatting'''
    def tdp_num(inp):
        return '{:>23.15e}'.format(float(inp))
    def tdp_name(inp):
        return '{0:<25}'.format(inp)
    with open(output_file, 'w') as file:
            file.write(tdp_concat.to_string(columns=['Time','NominalValue','Value','Sigma','Name'],
                      formatters={'Time': tdp_num,
                                  'NominalValue': tdp_num,
                                  'Value': tdp_num,
                                  'Sigma': tdp_num,
                                  'Name': tdp_name}, index=False, header=False) +'\n')

def get_rot(ref_xyz_df):
    '''Expects output of get_ref_xyz. Returns ndarray of rot matrices (one for each station in the input)'''
    refxyz_np = ref_xyz_df[['X','Y','Z']].values
    return _np.asarray([_eo.rotEnv2Xyz(refxyz) for refxyz in refxyz_np],dtype=object)

def _gen_penna_tdp_file(np_set):
    '''Reads tdp file generated by GipsyX from tropNom model and creates E N V signals in nominal X Y Z '''
    path2tdp_file = np_set[0]
    staDb = np_set[1]
    period = np_set[2]

    A_E = np_set[3]
    A_N = np_set[4]
    A_V = np_set[5]
    rot_ndarray = np_set[6]
    tropNom_table = _pd.read_csv(path2tdp_file,delim_whitespace=True,header=None,names=['Time','NominalValue','Value','Sigma','Name']) #reading tdp file with pandas
        
    df = _pd.DataFrame()
    df['Time'] = tropNom_table['Time'].unique()

    Fs = 1
    f = 1/(period*3600) #we need to convert hours/period to period per seconds

    df['E'] = A_E*_np.sin(2 * _np.pi * f * df['Time'] / Fs )
    df['N'] = A_N*_np.sin(2 * _np.pi * f * df['Time'] / Fs )
    df['V'] = A_V*_np.sin(2 * _np.pi * f * df['Time'] / Fs )
    '''df has Time E N V columns'''
    env = df[['E','N','V']]/1000 #converting to meters
    
    #init arrays that will collect data for all stations
    tdp_xyz = _np.ndarray((staDb.shape[0]),dtype=object)
    tdp = _pd.DataFrame(columns=['Time','NominalValue','Value','Sigma','Name'])

    for i in range(staDb.shape[0]):
        refxyz = staDb[['X','Y','Z']].iloc[i]

        tmp_xyz = _pd.DataFrame(rot_ndarray[i].dot(env.T).T, columns=['X','Y','Z'],dtype=float) + refxyz

        tmp_x = _pd.DataFrame()
        tmp_x['Time'] = df['Time']
        tmp_x['Value'] = tmp_xyz['X']
        tmp_x['Name'] = '.Station.' + staDb['Station'].iloc[i] + '.State.Pos.X'
        tmp_x['NominalValue'] = refxyz['X']

        tmp_y = _pd.DataFrame()
        tmp_y['Time'] = df['Time']
        tmp_y['Value'] = tmp_xyz['Y']
        tmp_y['Name'] = '.Station.' + staDb['Station'].iloc[i] + '.State.Pos.Y'
        tmp_y['NominalValue'] = refxyz['Y']

        tmp_z = _pd.DataFrame()
        tmp_z['Time'] = df['Time']
        tmp_z['Value'] = tmp_xyz['Z']
        tmp_z['Name'] = '.Station.' + staDb['Station'].iloc[i] + '.State.Pos.Z'
        tmp_z['NominalValue'] = refxyz['Z']

        '''tdp_xyz is a completed list ready for string conversion and output'''
        tdp_xyz[i] = _pd.concat([tmp_x,tmp_y,tmp_z])
        #tdp_xyz[i]['NominalValue'] = 0.0 #Zeroing nominals
        tdp_xyz[i]['Sigma'] = 0.0

        tdp = _pd.concat([tdp,tdp_xyz[i]],sort=False) # will sort later when all stations in place so false

    output_file = path2tdp_file + '_penna'
    tdp_concat = _pd.concat([tropNom_table,tdp]).sort_values(by=['Time','Name'])
    write_tdp(tdp_concat=tdp_concat,output_file=output_file)
    # print(output_file)

def gen_penna_tdp(tmp_path,
            staDb_path,
            tqdm,
            period=13.9585147, # Penna, N. T. et al. (2015) p.6526
            num_cores = 25,
            A_East=2, A_North=4, A_Vertical=6):
    '''
    1. Read staDb file (staDb has to have information on all the stations in the dataset)
    2. Extract stations names and positions. Create rot for each station.
    3. Glob all tdp files
    4. Loop throught tdp files list. Read each file. All years and DOYs that are present in the directory!!!
    5. For each file extract time values. Generate synth waves.
    6. Rotate for each station [in staDb?] and create tdp output lines for each station. staDb is generated on the fly from the list of stations fetched
    7. Concatanate outputs and append to input tdp file 
    '''
    files = _np.asarray(sorted(_glob.glob(tmp_path+'/tropNom/*/*/30h_tropNominalOut_VMF1.tdp')))
    num_cores = num_cores if len(files) > num_cores else len(files)
    
    ref_xyz_df = get_ref_xyz(staDb_path)
    rot = get_rot(ref_xyz_df)

    aux = _np.empty((files.shape[0],6),dtype = object) #population array [xyz_staDb_data, period, A_East, A_North, A_Vertical, rot]
    aux[:] = [ref_xyz_df,period,A_East, A_North, A_Vertical,rot]

    print('Number of files to be processed:', len(files),
          '\nAdjusted number of cores:', num_cores)
    np_set = _np.column_stack((files,aux))
    '''
    np_set[0]
    ['/mnt/Data/bogdanm/tmp_GipsyX/tropNom/2003/001/30h_tropNominalOut_VMF1.tdp',
         Station             X            Y             Z
    0    BRAE  3.475467e+06 -206213.0000  5.326645e+06
    1    LOFT  3.706041e+06  -55853.0000  5.173496e+06
    2    WEAR  3.686877e+06 -143592.0000  5.185648e+06
    3    CAMB  4.071647e+06 -379677.1000  4.878479e+06
    4    HERT  4.033461e+06   23537.6625  4.924318e+06
    5    LERW  3.183055e+06  -65838.5000  5.508326e+06
    6    NEWL  4.079954e+06 -395930.4000  4.870197e+06
    7    SHEE  3.983074e+06   51683.0000  4.964640e+06,
       13.9585147, 2, 4, 6]'''

    with _Pool(processes = num_cores) as p:
        if tqdm: list(_tqdm.tqdm(p.imap(_gen_penna_tdp_file, np_set), total=np_set.shape[0]))
        else: p.map(_gen_penna_tdp_file, np_set)

#     return np_set
