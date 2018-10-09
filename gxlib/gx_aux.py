import os as _os, re as _re, glob as _glob
import numpy as _np
import pandas as _pd
from subprocess import Popen as _Popen, PIPE as _PIPE, STDOUT as _STDOUT
from multiprocessing import Pool as _Pool

_regex_ID = _re.compile(r"1\.\W+S.+\W+Site Name\s+\:\s(.+|)\W+Four Character ID\s+\:\s(.+|)\W+Monument Inscription\s+\:\s(.+|)\W+IERS DOMES Number\s+\:\s(.+|)\W+CDP Number\s+\:\s(.+|)", _re.MULTILINE)
_regex_loc = _re.compile(r"2\.\W+S.+\W+City or Town\W+\:\s(.+|)\W+State or Province\W+\:\s(.+|)\W+Country\W+\:\s(.+|)\W+Tectonic Plate\W+\:\s(.+|)\W+.+\W+X.+\:\s(.+|)\W+Y..+\:\s(.+|)\W+Z.+\:\s(.+|)\W*Latitude.+\:\s(.+|)\W*Longitude.+\:\s(.+|)\W*Elevation.+\:\s(.+|)", _re.MULTILINE)
_regex_rec = _re.compile(r"3\.\d+\s+R.+\W+\:\s(.+|)\W+Satellite System\W+\:\s(.+|)\W+Serial Number\W+\:\s(.+|)\W+Firmware Version\W+\:\s(.+|)\W+Elevation Cutoff Setting\W+\:\s(.+|)\W+Date Installed\W+\:\s(.{10}|)(.{1}|)(.{5}|)", _re.MULTILINE)
_regex_ant = _re.compile(r"4\.\d\s+A.+\W+:\s(\w+\.?\w+?|)\s+(\w+|)\W+Serial Number\W+:\s(\w+\s?\w+?|)\W+Antenna.+:\s(.+|)\W+Marker->ARP Up.+:\s(.+|)\W+Marker->ARP North.+:\s(.+|)\W+Marker->ARP East.+:\s(.+|)\W+Alignment from True N\W+:\s(.+|)\W+Antenna Radome Type\W+:\s(.+|)\W+Radome Serial Number\W+:\s(.+|)\W+Antenna Cable Type\W+:\s(.+|)\W+Antenna Cable Length\W+:\s(.+|)\W+Date Installed\W+:\s(.{10})T?(.{5}|)Z?\W+Date Removed\W+:\s(.{10})T?(.{5}|)Z?\W+Additional Information\W+:\s(.+|)", _re.MULTILINE)

J2000origin = _np.datetime64('2000-01-01 12:00:00')

def gen_staDb(tmp_dir,project_name,stations_list,IGS_logs_dir):
    '''Creates a staDb file from IGS logs'''
    #Making staDb directory in tmp folder 
    staDb_dir = tmp_dir + '/staDb/' + project_name + '/'
    staDb_file = staDb_dir + project_name + '.staDb'
    if not _os.path.exists(staDb_dir):
        _os.makedirs(staDb_dir)
    #getting paths to all log files needed    
    logs = _np.ndarray((len(stations_list)),dtype=object)
    for i in range(len(stations_list)):
        logs[i] = _glob.glob(IGS_logs_dir + '/*/' + stations_list[i].lower() +'*')[0]

    with open(staDb_file,'w') as output:
        output.write("KEYWORDS: ID STATE ANT RX\n")  # POSTSEISMIC, LINK, END
        for file in logs:
            with open(file, 'r') as f:
                data = f.read()
        # Site ID
            matches_ID = _re.findall(_regex_ID, data)
        # Site Location, only one location line per BIGF log
            matches_loc = _re.findall(_regex_loc, data)
            output.write("{ID}  ID  {IERS} {loc_2} {loc_1}\n".format(ID=matches_ID[0][1], IERS=matches_ID[0][3] if matches_ID[0][3] != '' else 'NONE',
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
                output.write("{ID}  RX {d_inst} {t_inst}:00 {rec_type} {rec_num} {rec_fw_v}\n".format(ID=matches_ID[0][1], d_inst=rec[matchNum][5], t_inst=rec[
                      matchNum][7] if rec[matchNum][7] != '' else '00:00', rec_type=rec[matchNum][0], rec_num=rec[matchNum][2], rec_fw_v=rec[matchNum][3]))
        # Antenna Information
            ant = []
            matches_ant = _re.finditer(_regex_ant, data)
            for matchNum, match in enumerate(matches_ant):
                for groupNum in range(0, len(match.groups())):
                    groupNum = groupNum + 1
                ant.append(match.groups())
                output.write("{ID}  ANT {d_inst} {t_inst}:00 {ant_type} {radome_type} {up} {north} {east} {ant_num}\n".
                      format(ID=matches_ID[0][1], d_inst=ant[matchNum][12], t_inst=ant[matchNum][13] if ant[matchNum][13]!= '' else '00:00', ant_type=ant[matchNum][0],
                             radome_type=ant[matchNum][8], up=ant[matchNum][4], north=ant[matchNum][5], east=ant[matchNum][6], ant_num=ant[matchNum][2]))
    return staDb_file

def _dr_size(rnx_files_in_out):
    '''Returns ndarray with sizes of converted dr files. Based on this, selects bad and good files (bad files have size less than 20, technically empty).
    Bad file can be created by GipsyX in case input RNX file doesn't have enough data for conversion. Bad files should be filtered out of processing.
    The script can be converted to multiprocessing''' 
    size_array= _np.ndarray((rnx_files_in_out.shape),dtype = object)
    bad_files = _np.ndarray((rnx_files_in_out.shape),dtype = object)
    good_files = _np.ndarray((rnx_files_in_out.shape),dtype = object)        

    for i in range(len(rnx_files_in_out)):
        tmp = _np.ndarray((len(rnx_files_in_out[i])))
        for j in range(len(tmp)):
            tmp[j] = _os.path.getsize(rnx_files_in_out[i][j,1]) #index of 1 means dr file path

        size_array[i] = _np.column_stack((rnx_files_in_out[i],tmp))
        bad_files[i] = rnx_files_in_out[i][tmp==20]
        good_files[i] = rnx_files_in_out[i][tmp!=20]

    return size_array,bad_files,good_files        


def _drinfo(dr_file):
    '''Calls a dataRecordInfo script on already converted to dr format RNX file with rnxEditGde.py.'''
    drInfo_process = _Popen(args=['dataRecordInfo', '-file', _os.path.basename(dr_file)],
                                        stdout=_PIPE, stderr=_STDOUT, cwd=_os.path.dirname(dr_file))
    out, err = drInfo_process.communicate()
    dr_Info_raw = _pd.Series(out.decode('ascii').splitlines()).str.split(pat=':\s', expand=True)

    number_of_records = _pd.to_numeric(dr_Info_raw.iloc[0, 1])
    timeframe = _pd.to_datetime(dr_Info_raw.iloc[1:3, 1])
    number_of_receivers = _pd.to_numeric(dr_Info_raw.iloc[3, 1])
    number_of_transmitters = _pd.to_numeric(dr_Info_raw.iloc[5, 1])
    site_name = dr_Info_raw.iloc[4, 0].strip()
    transmitter_types = _np.unique(
        ((dr_Info_raw.iloc[6:, 0]).str.strip()).str[:1].values)

    return _np.asarray(( site_name, number_of_records, _np.datetime64(timeframe[1]), _np.datetime64(timeframe[2]),
                        number_of_receivers, number_of_transmitters,transmitter_types, dr_file))

def get_drinfo(rnx_files_in_out, stations_list, years_list, tmp_dir, num_cores):
    ''' Takes a list of all the rnx files of the project that were converted with rnxEditGde.py. rnx_files_in_out is essentially an array of shape: [[rnx_in_path,rnx_out_path],...]'''
    num_cores = int(num_cores) #safety precaution if str value is specified
    rs = _np.ndarray((len(stations_list)),dtype=object)

    # dr_size_array, dr_empty, dr_good = _dr_size(rnx_files)
    dr_good = _dr_size(rnx_files_in_out)[2] #Only good files will be analysed and processed. Bad ignored. Size array may be used for additional dr analysis

    
    for i in range(len(stations_list)):
        num_cores = num_cores if len(dr_good[i]) > num_cores else len(dr_good[i])

        chunksize = int(_np.ceil(len(dr_good[i]) / num_cores))
        print(stations_list[i],'station binary files analysis...')
        print ('Number of files to process:', len(dr_good[i]),'| Adj. num_cores:', num_cores,'| Chunksize:', chunksize,end=' ')
        
        pool = _Pool(processes=num_cores)
        rs[i] = _np.asarray(pool.map(func=_drinfo, iterable=dr_good[i][:,1], chunksize=chunksize))
        pool.close()
        pool.join()
        print('| Done!')

    
    #Saving extracted data for furthe processing
    _np.savez_compressed(file=tmp_dir+'/rnx_dr/drinfo',drinfo=rs,stations_list=stations_list,years_list=years_list)