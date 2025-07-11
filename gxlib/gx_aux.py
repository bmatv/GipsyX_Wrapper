import binascii as _binascii
import glob as _glob
import os as _os
import re as _re
import sys as _sys
from multiprocessing import Pool as _Pool
from subprocess import PIPE as _PIPE
from subprocess import STDOUT as _STDOUT
from subprocess import Popen as _Popen

import blosc as _blosc
import numpy as _np
import pandas as _pd
import pyarrow as _pa
import tqdm as _tqdm
from shutil import move as _move

PYGCOREPATH = "{}/lib/python{}.{}".format(_os.environ['GCOREBUILD'],\
              _sys.version_info[0], _sys.version_info[1])
if PYGCOREPATH not in _sys.path:
    _sys.path.insert(0, PYGCOREPATH)
import gcore.EarthCoordTrans as _eo
import gcore.StationDataBase as StationDataBase

from .gx_const import J2000origin
from .gx_hardisp import blq2hardisp as _blq2hardisp

import GipsyX_Wrapper.trees_options as trees_options

_regex_ID = _re.compile(r"1\.\W+S.+\W+Site Name\s+\:\s(.+|)\W+Four Character ID\s+\:\s(.+|)\W+Monument Inscription\s+\:\s(.+|)\W+IERS DOMES Number\s+\:\s(.+|)\W+CDP Number\s+\:\s(.+|)", _re.MULTILINE)
_regex_loc = _re.compile(r"2\.\W+S.+\W+City or Town\W+\:\s(.+|)\W+State or Province\W+\:\s(.+|)\W+Country\W+\:\s(.+|)\W+Tectonic Plate\W+\:\s(.+|)\W+.+\W+X.+\:\s(.+|)\W+Y..+\:\s(.+|)\W+Z.+\:\s(.+|)\W*Latitude.+\:\s(.+|)\W*Longitude.+\:\s(.+|)\W*Elevation.+\:\s(.+|)", _re.MULTILINE)
_regex_rec = _re.compile(r"3\.\d+\s+R.+\W+\:\s(.+|)\W+Satellite System\W+\:\s\(?(?:\(\w*\/\w*\/|)([a-zA-Z+]+)\W+Serial Number\W+\:\s(.+|)\W+Firmware Version\W+\:\s(.+|)\W+Elevation Cutoff Setting\W+\:\s(.+|)\W+Date Installed\W+\:\s(\d{4}.{1}\d{2}.{1}\d{2}|)(?:.{1}|)(\d{2}.{1}\d{2}|)Z?\W+Date Removed\W+\:\s(\d{4}.{1}\d{2}.{1}\d{2}|)(?:.{1}|)(\d{2}.{1}\d{2}|)", _re.MULTILINE)
_regex_ant = _re.compile(r"4\.\d\s+Antenna Type.+\W+:\s(\w+\S?\w+?|)\s+(\w+|)\W+Serial Number\W+:\s(\w+\s?\W?\w+?|)\W+Antenna.+:\s(.+|)\W+Marker->ARP Up.+:\s(.+|)\W+Marker->ARP North.+:\s(.+|)\W+Marker->ARP East.+:\s(.+|)\W+Alignment from True N\W+:\s(.+|)\W+Antenna Radome Type\W+:\s(.+|)\W+Radome Serial Number\W+:\s(.+|)\W+Antenna Cable Type\W+:\s(.+|)\W+Antenna Cable Length\W+:\s(.+|)\W+Date Installed\W+:\s(.{10})T?(.{5}|)Z?\W+Date Removed\W+\:(?:\s\(?(.{10})T(.{5}|)Z?|)\W+Additional Information\W+:\s(.+|)\W+", _re.MULTILINE)

drInfo_lbl = 'drInfo'
rnx_dr_lbl = 'rnx_dr'

def prepare_dir_struct_dr(begin_year, end_year,tmp_dir):
    timeline = _pd.Series(_np.arange(_np.datetime64(str(begin_year)),_np.datetime64(str(end_year+1)),_np.timedelta64(1,'D')))
    dayofyear = timeline.dt.dayofyear.astype(str).str.zfill(3)
    year = timeline.dt.year.astype(str)
    dirs = tmp_dir + '/{}/'.format(rnx_dr_lbl) + year +'/'+ dayofyear
    for path in dirs:
        if not _os.path.exists(path):
            _os.makedirs(path)

    drinfo_dirs = tmp_dir +'/{}/{}/'.format(rnx_dr_lbl,drInfo_lbl) + year
    for drinfo_path in drinfo_dirs:
        if not _os.path.exists(drinfo_path):
            _os.makedirs(drinfo_path)

def prepare_dir_struct_gathers(tmp_dir,project_name):
    env_gathers_dir = _os.path.join(tmp_dir,'gd2e/env_gathers',project_name)
    # solutions_dir = _os.path.join(tmp_dir,'gd2e/solutions',project_name)
    # residuals_dir = _os.path.join(tmp_dir,'gd2e/residuals',project_name)
    # for path in [env_gathers_dir,solutions_dir,residuals_dir]:
    if not _os.path.exists(env_gathers_dir):
        _os.makedirs(env_gathers_dir)

# service functions for uncompressing
def uncompress(file_path):
    process = _Popen(['uncompress',file_path])
    process.wait()

def uncompress_mp(filelist,num_cores=10):
    with _Pool(processes=num_cores) as p:
        p.map(uncompress,filelist)

def _update_mindex(dataframe, lvl_name,loc=0,axis=1):
    '''Inserts a level named as lvl_name into dataframe_in in loc position.
    Level can be inserted either in columns (default axis=1) or index (axis=0)'''

    mindex_df = dataframe.columns if axis == 1 else dataframe.index
    mindex_df =  mindex_df.to_frame(index=False)

    if loc == -1: loc = mindex_df.shape[1] #can insert below levels
    mindex_df.insert(loc = loc,column = 'add',value = lvl_name)

    mindex_df_updated = _pd.MultiIndex.from_arrays(mindex_df.values.T)
    if axis == 1: dataframe.columns = mindex_df_updated
    else: dataframe.index = mindex_df_updated
    return dataframe

def split10(array,split_arrays_size = 10):
    '''takes list or ndarray and splits it into chunks with size of 10.'''
    array = _np.asarray(array)
    nchunks = int(array.shape[0]/split_arrays_size)
    nchunks+=1*(nchunks == 0) #for the case of less than 10 sites in array - leave in a single array
    return _np.array_split(array,nchunks)

def _check_stations(stations_list,tmp_dir,project_name):
    '''Check presence of stations in the project and outputs corrected station list'''
    stations_list = _np.core.defchararray.upper(stations_list)
    #check if station from input is in the folder
    gd2e_stations_list = _os.listdir(tmp_dir + '/gd2e/'+project_name)
    station_exists = _np.isin(stations_list,gd2e_stations_list)

    checked_stations = stations_list[station_exists==True]
    return checked_stations

def _dump_write(filename,data,num_cores=24,cname='zstd'):
    '''Serializes the input (may be a list of dataframes or else) and uses blosc to compress it and write to a file specified'''
    _blosc.set_nthreads(num_cores) #using 24 threads for efficient compression of extracted data
    context = _pa.default_serialization_context()
    serialized_data = context.serialize(data).to_buffer()
    compressed = _blosc.compress(serialized_data, typesize=8,clevel=9,cname=cname)
    with open(filename,'wb') as f: f.write(compressed)

def _dump_read(filename):
    '''Serializes the input (may be a list of dataframes or else) and uses blosc to compress it and write to a file specified'''
    with open(filename,'rb') as f:
        decompressed = _blosc.decompress(f.read())
    deserialized = _pa.deserialize(decompressed)
    return deserialized

def _project_name_construct(project_name,PPPtype,pos_s,wetz_s,tropNom_input,ElMin,ambres,tree_options=trees_options.rw_otl):
    '''pos_s and wetz_s are im mm/sqrt(s)'''
    if PPPtype=='kinematic':
        project_name = '{}_{}_{}'.format(str(project_name),str(pos_s),str(wetz_s))
    if PPPtype=='static':
        project_name = '{}_static'.format(str(project_name))
    #adding _synth if tropNom type == trop+penna
    if tropNom_input == 'trop+penna':
        project_name += '_synth'
    if ambres:
        project_name += '_ar'
    # the last component in proj_name will be ElMin if it is not default 7 degrees
    if ElMin!=7:
        project_name += '_El{}'.format(ElMin)
    if tree_options == trees_options.rw_no_otl:
        project_name += '_nootl'
    return project_name

def gen_staDb(tmp_dir,project_name,stations_list,IGS_logs_dir):
    '''Creates a staDb file from IGS logs'''
    #Making staDb directory in tmp folder
    staDb_dir = tmp_dir + '/staDb/' + project_name + '/'
    staDb_path = staDb_dir + project_name + '.staDb'

    #if staDb_path was already generated, just return staDb_path path
    # if not _os.path.exists(staDb_path): #The staDb should be overwritten every time.

    if not _os.path.exists(staDb_dir):
        _os.makedirs(staDb_dir)
    #getting paths to all log files needed
    logs = _np.ndarray((len(stations_list)),dtype=object)

    for i in range(len(stations_list)):
        logs[i] = sorted(_glob.glob(IGS_logs_dir + '/*/' + stations_list[i].lower() +'*'+'.log'))[-1] #should be the last log created in case multiple exist


    buf = ("KEYWORDS: ID STATE ANT RX\n")  # POSTSEISMIC, LINK, END
    for file in logs:
        with open(file, 'r') as f:
            data = f.read()
    # Site ID
        matches_ID = _re.findall(_regex_ID, data)
    # Site Location, only one location line per BIGF log
        matches_loc = _re.findall(_regex_loc, data)
        buf += ("{ID}  ID  {IERS} {loc_2} {loc_1}\n".format(ID=matches_ID[0][1], IERS=matches_ID[0][3] if matches_ID[0][3] != '' else 'UNKNOWN',
                                                        loc_2=matches_loc[0][1], loc_1=matches_loc[0][2]))

        buf += ("{ID}  STATE 1-01-01 00:00:00 {X:.15e}  {Y:.15e} {Z:.15e} {X_v:.15e}  {Y_v:.15e} {Z_v:.15e}\n".format(ID=matches_ID[0][1],
                                                                                                                X=float(matches_loc[0][4]) if matches_loc[0][4] != '' else 0,
                                                                                                                Y=float(matches_loc[0][5]) if matches_loc[0][5] != '' else 0,
                                                                                                                Z=float(matches_loc[0][6]) if matches_loc[0][6] != '' else 0,
                                                                                                                X_v=0, Y_v=0, Z_v=0))
    # Receiver Information
        rec = []
        matches_rec = _re.finditer(_regex_rec, data)
        for matchNum, match in enumerate(matches_rec):
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
            rec.append(match.groups())
            buf += ("{ID}  RX {d_inst} {t_inst}:00 {rec_type} # {rec_num} {rec_fw_v}\n".format(ID=matches_ID[0][1], d_inst=rec[matchNum][5], t_inst=rec[
                matchNum][6] if rec[matchNum][6] != '' else '00:00', rec_type=rec[matchNum][0], rec_num=rec[matchNum][2], rec_fw_v=rec[matchNum][3]))
    # Antenna Information
        ant = []
        matches_ant = _re.finditer(_regex_ant, data)
        for matchNum, match in enumerate(matches_ant):
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
            ant.append(match.groups())

            # Each field is whitespace delimited:
            # Field 0:         Station identifier (arbitrary string length)
            # Field 1:         Record key, must be 'ANT'
            # Field 2:         Date of epoch in calendar format YYYY-MM-DD (year, month, day as integers)
            # Field 3:         Time of epoch in HH:MM:SS format (hours, minutes, seconds as integers)
            # Field 4:         Antenna type
            # Field 5:         Radome type
            # Field 6,7,8:     Site vector in meters (east, north, vertical)
            # Field 9:         Comments starting with '#'

            buf += ("{ID}  ANT {d_inst} {t_inst}:00 {ant_type} {radome_type} {east} {north} {vertical} # {ant_num}\n".
                format(ID=matches_ID[0][1], d_inst=ant[matchNum][12], t_inst=ant[matchNum][13] if ant[matchNum][13]!= '' else '00:00', ant_type=ant[matchNum][0],
                        radome_type=ant[matchNum][8] if ant[matchNum][8]!= '' else 'NONE', vertical=ant[matchNum][4], north=ant[matchNum][5], east=ant[matchNum][6], ant_num=ant[matchNum][2]))

    #we read the existing staDb, do the crc, compare, overwrite if different
    if _os.path.exists(staDb_path):
        with open(staDb_path,'rb') as ex_staDb:
            crc_ex = _binascii.crc32(ex_staDb.read())& 0xffffffff
        crc = _binascii.crc32(buf.encode('ascii'))& 0xffffffff
        if crc_ex!=crc:
            print('Overwriting existing staDb file')
            with open(staDb_path,'w') as output: output.write(buf)
    else:
        print('Writing new staDb file')
        with open(staDb_path,'w') as output: output.write(buf)

    #     return staDb_path,crc_ex, crc
    return staDb_path

def get_chalmers(staDb_path,as_df=False):
    '''Converts staDb to input for http://holt.oso.chalmers.se/loading/
    Name of station_________|	|Longitude (deg)	| Latitude (deg)	| Height (m)
    //sala                        11.9264         57.3958         0.0000
    //ruler.................b................<...............<...............
    // Records starting with // are treated as comments

    OR returns a dataframe if as_df (needed for plotting)'''
    staDb = StationDataBase.StationDataBase(dataBase=staDb_path)  # creating staDb object + read as after GipsyX 1.3


    max_t = 3.0e8  # maximum time value for the dataset on which available sites will be added to OTL computation with SPOTL
    names_stdb = _np.asarray(staDb.getStationList(), dtype=object)
    llh_stdb = _np.asarray(staDb.dumpLatLonHeights(epoch=max_t,
                                                    stationList=staDb.getStationList()))
    nllh = _np.column_stack((names_stdb, llh_stdb.T))
    nllh =  nllh[nllh[:,0].argsort()]
    if as_df:
        return _pd.DataFrame(nllh,columns=['SITE','LAT','LON','HEIGHT'])
    else:
        for station in nllh:
            print('%-19.4s %15.4f %15.4f %15.4f'%(station[0],station[2],station[1],station[3]))
# def get_atm1(staDb_path):
#     '''https://geophy.uni.lu/atmosphere/tide-loading-calculator/ATM1OnlineCalculator/'''
#         staDb = StationDataBase.StationDataBase(dataBase=staDb_path)  # creating staDb object + read as after GipsyX 1.3


#     max_t = 3.0e8  # maximum time value for the dataset on which available sites will be added to OTL computation with SPOTL
#     names_stdb = _np.asarray(staDb.getStationList(), dtype=object)
#     llh_stdb = _np.asarray(staDb.dumpLatLonHeights(epoch=max_t,
#                                                     stationList=staDb.getStationList()))
#     nllh = _np.column_stack((names_stdb, llh_stdb.T))
#     for station in nllh:
#         print('%-19.4s %15.4f %15.4f'%(station[0],station[2],station[1]))

def _dr_size(dr_files):
    '''Returns ndarray with sizes of converted dr files. Based on this, selects bad and good files (bad files have size less than 20, technically empty).
    Bad file can be created by GipsyX in case input RNX file doesn't have enough data for conversion. Bad files should be filtered out of processing.
    The script can be converted to multiprocessing'''

    size_array= _np.ndarray((dr_files.shape[0]))

    for i in range(dr_files.shape[0]):
        size_array[i] = _os.path.getsize(dr_files[i]) #index of 1 means dr file path
    return size_array


def _drInfo2df(dr_file):
    '''Calls a dataRecordInfo script on already converted to dr format RNX file with rnxEditGde.py.
    dr_file is an absolute path but if switching machines/dr_location we need to rerun'''
    drInfo_process = _Popen(args=['dataRecordInfo', '-file', _os.path.basename(dr_file)],
                                        stdout=_PIPE, stderr=_STDOUT, cwd=_os.path.dirname(dr_file))
    out = drInfo_process.communicate()[0]
    dr_Info_raw = _pd.Series(out.decode('ascii').splitlines()).str.split(pat=r':\s', expand=True)

    df = _pd.DataFrame(index=[0])
    df['n_records'] = int(dr_Info_raw.iloc[0, 1])
    time_vals = _pd.to_datetime(dr_Info_raw.iloc[1:3, 1]).values
    df['begin'] = time_vals[0]
    df['end'] = time_vals[1]
    df['n_receivers'] = _pd.to_numeric(dr_Info_raw.iloc[3, 1])
    df['n_transmitters'] = _pd.to_numeric(dr_Info_raw.iloc[5, 1])
    df['station_name'] = dr_Info_raw.iloc[4, 0].strip()

    transmitters = dr_Info_raw.iloc[6:, 0]
    df['GPS'] = transmitters.str.contains(pat=r'GPS\d{2}').sum() #number of GPS satellites present in the dr file
    df['GLONASS'] = transmitters.str.contains(pat=r'R\d{3}').sum() #number of GLONASS satellites present in the dr file
    df['path'] = _pd.Series(dr_file).str.extract(r'(\/rnx_dr.+)')

    return df

def get_drInfo(tmp_dir,num_cores,tqdm,selected_rnx):
    '''Analysis is done over all stations in the projects tmp_dir. The problem to run analysis on all converted fies is 30 hour files
    Naming convention for 30h files was changed
    that are present in the directory so original files are difficult to extract. Need to change merging naming'''
    tmp_dir = _os.path.abspath(tmp_dir); num_cores = int(num_cores) #safety precaution if str value is specified
    rnx_dir = _os.path.join(tmp_dir,rnx_dr_lbl)
    drinfo_dir = _os.path.join(rnx_dir,drInfo_lbl)
    if not _os.path.exists(drinfo_dir): _os.makedirs(drinfo_dir)

    selected_rnx['good'] = _dr_size(selected_rnx['dr_path'])>20
    #New approach to file saving is to save SSSSYYYY.zstd files for each year in each station. More modular approach.
    stations = selected_rnx[selected_rnx['good']]['station_name'].unique().sort_values()
    print('stations selected: {}'.format(stations.to_numpy()))

    years = selected_rnx[selected_rnx['good']]['year'].unique()
    years.sort()
    print('years selected   : {}'.format(years))
    
    for station in stations:
        for year in years:
            filename = '{drinfo_dir}/{yyyy}/{station}{yy}.zstd'.format(drinfo_dir=drinfo_dir,yyyy=year.astype(str),station=station.lower(),yy=year.astype(str)[2:])
            if not _os.path.exists(filename):
                dr_station_year = selected_rnx[(selected_rnx['station_name'] == station) & (selected_rnx['year'] == year)]
                dr_good_station_year = dr_station_year['dr_path'][dr_station_year['good']]
                if dr_good_station_year.shape[0]>0:
                    print('{} good files found for {}{} out of {}. Running get_drInfo...'.format(dr_good_station_year.shape[0],station,year,dr_station_year.shape[0]))
                    num_cores = num_cores if dr_good_station_year.shape[0] > num_cores else dr_good_station_year.shape[0]
                    with _Pool(processes = num_cores) as p:
                        if tqdm: drinfo_df = _pd.concat(list(_tqdm.tqdm_notebook(p.imap(_drInfo2df, dr_good_station_year),
                                                                                total=dr_good_station_year.shape[0],
                                                                                desc='{}{}'.format(station.lower(),year.astype(str)[2:]))),axis=0,ignore_index=True)
                        else:
                            print('Running get_drInfo for {station}{yy}.zstd'.format(station=station.lower(),yy=year.astype(str)[2:]))
                            drinfo_df = _pd.concat(p.map(_drInfo2df, dr_good_station_year),axis=0,ignore_index=True)
                    drinfo_df['station_name'] = drinfo_df['station_name'].astype('category')
                    drinfo_df['length'] = (drinfo_df['end'] - drinfo_df['begin']).astype('timedelta64[h]').astype(int)
                    #Saving extracted data for furthe processing
                    _dump_write(data = drinfo_df,filename=filename,cname='zstd',num_cores=num_cores)
                #gather should be separate, otherwise conflict and corrupted files
                else:
                    print('{} good files found for {}{} out of {}. Skipping.'.format(dr_good_station_year.shape[0],station,year,dr_station_year.shape[0]))
            else: print('{} exists'.format(filename))

def gather_drInfo(tmp_dir,num_cores,tqdm):
    #After all stationyear files were generated => gather them to single dr_info file. Will be rewritten on every call (dr_info unique files will get updated if new files were added)
    #should be run only once with single core
    tmp_dir = _os.path.abspath(tmp_dir); num_cores = int(num_cores) #safety precaution if str value is specified
    rnx_dir = _os.path.join(tmp_dir,rnx_dr_lbl)
    drinfo_dir = _os.path.join(rnx_dir,drInfo_lbl)
    tmp = []
    drInfo_files = sorted(_glob.glob('{}/*/*.zstd'.format(drinfo_dir)))
    for drInfo_file in drInfo_files:
        tmp.append(_dump_read(drInfo_file))
    print('gather_drInfo: Concatenating partial drinfo files to proj_tmp/rnx_dr/drInfo.zstd')
    _dump_write(data = _pd.concat(tmp,axis=0),filename='{}/{}.zstd'.format(rnx_dir,drInfo_lbl),cname='zstd',num_cores=num_cores)
    print('gather_drInfo: Done')
    print('Now run gen_tropNom() to update the tropnominals. Sites will be taken from recently generated staDb so be careful (need to change it to drInfo sites')

def mode2label(mode):
    mode_table = _pd.DataFrame(data = [['GPS','_g'],['GLONASS','_r'],['GPS+GLONASS','_gr']],columns = ['mode','label'])
    '''expects one of the modes (GPS, GLONASS or GPS+GLONASS and returs g,r or gr respectively for naming conventions)'''
    return mode_table[mode_table['mode']==mode]['label'].values[0]

def names2labels(constituents):
    constituents_labels = _pd.Series(constituents).str.slice(0,1)+'$_'+_pd.Series(constituents).str.slice(1,2)+'$'
    return constituents_labels

'''section of solution to ENV conversion'''
def _xyz2env(dataset,reference_df,mode,dump=None):
    '''Correct way of processing smooth0_0.tdp file. Same as tdp2EnvDiff.py
    tdp2EnvDiff outputs in cm. We need in mm.
    Outputs a MultiIndex DataFrame with value and nomvalue subsections to control tdp_in procedure
    mode is used bu mGNSS_class to process synchronized series with multiple constellations. Prevents collecting envs
    In case encounters dump option -> dumps each gather as a {station}_{mode}.zstd
    '''
        #     if dump: gx_aux._dump_write(filename, data, num_cores=24, cname='zstd')
    envs = _np.ndarray((len(dataset)),dtype=object)

    for i in range(len(dataset)):
        # Creating MultiIndex:
        station_name = dataset[i].columns.levels[1].str.split('.',expand=True).levels[2][0].upper() #get station name from .Station.XXXX.blabla
        env_path = _os.path.join(dump,'{}{}.zstd'.format(station_name.lower(),mode2label(mode))) if dump is not None else None

        if dump is not None and _os.path.exists(env_path):
            envs[i] = _dump_read(env_path)
        else:
            m_index= _pd.MultiIndex.from_product([[station_name],['value','nomvalue','sigma'],['east','north','up']])
            frame = _pd.DataFrame(columns = m_index)

            XYZ_columns = '.Station.{}.State.Pos.'.format(station_name)+ _pd.Series(['X','Y','Z'])
            xyz_value = dataset[i]['value'][XYZ_columns]
            xyz_nomvalue = dataset[i]['nomvalue'][XYZ_columns]
            xyz_sigma = dataset[i]['sigma'][XYZ_columns]

            refxyz = get_xyz_site(reference_df,station_name) #stadb values. Median also possible. Another option is first 10-30% of data
            # refxyz = xyz.median() #ordinary median as reference. Good for data with no trend. Just straight line.
            # refxyz = xyz.iloc[:int(len(xyz)*0.5)].median() #normalizing on first 10% of data so the trends should be visualized perfectly.
            rot = _eo.rotEnv2Xyz(refxyz).T #XYZ

            diff_value = xyz_value - refxyz #XYZ
            diff_nomvalue = xyz_nomvalue - refxyz #XYZ

            diff_env_value = rot.dot(diff_value.T).T*1000
            diff_env_nomvalue = rot.dot(diff_nomvalue.T).T*1000
            env_sigma = rot.dot(xyz_sigma.T).T*1000

            frame = _pd.DataFrame(_np.column_stack([diff_env_value,diff_env_nomvalue,env_sigma]),columns = m_index).set_index(dataset[i].index)
            envs[i] = _pd.concat([frame],keys=[mode],axis=1)
            if dump is not None:
                _dump_write(filename = env_path, data=envs[i], num_cores=24, cname='zstd')
    return envs

def get_xyz_site(staDb_ref_xyz,site_name):
    #return reference XYZ coordinates for specified station from staDb
    return staDb_ref_xyz[staDb_ref_xyz['Station'] == site_name][['X','Y','Z']].squeeze().values #Squeeze to series. Not to create array in array

def get_ref_xyz_sites(staDb_path):
    '''Function reads staDb file provided. Uses pandas, as default staDb object can not return XYZ coordinates???'''
    read = _pd.read_csv(staDb_path,delimiter=r'\s+',names=list(range(11)))
    positions = read[read.iloc[:,1]=='STATE']
    # refxyz = get_xyz_site(positions)
    xyz_table = positions[[0,4,5,6]]
    xyz_table.reset_index(inplace=True,drop=True)

    staDb_xyz = _pd.DataFrame()
    staDb_xyz['Station'] = xyz_table[0]
    staDb_xyz[['X','Y','Z']] = xyz_table[[4,5,6]].astype('float')
    return staDb_xyz

def remove_30h(tmp_dir):
    #'rnx_dr/SITE/YEAR/DAY/*_30h.dr.gz
    files = _glob.glob(_os.path.join(tmp_dir,'rnx_dr/*/*/*/*_30h.dr.gz'))
    for file in files: _os.remove(file)

def remove_32h(tmp_dir):
    #'rnx_dr/SITE/YEAR/DAY/*_32h.dr.gz
    files = _glob.glob(_os.path.join(tmp_dir,'rnx_dr/*/*/*/*_32h.dr.gz'))
    for file in files: _os.remove(file)

def wetz(tdps):
    wetz = _np.ndarray((tdps.shape),dtype = object)
    for i in range(wetz.shape[0]):
        dataframe = tdps[i].value #Only value part is used
        #find column needed
        columns = dataframe.columns
        wetz_column_name = columns[_pd.Series(columns).str.contains('WetZ')].values[0]
        wetz[i] = dataframe[[wetz_column_name,]]
    return wetz

def get_const_df(ConstellationInfoFile,constellation):
    '''returns timeline of SVs count for the constellation specified. The constellationInfo file is of the JPL's format'''
    #reading constellation file
    file = _pd.read_fwf(ConstellationInfoFile,comment='#',header=None,)
    #selecting constellation needed
    if constellation not in ['GPS','GLONASS']:
        raise ValueError('GPS or GLONASS only')
    if constellation == 'GLONASS':
        data = file[file[1]=='SLO']
    if constellation == 'GPS':
        prn = file[file[1]=='PRN']
        data = prn[prn[6]=='G']

    df = _pd.DataFrame()
    df['SV'] = data[0]
    df['begin'] = (data[2] +" "+ data[3]).astype('datetime64')


    end_dates = data[4].copy()
    end_dates[end_dates=='0000-00-00'] = '2100-01-01' #changing 0 date to year 2100 to convert to datetime64
    end = (end_dates +" "+ data[5]).astype('datetime64')

    df['end'] = end
    df.sort_values(by=['begin','end'],inplace=True)
    #build unique SV table
    unique_SV = df['SV'].unique()
    df_SV = _pd.DataFrame(index=unique_SV,columns=['begin','end'])
    for SV in unique_SV:
        df_SV.loc[SV]['begin'] = df[df['SV'] == SV]['begin'].min()
        df_SV.loc[SV]['end'] = df[df['SV'] == SV]['end'].max()

    df_SV.begin = df_SV.begin.astype('datetime64')
    df_SV.end = df_SV.end.astype('datetime64')
    begin = df_SV['begin'].values
    end = df_SV['end'].values
    # end_dates
    array_count = _np.arange(df_SV.shape[0])+1


    for date in end:
        array_count[begin>=date]-= 1

    df_SV['count'] = array_count
    df_SV['SV'] = df_SV.index

    begin_day,end_day = df_SV.begin.values.astype('datetime64[D]').astype('datetime64')[[0,-1]]

    daily_date = _np.arange(begin_day,end_day)
    daily_count = _np.ndarray((daily_date.shape))

    for i in range(df_SV.shape[0]-1):

        daily_count[(daily_date>=df_SV['begin'].values[i])&(daily_date<df_SV['begin'].values[i+1])] = df_SV['count'][i]
    df_total = _pd.DataFrame(index=daily_date)
    df_total['count'] = daily_count.astype(int)

    return df_total

def _CRC32_from_file(filename):
    with open(filename,'rb') as file:
        buf = file.read()
    return "%08X" % (_binascii.crc32(buf) & 0xFFFFFFFF)

def _blq2blq_df_slow(blq_file):
    '''Original blq2blq_df function. Reads blq file specified and returns blq dataframe as needed for analysis.
    SLOW on larger blq files (e.g. NZ blq with 183 stations takes ~1 sec to execute)'''
    _pd.options.display.max_colwidth = 200 #By default truncates text
    blq = _blq2hardisp(blq_file=blq_file)
    tmp_df_gather = []
    for blq_record in blq:
        blq_record_df = _pd.Series(blq_record[1]).str.split(r'\n',expand=True).squeeze().str.strip().str.split(r'\s+',expand=True,).T
        blq_record_df.index = _pd.MultiIndex.from_product([[blq_record[0]],['M2','S2','N2','K2','K1','O1','P1','Q1','MF','MM','SSA']])
        tmp_df_gather.append(blq_record_df)
    df = _pd.concat(tmp_df_gather)
    df.columns =  _pd.MultiIndex.from_product([['OTL'],['amplitude','phase'],['up','east','north'],['value']])
    df = df.swaplevel(1,2,axis=1)

    df_std = _pd.DataFrame(0,index=df.index,columns=_pd.MultiIndex.from_product([['OTL'],['up','east','north'],['amplitude','phase'],['std']]))
    return _pd.concat([df,df_std],axis=1).astype(float)

def blq2blq_df(blq_file,XYZ=False):
    '''A faster version of original blq2blq_df. Has no performance penalty on larger blq files.
    Reads blq file specified and returns blq dataframe as needed for analysis. NZ blq with 183 stations takes ~129 msec to execute'''
    _pd.options.display.max_colwidth = 200 #By default truncates text
    blq = _blq2hardisp(blq_file=blq_file)
    data_raw = _pd.Series(blq[:,1]).str.split('\n',expand=True)
    sta_names = blq[:,0]

    buf=[]
    for column in data_raw.columns:
        tmp = data_raw[column].str.split(pat=None,expand=True).astype(float)
        tmp.columns= ['M2','S2','N2','K2','K1','O1','P1','Q1','MF','MM','SSA']
        tmp.index = sta_names
        buf.append(tmp.stack())
    components = ['up','east','north']
    if XYZ: components = ['X','Y','Z'] #as in GipsyX com file (based on blq)
    values = _pd.concat(buf,axis=1,keys=_pd.MultiIndex.from_product([['OTL'],['amplitude','phase'],components,['value']]).swaplevel(i=2,j=1))
    sigmas = _pd.DataFrame(_np.zeros(values.shape),index = values.index,columns=_pd.MultiIndex.from_product([['OTL'],['amplitude','phase'],components,['std']]).swaplevel(i=2,j=1))

    return _pd.concat([values,sigmas],axis=1)

def parse_otl_name(filepath):
    model_data = _pd.Series(_os.path.basename(filepath)).str.split(pat=r'_(?!atl)(?!disp)|\.csv',expand=True)
    return model_data

def csv2df(filepath = '../otl_comparison/otl_construct/FES2012_PREM_direct.csv',as_blq_df=False):
    '''Reads MSB csv file and outputs a DataFrame with models in heading or a blq_df (as needed for norm_table)'''
    raw_file = _pd.read_csv(filepath_or_buffer=filepath,header=None,names=[0,1,2,3,'amplitude','phase'])
    # 0=up, 1=North-South, 2=East-West
    raw_file[2] = raw_file[2].astype('category').cat.rename_categories(['up','north','east'])
    raw_file[3] = raw_file[3].str.strip().str.upper()
    raw_file[0] = raw_file[0].str.strip().str.upper()
    df_values = raw_file[[0,2,3,'amplitude','phase']].pivot_table(columns=2,index=[0,3],)
    df_values.loc(axis=1)['phase',['north','east']]+=180 #+180 deg to horizontal phase to convert to blq
    df_values[df_values.loc(axis=1)[['phase',],['east','north']]>180] -=360
    df_values.index.names = [None,None]
    df_values.columns.names = [None,None]
    if as_blq_df:
        df_values['amplitude']/=1000 #MSB has values in mm so we divide by 1000 to be consistent with blq
        df_std = df_values.copy() * 0
        df = _pd.concat([df_values,df_std],keys=['value','std'],axis=1)
        df = df.swaplevel(axis=1,i=0,j=2,)
        df = _pd.concat([df],keys=['OTL'],axis=1)
        return df #output is in meters
    if not as_blq_df:
        model_data = parse_otl_name(filepath)
        df_values = _pd.concat([df_values],keys=[model_data[2][0]],axis=1)
        df_values = _pd.concat([df_values],keys=[model_data[1][0]],axis=1)
        df_values = _pd.concat([df_values],keys=[model_data[0][0]],axis=1)
        return df_values #output is in mm

def norm_table(blq_df, custom_blq_path,normalize=True,gps_only = False,ascomplex_xy=False):
    '''converts blq into set of parameters needed for plotting. Accepts MSB csv files by separating file extension.
    If .blq -> Hans-Georg blq; if .csv -> MSB csv'''
    blq_df = blq_df.astype(float)
    coeff95 = 1.96
    if not custom_blq_path:pass
    else:
        file_ext = _os.path.splitext(custom_blq_path)[1] #getting file extension. Either .blq or .csv
        # a = 2 if file_ext == '.csv' else 3 if file_ext == '.blq' else print('{} is unknown filetype'.format(file_ext))
        if file_ext == '.blq':
            blq_df_custom = blq2blq_df(custom_blq_path)#reading custom blq path and converting it to df
        elif file_ext == '.csv':
            blq_df_custom = csv2df(custom_blq_path,as_blq_df=True)#reading MSB formatted file
        else: print('{} is unknown filetype'.format(file_ext))

        stations_present_input = blq_df.index.levels[0] #stores a list of stations present in the input eterna analisys df
        stations_present_custom  = blq_df_custom.index.levels[0] #stores a list of stations present in custom blq file specified
        #check if all stations from eterna ana exist in custom file
        missing_stations_count = (~_np.isin(stations_present_input,stations_present_custom)).sum()
        if missing_stations_count > 0:
            raise ValueError('{} stations missing from {}'.format(missing_stations_count, custom_blq_path))
        else:
            blq_df.update(blq_df_custom)

        amplitude = blq_df.xs(key = ('amplitude','value'),axis=1,level = (2,3),drop_level=True)*1000
        phase = blq_df.xs(key = ('phase','value'),axis=1,level = (2,3),drop_level=True)

    std_a = blq_df.xs(key = ('amplitude','std'),axis=1,level = (2,3),drop_level=True)*1000
    std_p = blq_df.xs(key = ('phase','std'),axis=1,level = (2,3),drop_level=True)

    x = _np.cos(_np.deg2rad(phase)) * amplitude
    y = _np.sin(_np.deg2rad(phase)) * amplitude
    if normalize:
        x_norm = x['OTL'].copy()
        y_norm = y['OTL'].copy()
        for mode in x.columns.levels[0]:
            x[mode] -= x_norm
            y[mode] -= y_norm

    if ascomplex_xy: return x+1j*y

    semiAxisA = std_a
    semiAxisP = _np.tan(_np.deg2rad(std_p))*amplitude
    #returns x,y width, height. angle should be computed as arccos(x/y)
    width = semiAxisA*2*coeff95 #should be multiplied by 2 as axis and not radius
    height = semiAxisP*2*coeff95
    return x,y,width,height,phase


def check_date_margins(begin,end,years_list):
    begin_data = _pd.Timestamp(_np.asarray(years_list).min().astype(str))
    end_data = _pd.Timestamp((_np.asarray(years_list).max()+1).astype(str))
    if begin is not None:
        begin = _pd.Timestamp(begin);print('Overriding {} begin with {}'.format(begin_data,begin))
        if begin < begin_data:
            print('{} is before the data. Changing to data begin at {}'.format(begin,begin_data))
            begin = begin_data
    else: begin = begin_data
    if end is not None:
        end = _pd.Timestamp(end); print('Overriding {} end with {}'.format(end_data,end))
        # if end > end_data:
        #     print('{} is after the data. Changing to data end at {}'.format(end,end_data))
        #     end = end_data
    else: end = end_data
    return begin.to_datetime64(), end.to_datetime64()

def date2yyyydoy(date):
    date = _pd.Timestamp(date)
    doy = str((date.dayofyear -1)).zfill(3)
    yyyy = str(date.year)
    return '{}.{}'.format(yyyy,doy)

def ECDF(x_series):
    '''expects pandas dataframe'''
    x = x_series.sort_values().copy()
    nobs = x.shape[0]
    y = _np.linspace(1./nobs,1,nobs)
    x = x.to_frame()
    x['ECDF'] = y
    return x
# from datetime import datetime
# def _from_ordinal(x, tz=None):
#     ix = int(x)
#     dt = datetime.fromordinal(ix)
#     remainder = float(x) - ix
#     hour, remainder = divmod(24 * remainder, 1)
#     minute, remainder = divmod(60 * remainder, 1)
#     second, remainder = divmod(60 * remainder, 1)
#     microsecond = int(1e6 * remainder)
#     if microsecond < 10:
#         microsecond = 0  # compensate for rounding errors
#     dt = datetime(dt.year, dt.month, dt.day, int(hour), int(minute),
#                   int(second), microsecond)
#     if tz is not None:
#         dt = dt.astimezone(tz)

#     if microsecond > 999990:  # compensate for rounding errors
#         dt += timedelta(microseconds=1e6 - microsecond)

#     return dt

# _from_ordinal(733414.07083333)

# import numpy as _np
# J2000origin = _np.datetime64('2000-01-01 12:00:00')
# date = '2019-01-01 00:00:00'
# J2000_seconds = (_np.datetime64(date) - J2000origin).astype(int)
# J2000_seconds

def struct_rnx(src_files_glob = '/array/bogdanm/GNSS_data/gnss-ga/*.gz', out_dir = False):
    '''Will extract all the necessary information from the filename and move to the respective dir YYYY/DDD/
    For GA's ftp:  src_files_glob = ".... /*.Z"
    src_files_glob = '/array/bogdanm/GNSS_data/gnss-ga/*.gz'
    if out_dir not specified - same folder as src'''
    if not out_dir:
        out_dir = _os.path.dirname(src_files_glob)
    out_dir= _os.path.abspath(out_dir)
    files = _pd.Series(_glob.glob(src_files_glob))
    print('Found {} files'.format(files.shape[0]))
    files.name = 'PATH_SRC'
    names = files.str.split('/',expand=True).iloc[:,-1]
    names.name = 'NAME'
    names_info = names.str.extract(r'(\w{4})(\d{3})\w{1}\.(\d{2})(.+)') # cannot use (\d{4}) as some files may have 'a', not '0'
    names_info.columns = ['SITE','DOY','YEAR','EXT']
    names_df = _pd.concat([names_info,names,files],axis=1)
    # years = names_df['YEAR'].unique().astype(int)+2000

    names_df['YEAR'] = (names_df['YEAR'].astype(int)+2000).astype(str)

#     out_dir = _os.path.dirname(files[0])
    names_df['PATH_DST'] = out_dir + '/' +names_df['YEAR'] +  '/' + names_df['DOY']  +'/'+names_df['NAME']

    #prepare dir structure
    for year_doy in (names_df['YEAR'] +  '/' + names_df['DOY']).unique():
        year_dir_path = _os.path.join(out_dir,year_doy)
        if not _os.path.exists(year_dir_path):
            _os.makedirs(year_dir_path)

    for i in range(names_df.shape[0]):
        _move(src=names_df.loc[i]['PATH_SRC'],dst=names_df.loc[i]['PATH_DST'])
