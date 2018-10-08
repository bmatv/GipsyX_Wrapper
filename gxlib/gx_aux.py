import os, re, glob
import numpy as np
import pandas as pd


regex_ID = re.compile(r"1\.\W+S.+\W+Site Name\s+\:\s(.+|)\W+Four Character ID\s+\:\s(.+|)\W+Monument Inscription\s+\:\s(.+|)\W+IERS DOMES Number\s+\:\s(.+|)\W+CDP Number\s+\:\s(.+|)", re.MULTILINE)
regex_loc = re.compile(r"2\.\W+S.+\W+City or Town\W+\:\s(.+|)\W+State or Province\W+\:\s(.+|)\W+Country\W+\:\s(.+|)\W+Tectonic Plate\W+\:\s(.+|)\W+.+\W+X.+\:\s(.+|)\W+Y..+\:\s(.+|)\W+Z.+\:\s(.+|)\W*Latitude.+\:\s(.+|)\W*Longitude.+\:\s(.+|)\W*Elevation.+\:\s(.+|)", re.MULTILINE)
regex_rec = re.compile(r"3\.\d+\s+R.+\W+\:\s(.+|)\W+Satellite System\W+\:\s(.+|)\W+Serial Number\W+\:\s(.+|)\W+Firmware Version\W+\:\s(.+|)\W+Elevation Cutoff Setting\W+\:\s(.+|)\W+Date Installed\W+\:\s(.{10}|)(.{1}|)(.{5}|)", re.MULTILINE)
regex_ant = re.compile(r"4\.\d\s+A.+\W+:\s(\w+\.?\w+?|)\s+(\w+|)\W+Serial Number\W+:\s(\w+\s?\w+?|)\W+Antenna.+:\s(.+|)\W+Marker->ARP Up.+:\s(.+|)\W+Marker->ARP North.+:\s(.+|)\W+Marker->ARP East.+:\s(.+|)\W+Alignment from True N\W+:\s(.+|)\W+Antenna Radome Type\W+:\s(.+|)\W+Radome Serial Number\W+:\s(.+|)\W+Antenna Cable Type\W+:\s(.+|)\W+Antenna Cable Length\W+:\s(.+|)\W+Date Installed\W+:\s(.{10})T?(.{5}|)Z?\W+Date Removed\W+:\s(.{10})T?(.{5}|)Z?\W+Additional Information\W+:\s(.+|)", re.MULTILINE)


def gen_staDb(tmp_dir,project_name,stations_list,IGS_logs_dir):
    '''Creates a staDb file from IGS logs'''
    #Making staDb directory in tmp folder 
    staDb_dir = tmp_dir + '/staDb/' + project_name + '/'
    staDb_file = staDb_dir + project_name + '.staDb'
    if not os.path.exists(staDb_dir):
        os.makedirs(staDb_dir)
    #getting paths to all log files needed    
    logs = np.ndarray((len(stations_list)),dtype=object)
    for i in range(len(stations_list)):
        logs[i] = glob.glob(IGS_logs_dir + '/*/' + stations_list[i].lower() +'*')[0]

    with open(staDb_file,'w') as output:
        output.write("KEYWORDS: ID STATE ANT RX\n")  # POSTSEISMIC, LINK, END
        for file in logs:
            with open(file, 'r') as f:
                data = f.read()
        # Site ID
            matches_ID = re.findall(regex_ID, data)
        # Site Location, only one location line per BIGF log
            matches_loc = re.findall(regex_loc, data)
            output.write("{ID}  ID  {IERS} {loc_2} {loc_1}\n".format(ID=matches_ID[0][1], IERS=matches_ID[0][3] if matches_ID[0][3] != '' else 'NONE',
                                                            loc_2=matches_loc[0][1], loc_1=matches_loc[0][2]))

            output.write("{ID}  STATE 1-01-01 00:00:00 {X:.15e}  {Y:.15e} {Z:.15e} {X_v:.15e}  {Y_v:.15e} {Z_v:.15e}\n".format(ID=matches_ID[0][1],
                                                                                                                      X=float(matches_loc[0][4]) if matches_loc[0][4] != '' else 0,
                                                                                                                      Y=float(matches_loc[0][5]) if matches_loc[0][5] != '' else 0,
                                                                                                                      Z=float(matches_loc[0][6]) if matches_loc[0][6] != '' else 0,
                                                                                                                      X_v=0, Y_v=0, Z_v=0))
        # Receiver Information
            rec = []
            matches_rec = re.finditer(regex_rec, data)
            for matchNum, match in enumerate(matches_rec):
                for groupNum in range(0, len(match.groups())):
                    groupNum = groupNum + 1
                rec.append(match.groups())
                output.write("{ID}  RX {d_inst} {t_inst}:00 {rec_type} {rec_num} {rec_fw_v}\n".format(ID=matches_ID[0][1], d_inst=rec[matchNum][5], t_inst=rec[
                      matchNum][7] if rec[matchNum][7] != '' else '00:00', rec_type=rec[matchNum][0], rec_num=rec[matchNum][2], rec_fw_v=rec[matchNum][3]))
        # Antenna Information
            ant = []
            matches_ant = re.finditer(regex_ant, data)
            for matchNum, match in enumerate(matches_ant):
                for groupNum in range(0, len(match.groups())):
                    groupNum = groupNum + 1
                ant.append(match.groups())
                output.write("{ID}  ANT {d_inst} {t_inst}:00 {ant_type} {radome_type} {up} {north} {east} {ant_num}\n".
                      format(ID=matches_ID[0][1], d_inst=ant[matchNum][12], t_inst=ant[matchNum][13] if ant[matchNum][13]!= '' else '00:00', ant_type=ant[matchNum][0],
                             radome_type=ant[matchNum][8], up=ant[matchNum][4], north=ant[matchNum][5], east=ant[matchNum][6], ant_num=ant[matchNum][2]))
    return staDb_file

def select_rnx(stations_list,years_list,rnx_dir):
    station_files = np.zeros((len(stations_list)),dtype=object)
    for i in range(len(stations_list)):
        station_files[i] = sorted(glob.glob(rnx_dir+'/'+str(years_list[0])+'/*/'+ np.str.lower(stations_list[i])+'*'+str(years_list[0])[2:]+'d.Z')) #populate with years_list[0] value
        for j in range(1, len(years_list)):
            station_files[i] = np.concatenate((station_files[i], np.asarray(sorted(glob.glob(rnx_dir+'/'+str(years_list[j])+'/*/'+
                                                            np.str.lower(stations_list[i])+'*'+str(years_list[j])[2:]+'d.Z')))),axis=0)
    return station_files #ndarray of station specific file lists

def analyse(stations_list,years_list,rnx_files):
    '''Small analysis module that outputs a pandas dataframe with number of daily observations by station (columns) and year (rows).
    Based on select_rnx function'''
    output = pd.DataFrame(columns=stations_list,index=years_list)
    for i in range(len(stations_list)):
        tmp = pd.Series(rnx_files[i]).str.split('/',expand=True)
#             print(self.stations_list[i],end='\n---------------\n')
        for year in years_list:
            output.loc[year,stations_list[i]] = len(tmp[tmp.iloc[:,-3]==str(year)])
    return output