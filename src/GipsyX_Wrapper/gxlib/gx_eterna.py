import numpy as _np
import pandas as _pd

from GipsyX_Wrapper.gxlib.gx_aux import J2000origin as _J2000origin, date2yyyydoy
from GipsyX_Wrapper.gxlib.gx_filter import _stretch, _avg_30
from GipsyX_Wrapper.gxlib.gx_hardisp import gen_synth_otl

import sys as _sys,os as _os
import shutil as _shutil
from subprocess import Popen as _Popen, PIPE as _PIPE
from multiprocessing import Pool
#Converting staDb coordinates to llh for eterna ini file
PYGCOREPATH = "{}/lib/python{}.{}".format(_os.environ['GCOREBUILD'],
                                          _sys.version_info[0], _sys.version_info[1])
if PYGCOREPATH not in _sys.path:
    _sys.path.insert(0, PYGCOREPATH)

import gcore.StationDataBase as StationDataBase


def _write_ETERNA(dataset, filename,sampling,station_name):
    '''sampling is 1800 for 30 min averaged files. Sampling detection may be done automatically if needed (histogram analysis of the dataset)'''
    def a(inp):
        return '{:8d}'.format(inp)
    def b(inp):
        return '{:6d}'.format(inp)
    def c(inp):
        if _np.isnan(inp):

            return '{:9.3s}'.format('')
        else:
            return '{:9.3f}'.format(inp)
        
    #test harmonic dataset
#     data = pandas.DataFrame(data=dataset,columns=['J2000_time','Data'])
    dataset = dataset[~_pd.isna(dataset.iloc[:,0])]
    data = _pd.DataFrame(index = dataset.index)
    time_int = dataset.index.values.astype(int)
    data['Time'] = time_int+ _J2000origin

    data['Date_et'] = data['Time'].dt.strftime('%Y%m%d').astype(int)
    data['Time_et'] = data['Time'].dt.strftime('%H%M%S').astype(int)
    data['Data'] = dataset.iloc[:,0]

    file_begin = 'C******************************************************************************\n'
    block_end = '\n99999999\n'
    file_end = '88888888'
    
    #Get blocks if there are gaps:
    block_ends = _np.where(time_int -_np.roll(time_int,1) > sampling)[0]
    block_ends = _np.append(block_ends,-1) #Adding -1 to extract the last block
    block_begin_ind = 0 #Init begin block index which is zero
    


    
    out_buf = file_begin
    block_number = 1
    for i in range(len(block_ends)):
        block_end_ind = block_ends[i]
        block = data.iloc[block_begin_ind:block_end_ind]
        # Additional check: if block len < 24 => skip block
        if block.shape[0] >= 24:
            
            block_begin = '{}               1.0000    1.0000     0.000         0    BLOCK{}\n77777777            0.000\n'.format(station_name,block_number)

            out_buf+=(block_begin +
                    data.iloc[block_begin_ind:block_end_ind].to_string(columns=['Date_et', 'Time_et', 'Data'], formatters={'Date_et': a, 'Time_et': b, 'Data': c},
                                    index=False, header=False) + block_end)
            block_begin_ind = block_end_ind
            block_number += 1 
        else: block_begin_ind = block_end_ind
            
    out_buf+=(file_end)
    
    with open(filename, 'w') as file:
        file.write(out_buf)
        
def _get_trend(dataset,deg=1):
    '''returns''' 
    dataset = dataset[(~_np.isnan(dataset)).min(axis=1)].copy()

    x = dataset.index.values
    y = dataset.values
    p = _np.polyfit(x,y,deg=deg)

    return _pd.DataFrame(p[0]*x[:,_np.newaxis] + p[1],index = x,columns=dataset.columns)

def _remove_outliers(dataset_env,v_type,coef=3):
    '''Runs detrending of the data to normalize to zero'''
    detrend = dataset_env[v_type] - _get_trend(dataset_env[v_type])   
    return detrend[(detrend.abs() <= detrend.std()*coef).min(axis=1)]

def _fill_block(block_):
    delta_var = block_.iloc[-1] - block_.iloc[0]
    delta_t = block_.index[-1] - block_.index[0]
    lin_coeff = (delta_var/ delta_t).values
    dT = (block_.index[1:-1]- block_.index[0]).values
    t0_var = block_.iloc[0].values
    block_.iloc[1:-1] = dT[:,_np.newaxis] * lin_coeff + t0_var
    return block_.iloc[1:-1]

def _interp_short_gaps(dataset_avg):
    #expects averaged 30 min sampling ENV dataset as input
    dataset_avg = dataset_avg.copy()
    dataset_breaks = dataset_avg[(~_np.isnan(dataset_avg)).min(axis=1)].copy()
    
    
    dataset_breaks['break_begin'] = _np.roll(dataset_breaks.index,1)
    dataset_breaks['break_end'] = dataset_breaks.index
    dataset_breaks['break_length'] = (((dataset_breaks['break_end'] - dataset_breaks['break_begin']))-1800)/3600 #how many hours is in the break
    short_breaks = dataset_breaks[(dataset_breaks['break_length'] <=12) & (dataset_breaks['break_length'] > 0)] #these are short breaks
    
    tmp=[]
    for i in range(short_breaks.shape[0]):
        begin = short_breaks.iloc[i].break_begin
        end = short_breaks.iloc[i].break_end
        
        block_ = dataset_avg.loc[begin : end]
        tmp.append(_fill_block(block_.copy()))
        
    update = _pd.concat(tmp)
    dataset_avg.loc[update.index] = update
    return dataset_avg

def env2eterna(dataset,remove_outliers,v_type = 'value'):
    '''Expects env dataset. Removes outliers via detrend
    remove_outliers is bool (detrend and filter on 3*std)'''
    if remove_outliers: filt1 = _remove_outliers(dataset,v_type=v_type) #Turning off and on the detrending
    else: filt1 = dataset[v_type]

    filt1_st = _stretch(filt1)
    filt1_avg = _avg_30(filt1_st)
    return _interp_short_gaps(filt1_avg)

ini_extra = '''
STATGRAVIT=      0.        #PRETERNA stations gravity in m/s**2
STATAZIMUT=      0.        #PRETERNA stations azimuth in degree from north
TIDALCOMPO=      2         #PRETERNA tidal component, see manual

TIDALPOTEN=      4        #CHOICE OF POTENTIAL DEVELOPMENT 4=TAMURA
                          #                                7=HW95
INITIALEPO= 2003  1  1
PREDICSPAN= 35063
#AMTRUNCATE=      1.D-10   #truncation threshold for tidal waves(Complete)
PRINTDEVEL=      0        #ETERNA print param. for tidal development (1=yes)
#SEARDATLIM=     -1.       #ETERNA search for data error threshold
#NUMHIGPASS=      1        #ANALYZE highpass filtering = 1

#NUMFILNAME=n30m30m2.nlf   #ANALYZE low pass filter for hourly data
PRINTOBSER=      0        #ETERNA print parameter for observations (1=yes)
PRINTLFOBS=      0        #ETERNA print parameter fo lowpass filtered obs.
RIGIDEARTH=      1        #ETERNA parameter for rigid earth model (1=yes)
HANNWINDOW=      0        #ETERNA parameter for Hann-window (1=yes)
QUICKLOOKA=      0        #ETERNA parameter for quick look analysis (1=yes)

WAVEGROUPI=   .001379   .004107  1.000000   .000000 SA    #ETERNA wavegroup
WAVEGROUPI=   .004108   .020884  1.000000   .000000 SSA   #ETERNA wavegroup
WAVEGROUPI=   .020885   .054747  1.000000   .000000 MM    #ETERNA wavegroup
WAVEGROUPI=   .054748   .091348  1.000000   .000000 MF    #ETERNA wavegroup
WAVEGROUPI=   .501370   .911390  1.000000   .000000 Q1    #ETERNA wavegroup
WAVEGROUPI=   .911391   .947991  1.000000   .000000 O1    #ETERNA wavegroup
WAVEGROUPI=   .981855   .998631  1.000000   .000000 P1    #ETERNA wavegroup
WAVEGROUPI=   .998632  1.001369  1.000000   .000000 S1    #ETERNA wavegroup
WAVEGROUPI=  1.001370  1.004107  1.000000   .000000 K1    #ETERNA wavegroup
WAVEGROUPI=  1.023623  1.057485  1.000000   .000000 J1    #ETERNA wavegroup
WAVEGROUPI=  1.057486  1.470243  1.000000   .000000 OO1   #ETERNA wavegroup
WAVEGROUPI=  1.719370  1.719390  1.000000   .000000 14h   #ANALYZE wave group
WAVEGROUPI=  1.880265  1.914128  1.000000   .000000 N2    #ETERNA wavegroup
WAVEGROUPI=  1.914129  1.950419  1.000000   .000000 M2    #ETERNA wavegroup
WAVEGROUPI=  1.950420  1.984282  1.000000   .000000 L2    #ETERNA wavegroup
WAVEGROUPI=  1.984283  2.002736  1.000000   .000000 S2    #ETERNA wavegroup
WAVEGROUPI=  2.002737  2.451943  1.000000   .000000 K2    #ETERNA wavegroup
WAVEGROUPI=  3.791963  3.937898  1.000000   .000000 M4    #ETERNA wavegroup

#METEOPARAM=         0      3.20airpress. hPa             #ANALYZE meteorol.
#STORENEQSY=         1

# End of file template.ini'''

def get_staDb_llh(staDb_path):
    '''Returns dataframe with staDb stations and llh that can be used for eterna ini file or nloadf'''
    max_t = 3.0e8
    staDb = StationDataBase.StationDataBase(dataBase = staDb_path)  # creating staDb object

    
    # staDb.read(staDb_path)# reading staDb into staDb object
    stns = staDb.getStationList()  # creating array with available station names
    llh_stdb = _np.asarray(staDb.dumpLatLonHeights(epoch=max_t,
                                                 stationList=stns))
    return _pd.DataFrame(llh_stdb.T,index=stns,columns=['LAT','LON','ELEV'])


def run_eterna(input_vars):
    eterna_exec,comp_path = input_vars
    process = _Popen([eterna_exec],cwd=comp_path,stdout=_PIPE)
    process.communicate()
    # out, err = process.communicate()
    # print(err.decode())
    # print(out.decode())
    
def analyse_et(env_et,begin_date, end_date,eterna_path,station_name,project_name,tmp_dir,staDb_path,remove_outliers,force,mode,otl_env=False,parameter_name=None):
    '''Ignores options needed for PREDICT for now (INITIALEPO and PREDICSPAN)
    otl_env switch means creating tmp_otl_et directory and not standard tmp_et'''
    eterna_exec = _os.path.join(eterna_path,'bin/analyse')
    commdat_path = _os.path.join(eterna_path,'commdat')

    dir_name = '{}_{}_{}'.format('tmp_otl_et' if otl_env else 'tmp_et',date2yyyydoy(begin_date),date2yyyydoy(end_date))
    tmp_station_path = _os.path.join(tmp_dir,'gd2e',project_name,station_name,dir_name) #add begin_end names here
    
    if env_et.shape[-1] == 3:
        components = ['e_eterna','n_eterna','v_eterna']
        parameter_name = ['east','north','up']
    elif env_et.shape[-1] == 1:#need to add wetz_eterna component if component is 1
        components = ['aux_eter'] #used to be wetz_ete. renamed to aux_eter. All single column dataseries are treated as aux analysis timeseries
        
    
    components_exist = []
    for component in components:

        if force: #force removes eterna tmp folders
            print('Using "force" option', end=' | ')
            if _os.path.exists(_os.path.join(tmp_station_path,component)):_shutil.rmtree(_os.path.join(tmp_station_path,component))

        prn_exists = _os.path.exists(_os.path.join(tmp_station_path,component,component+'.prn'))
        components_exist.append(prn_exists)
    eterna_exists = _np.min(components_exist) #if at least one is missing -> False

    llh = (get_staDb_llh(staDb_path).loc[station_name]).round(4)



    if not eterna_exists:
        print(('Processing {} {} with Eterna {}-{} | {}').format(station_name,mode,begin_date,end_date,dir_name),end=' | ')

        if not _os.path.exists(tmp_station_path): _os.makedirs(tmp_station_path) 
        for i in range(env_et.shape[-1]):
            comp_path = _os.path.join(tmp_station_path,components[i])
            if not _os.path.exists(comp_path): _os.makedirs(comp_path)
            #create a symlink to commdat folder as needed for eterna
            _os.symlink(commdat_path,_os.path.join(comp_path,'commdat'))   
            #Writing Eterna dat file for specific component and station
            # return env_et.iloc[:,[i,]]
            _write_ETERNA(dataset=env_et.iloc[:,[i,]],filename=_os.path.join(comp_path,components[i]+'.dat'),sampling=1800, station_name=station_name)

            #Writing ini file for specific component and station
            ini_path = _os.path.join(comp_path,components[i]+'.ini')
            
            with open(ini_path,'w') as ini_file:
                ini_file.write('''SENSORNAME= {}\nSAMPLERATE= {}\nSTATLATITU= {}\nSTATLONITU= {}\nSTATELEVAT= {}\nTEXTHEADER= {} {} {} {} '''
                            .format(station_name,'1800',llh['LAT'],llh['LON'],llh['ELEV'],station_name,'GNSS station',llh['LAT'],llh['LON'] ))
                ini_file.write(ini_extra)

            #Touch empty default.ini file
            def_ini_path = _os.path.join(comp_path,'default.ini')
            with open(def_ini_path,'w'):
                _os.utime(def_ini_path, None)

            #Writing project file
            project_path = _os.path.join(comp_path,'project')
            with open(project_path,'w') as project_file:
                project_file.write(components[i])

            # Executing ETERNA. For each component in sequence (expects list of arguments)
            run_eterna([eterna_exec,comp_path])

    if eterna_exists:
        print('Found previous Eterna session for', station_name + '. Extracting processed as not forced.', end=' | ')
        
    return extract_et(tmp_station_path,llh['LON'],llh['LAT'],et_components = components,components=parameter_name)

def read_prn(prn_file):
    with open(prn_file,'r') as file:
        data = file.read()
    data_lines = data.split('\n')
    begin_line = [i for i in range(len(data_lines)) if "adjusted tidal parameters :" in data_lines[i]][0]+6
    data_lines_part = data_lines[begin_line:]
    end_line = [i for i in range(len(data_lines_part)) if "M4" in data_lines_part[i]][0] #CORRECT!!!

    footer = len(data_lines) - (begin_line+end_line+1)
    df = _pd.read_fwf(prn_file,sep='\n',na_values='*********',colspecs=[(0,14),(15,23),(23,28),(28,37),(38,47),(47,56),(56,65),(65,76)],
                      names = ['from','to','wave','theor_a','a_factor','a_stdv','phase','phase_stdv'],skip_blank_lines=False,skiprows=begin_line,header=None,skipfooter=footer)

    waves_extracted = df.wave.values
    df.set_index(waves_extracted,inplace=True)
    return df

def extract_et(tmp_station_path,lon,lat,et_components = ['e_eterna','n_eterna','v_eterna'],components=['east','north','up'],print_lon_lat = False):
    lon-=360 if lon>180 else 0 #as the operator is -= then else will be -=parameter !!!
    lon+=360 if lon<-180 else 0
    if print_lon_lat: print(lon,lat)
    # if et_components == ['e_eterna','n_eterna','v_eterna']:#should be in alphabetical order. Not sure why
    #     components = ['east','north','up']
    # elif et_components == ['aux_eter']:
    #     components = ['aux']
    '''Function to return blq-like table from 3 component analysis of eterna.'''
    columns_mlevel = _pd.MultiIndex.from_product([components,['amplitude','phase'],['value','std']])
    df_blq = _pd.DataFrame(columns = columns_mlevel,index = ['M2','S2','N2','K2','K1','O1','P1','Q1','MF','MM','SSA','14h'])
    
    for i in range(len(et_components)):
        prn_file = _os.path.join(tmp_station_path,et_components[i],et_components[i]+'.prn')
        df = read_prn(prn_file) 

        df_blq[components[i]]['amplitude']['value'].update(((df.theor_a * df.a_factor)/1000).round(5))
        df_blq[components[i]]['amplitude']['std'].update(((df.theor_a * df.a_stdv)/1000).round(5))

        # 14h constituent will not get any corrections
        coeff = _pd.DataFrame([ ['M2',2],['S2',2],['N2',2],['K2',2],\
                                ['K1',1],['O1',1],['P1',1],['Q1',1],\
                                ['MF',0],['MM',0],['SSA',0],['14h',0]],columns=['','coeff']).set_index('')


        df_blq[components[i]]['phase']['value'].update((df['phase'] * -1) - lon*coeff['coeff'])
        df_blq[components[i]]['phase']['std'].update(df['phase_stdv'])
    
    #The true relation between local phase of the potential and Greenwich phase is given by equation (5),
    #  adding 180? for long-period tides for latitudes above 35.27?, and for long-period tides south of the equator.    
    # if lat > 0:
    df_blq.update(df_blq.loc(axis=1)[['east','north'],['phase',],['value',]]+180)
        
    if lat < 0: # -180 for southern hemisphere
        diurnal_constituents = coeff[coeff['coeff'] == 1].index.values
        df_blq.update(df_blq.loc(axis=1)[:,['phase',],['value',]].loc[diurnal_constituents] -180)
            
    if _np.abs(lat) > 35.27: #this was not tested as UK and NZ datasets are well above 35.27
        df_blq.update(df_blq.loc(axis=1)[:,['phase',],['value',]].loc[['MF','MM','SSA']] -180)
    df_blq[df_blq.loc(axis=1)[:,['phase',],['value',]] < -180] += 360
    df_blq[df_blq.loc(axis=1)[:,['phase',],['value',]] > 180] -= 360
    
    return df_blq[components]
    
def analyze_env_single_thread(values_set):
    # function that executes with single thread. Expects list of parameters to run with mp.
    # Expects env - an element of envs. Analyzes all 3 components one after the other
    env_mode,eterna_path,tmp_dir,staDb_path,project_name,remove_outliers,restore_otl,blq_file,sampling,hardisp_path,force,mode,otl_env,begin_date,end_date,v_type,parameter = values_set
    env = env_mode[mode]
    station_name = env.columns.levels[0][0]
    if parameter is not None:
        Trop = ['GradEast','GradNorth','WetZ'] 
        #.Station.{}.Trop.GradEast, .Station.2406.{}.GradNorth, .Station.{}.Trop.WetZ, .Station.{}.Clk.Bias
        parameter = ['{}.{}'.format('Trop',parameter) if parameter in Trop else 'Clk.Bias' if parameter == 'Clk' else ValueError('Unexpected parameter {}'.format(parameter))]
        env = env.loc(axis=1)[station_name,:,'.Station.{}.{}'.format(station_name.upper(),parameter[0])]

    begin_J2000 = (env.index[0]) if begin_date is None else (begin_date -_J2000origin).astype('timedelta64[s]').astype(int)
    end_J2000 = (env.index[-1]) if end_date is None else (end_date -_J2000origin).astype('timedelta64[s]').astype(int)

    env_station = env[station_name] #one level deeper
    if env_station.index.duplicated().sum()>0:
        print('Found duplicated index in',station_name,env_station.index[env_station.index.duplicated()])

    # print(dataset.index.duplicated().sum())
    env_et = env2eterna(env_station[(env_station.index>=begin_J2000) & (env_station.index<=end_J2000)],
                        remove_outliers, v_type = v_type)

    if otl_env:
        synth_otl = gen_synth_otl(dataset = env_et,station_name = station_name,hardisp_path=hardisp_path,blq_file=blq_file,sampling=sampling)
        blq_array = _pd.concat([analyse_et( env_et = synth_otl,
                                            begin_date = begin_date,end_date = end_date,
                                            eterna_path = eterna_path,station_name=station_name,project_name=project_name,
                                            tmp_dir=tmp_dir,staDb_path=staDb_path,
                                            remove_outliers=remove_outliers,force=force,otl_env=otl_env,mode=mode,parameter_name=parameter)],keys=[station_name])
    elif restore_otl:
        synth_otl = gen_synth_otl(dataset = env_et,station_name = station_name,hardisp_path=hardisp_path,blq_file=blq_file,sampling=sampling)
        restored_et = env_et + synth_otl
        blq_array = _pd.concat([analyse_et( env_et = restored_et,
                                            begin_date = begin_date,end_date = end_date,
                                            eterna_path = eterna_path,station_name=station_name,project_name=project_name,
                                            tmp_dir=tmp_dir,staDb_path=staDb_path,
                                            remove_outliers=remove_outliers,force=force,otl_env=otl_env,mode=mode,parameter_name=parameter)],keys=[station_name])
    else:
        blq_array = _pd.concat([analyse_et( env_et = env_et,
                                            begin_date = begin_date,end_date = end_date,
                                            eterna_path = eterna_path,station_name=station_name,project_name=project_name,
                                            tmp_dir=tmp_dir,staDb_path=staDb_path,
                                            remove_outliers=remove_outliers,force=force,otl_env=otl_env,mode=mode,parameter_name=parameter)],keys=[station_name])
    return blq_array

def analyze_env(envs,stations_list,eterna_path,tmp_dir,staDb_path,project_name,remove_outliers,
                restore_otl,blq_file,sampling,hardisp_path,force,num_cores,mode,otl_env,begin,end,
                v_type='value',parameter=None,return_sets=False):
    sets = []
    for i in range(len(envs)):
        sets.append([envs[i],eterna_path,tmp_dir,staDb_path,project_name,remove_outliers,
                    restore_otl,blq_file,sampling,hardisp_path,force,mode,otl_env,begin,end,v_type,parameter])
    num_cores = len(stations_list) if len(stations_list) < num_cores else num_cores
    if return_sets:
        return sets
    else:
        with Pool(num_cores) as p:
            blq_array = p.map(analyze_env_single_thread, sets)
        return _pd.concat(blq_array,axis=0)