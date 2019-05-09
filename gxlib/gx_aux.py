import os as _os, re as _re, glob as _glob, sys as _sys
import numpy as _np
import pandas as _pd
import tqdm as _tqdm
from subprocess import Popen as _Popen, PIPE as _PIPE, STDOUT as _STDOUT
from multiprocessing import Pool as _Pool
import pyarrow as _pa 
import blosc as _blosc

PYGCOREPATH = "{}/lib/python{}.{}".format(_os.environ['GCOREBUILD'], _sys.version_info[0], _sys.version_info[1])
if PYGCOREPATH not in _sys.path:
    _sys.path.insert(0, PYGCOREPATH)
import gcore.EarthCoordTrans as _eo
import gcore.StationDataBase as StationDataBase
_regex_ID = _re.compile(r"1\.\W+S.+\W+Site Name\s+\:\s(.+|)\W+Four Character ID\s+\:\s(.+|)\W+Monument Inscription\s+\:\s(.+|)\W+IERS DOMES Number\s+\:\s(.+|)\W+CDP Number\s+\:\s(.+|)", _re.MULTILINE)
_regex_loc = _re.compile(r"2\.\W+S.+\W+City or Town\W+\:\s(.+|)\W+State or Province\W+\:\s(.+|)\W+Country\W+\:\s(.+|)\W+Tectonic Plate\W+\:\s(.+|)\W+.+\W+X.+\:\s(.+|)\W+Y..+\:\s(.+|)\W+Z.+\:\s(.+|)\W*Latitude.+\:\s(.+|)\W*Longitude.+\:\s(.+|)\W*Elevation.+\:\s(.+|)", _re.MULTILINE)
_regex_rec = _re.compile(r"3\.\d+\s+R.+\W+\:\s(.+|)\W+Satellite System\W+\:\s(.+|)\W+Serial Number\W+\:\s(.+|)\W+Firmware Version\W+\:\s(.+|)\W+Elevation Cutoff Setting\W+\:\s(.+|)\W+Date Installed\W+\:\s(.{10}|)(.{1}|)(.{5}|)", _re.MULTILINE)
_regex_ant = _re.compile(r"4\.\d\s+A.+\W+:\s(\w+\.?\w+?|)\s+(\w+|)\W+Serial Number\W+:\s(\w+\s?\w+?|)\W+Antenna.+:\s(.+|)\W+Marker->ARP Up.+:\s(.+|)\W+Marker->ARP North.+:\s(.+|)\W+Marker->ARP East.+:\s(.+|)\W+Alignment from True N\W+:\s(.+|)\W+Antenna Radome Type\W+:\s(.+|)\W+Radome Serial Number\W+:\s(.+|)\W+Antenna Cable Type\W+:\s(.+|)\W+Antenna Cable Length\W+:\s(.+|)\W+Date Installed\W+:\s(.{10})T?(.{5}|)Z?\W+Date Removed\W+\:(?:\s\(?(.{10})T(.{5}|)Z?|)\W+Additional Information\W+:\s(.+|)\W+", _re.MULTILINE)

J2000origin = _np.datetime64('2000-01-01 12:00:00')

def _check_stations(stations_list,tmp_dir,project_name):
    '''Check presence of stations in the project and outputs corrected station list'''
    stations_list = _np.core.defchararray.upper(stations_list)
    #check if station from input is in the folder
    gd2e_stations_list = _os.listdir(tmp_dir + '/gd2e/'+project_name)
    station_exists = _np.isin(stations_list,gd2e_stations_list)

    checked_stations = stations_list[station_exists==True]
    return checked_stations

def _dump_write(filename,data,num_cores=24,cname='lz4'):
    '''Serializes the input (may be a list of dataframes or else) and uses blosc to compress it and write to a file specified'''

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
        logs[i] = _glob.glob(IGS_logs_dir + '/*/' + stations_list[i].lower() +'*')[0]

    with open(staDb_path,'w') as output:
        output.write("KEYWORDS: ID STATE ANT RX\n")  # POSTSEISMIC, LINK, END
        for file in logs:
            with open(file, 'r') as f:
                data = f.read()
        # Site ID
            matches_ID = _re.findall(_regex_ID, data)
        # Site Location, only one location line per BIGF log
            matches_loc = _re.findall(_regex_loc, data)
            output.write("{ID}  ID  {IERS} {loc_2} {loc_1}\n".format(ID=matches_ID[0][1], IERS=matches_ID[0][3] if matches_ID[0][3] != '' else 'UNKNOWN',
                                                            loc_2=matches_loc[0][1], loc_1=matches_loc[0][2]))

            output.write("{ID}  STATE 1-01-01 00:00:00 {X:.15e}  {Y:.15e} {Z:.15e} {X_v:.15e}  {Y_v:.15e} {Z_v:.15e}\n".format(ID=matches_ID[0][1],
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
                output.write("{ID}  RX {d_inst} {t_inst}:00 {rec_type} # {rec_num} {rec_fw_v}\n".format(ID=matches_ID[0][1], d_inst=rec[matchNum][5], t_inst=rec[
                    matchNum][7] if rec[matchNum][7] != '' else '00:00', rec_type=rec[matchNum][0], rec_num=rec[matchNum][2], rec_fw_v=rec[matchNum][3]))
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

                output.write("{ID}  ANT {d_inst} {t_inst}:00 {ant_type} {radome_type} {east} {north} {vertical} # {ant_num}\n".
                    format(ID=matches_ID[0][1], d_inst=ant[matchNum][12], t_inst=ant[matchNum][13] if ant[matchNum][13]!= '' else '00:00', ant_type=ant[matchNum][0],
                            radome_type=ant[matchNum][8] if ant[matchNum][8]!= '' else 'NONE', vertical=ant[matchNum][4], north=ant[matchNum][5], east=ant[matchNum][6], ant_num=ant[matchNum][2]))
    return staDb_path

def get_chalmers(staDb_path):
    '''Converts staDb to input for http://holt.oso.chalmers.se/loading/
    Name of station_________|	|Longitude (deg)	| Latitude (deg)	| Height (m) 
    //sala                        11.9264         57.3958         0.0000
    //ruler.................b................<...............<...............
    // Records starting with // are treated as comments'''
    staDb = StationDataBase.StationDataBase()  # creating staDb object
    staDb.read(staDb_path)  # reading staDb into staDb object
    
    max_t = 3.0e8  # maximum time value for the dataset on which available sites will be added to OTL computation with SPOTL
    names_stdb = _np.asarray(staDb.getStationList(), dtype=object)
    llh_stdb = _np.asarray(staDb.dumpLatLonHeights(epoch=max_t,
                                                    stationList=staDb.getStationList()))
    nllh = _np.column_stack((names_stdb, llh_stdb.T))

    for station in nllh:
        print('%-19.4s %15.4f %15.4f %15.4f'%(station[0],station[2],station[1],station[3]))


def _dr_size(dr_files):
    '''Returns ndarray with sizes of converted dr files. Based on this, selects bad and good files (bad files have size less than 20, technically empty).
    Bad file can be created by GipsyX in case input RNX file doesn't have enough data for conversion. Bad files should be filtered out of processing.
    The script can be converted to multiprocessing''' 
    size_array= _np.ndarray((dr_files.shape[0]))    

    for i in range(dr_files.shape[0]):
        size_array[i] = _os.path.getsize(dr_files[i]) #index of 1 means dr file path

    bad_files = dr_files[size_array==20]
    good_files = dr_files[size_array>20]

    return size_array,bad_files,good_files         


def _drinfo2df(dr_file):
    '''Calls a dataRecordInfo script on already converted to dr format RNX file with rnxEditGde.py.
    dr_file is an absolute path but if switching machines/dr_location we need to rerun'''
    drInfo_process = _Popen(args=['dataRecordInfo', '-file', _os.path.basename(dr_file)],
                                        stdout=_PIPE, stderr=_STDOUT, cwd=_os.path.dirname(dr_file))
    out = drInfo_process.communicate()[0]
    dr_Info_raw = _pd.Series(out.decode('ascii').splitlines()).str.split(pat=r':\s', expand=True)

    df = _pd.DataFrame(index=[0])
    df['n_records'] = dr_Info_raw.iloc[0, 1]
    time_vals = _pd.to_datetime(dr_Info_raw.iloc[1:3, 1]).values
    df['begin'] = time_vals[0]
    df['end'] = time_vals[1]
    df['n_receivers'] = _pd.to_numeric(dr_Info_raw.iloc[3, 1])
    df['n_transmitters'] = _pd.to_numeric(dr_Info_raw.iloc[5, 1])
    df['station_name'] = dr_Info_raw.iloc[4, 0].strip()
    transmitter_types = _np.unique(((dr_Info_raw.iloc[6:, 0]).str.strip()).str[:1].values)
    df['GPS'] = _np.max(_np.isin(transmitter_types,'G'))
    df['GLONASS'] = _np.max(_np.isin(transmitter_types,'R'))
    df['path'] = _pd.Series(dr_file).str.extract(r'(\/rnx_dr.+)')
    
    return df

def get_drinfo(tmp_dir,num_cores,tqdm):
    '''Analysis is done over all stations in the projects tmp_dir. The problem to run analysis on all converted fies is 30 hour files
    Naming convention for 30h files was changed
    that are present in the directory so original files are difficult to extract. Need to change merging naming'''
    tmp_dir = _os.path.abspath(tmp_dir); num_cores = int(num_cores) #safety precaution if str value is specified
    
    #find all dr.gx files in rnx_dr folder
    dr_files = _glob.glob('{}/rnx_dr/*/*/*/.dr.gz'.format(tmp_dir)) #after change of 30h naming this will select only original files

    dr_good = _dr_size(dr_files)[2] #Only good files will be analysed and processed. Bad ignored. Size array may be used for additional dr analysis
    # dr_size_array, dr_empty, dr_good = _dr_size(rnx_files)

    num_cores = num_cores if dr_good.shape[0] > num_cores else dr_good.shape[0]
    print ('Number of files to process:', dr_good.shape[0],'| Adj. num_cores:', num_cores, end=' ')
    with _Pool(processes = num_cores) as p:
        if tqdm: rs = _pd.concat(list(_tqdm.tqdm_notebook(p.imap(_drinfo2df, dr_good), total=dr_good.shape[0])),axis=0)
        else: rs = _pd.concat(p.map(_drinfo2df, dr_good),axis=0)

    #Saving extracted data for furthe processing
    _dump_write(data = rs,filename=tmp_dir+'rnx_dr/drInfo.zstd',cname='zstd',num_cores=num_cores)

'''section of solution to ENV conversion'''
def _xyz2env(dataset,stations_list,reference_df):
    '''Correct way of processing smooth0_0.tdp file. Same as tdp2EnvDiff.py
    tdp2EnvDiff outputs in cm. We need in mm.
    Outputs a MultiIndex DataFrame with value and nomvalue subsections to control tdp_in procedure
    '''
    envs = _np.ndarray((len(dataset)),dtype=object)

    for i in range(len(dataset)):
        # Creating MultiIndex:
        arrays_value=[['value','value','value'],[stations_list[i]+'.E', stations_list[i]+'.N', stations_list[i]+'.V']]
        arrays_nomvalue=[['nomvalue','nomvalue','nomvalue'],[stations_list[i]+'.E', stations_list[i]+'.N', stations_list[i]+'.V']]
        arrays_sigma=[['sigma','sigma','sigma'],[stations_list[i]+'.E', stations_list[i]+'.N', stations_list[i]+'.V']]
        
        m_index_value = _pd.MultiIndex.from_arrays(arrays=arrays_value)
        m_index_nomvalue = _pd.MultiIndex.from_arrays(arrays=arrays_nomvalue)
        m_index_sigma = _pd.MultiIndex.from_arrays(arrays=arrays_sigma)
        
        xyz_value = dataset[i]['value'].iloc[:,[1,2,3]]
        xyz_nomvalue = dataset[i]['nomvalue'].iloc[:,[1,2,3]]
        xyz_sigma = dataset[i]['sigma'].iloc[:,[1,2,3]]

        refxyz = get_xyz_site(reference_df,stations_list[i]) #stadb values. Median also possible. Another option is first 10-30% of data
        # refxyz = xyz.median() #ordinary median as reference. Good for data with no trend. Just straight line. 
        # refxyz = xyz.iloc[:int(len(xyz)*0.5)].median() #normalizing on first 10% of data so the trends should be visualized perfectly.
        rot = _eo.rotEnv2Xyz(refxyz).T #XYZ

        diff_value = xyz_value - refxyz #XYZ
        diff_nomvalue = xyz_nomvalue - refxyz #XYZ
        
        diff_env_value = rot.dot(diff_value.T)*1000
        diff_env_nomvalue = rot.dot(diff_nomvalue.T)*1000
        env_sigma = rot.dot(xyz_sigma.T)*1000
        
        frame_value = _pd.DataFrame(diff_env_value, index=m_index_value).T
        frame_nomvalue = _pd.DataFrame(diff_env_nomvalue, index=m_index_nomvalue).T
        frame_sigma = _pd.DataFrame(env_sigma, index=m_index_sigma).T
        envs[i] = _pd.concat((frame_value,frame_nomvalue,frame_sigma),axis=1).set_index(dataset[i].index)
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