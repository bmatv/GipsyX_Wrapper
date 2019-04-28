import numpy as _np
import pandas as _pd

from gxlib.gx_aux import J2000origin as _J2000origin
from gxlib.gx_filter import _stretch, _avg_30
from gxlib.gx_hardisp import gen_synth_otl

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


def _write_ETERNA(dataset, filename,sampling):
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
    for i in range(len(block_ends)):
        block_end_ind = block_ends[i]
        block_begin = 'CAMB               1.0000    1.0000     0.000         0    BLOCK{}\n77777777            0.000\n'.format(i+1)

        out_buf+=(block_begin +
                   data.iloc[block_begin_ind:block_end_ind].to_string(columns=['Date_et', 'Time_et', 'Data'], formatters={'Date_et': a, 'Time_et': b, 'Data': c},
                                  index=False, header=False) + block_end)
        block_begin_ind = block_end_ind
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

def _remove_outliers(dataset_env,coef=3):
    '''Runs detrending of the data to normalize to zero'''
    detrend = dataset_env.value - _get_trend(dataset_env.value)   
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

def env2eterna(dataset,remove_outliers):
    '''Expects env dataset. Removes outliers via detrend
    remove_outliers is bool (detrend and filter on 3*std)'''

    if remove_outliers: filt1 = _remove_outliers(dataset) #Turning off and on the detrending
    else: filt1 = dataset.value

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
#PRINTLFOBS=      1        #ETERNA print parameter fo lowpass filtered obs.
RIGIDEARTH=      1        #ETERNA parameter for rigid earth model (1=yes)
HANNWINDOW=      0        #ETERNA parameter for Hann-window (1=yes)
QUICKLOOKA=      0        #ETERNA parameter for quick look analysis (1=yes)

WAVEGROUPI=   .000146   .003426  1.000000   .000000 SA    #ETERNA wavegroup
WAVEGROUPI=   .004709   .010952  1.000000   .000000 SSA   #ETERNA wavegroup
WAVEGROUPI=   .025811   .031745  1.000000   .000000 MSM   #ETERNA wavegroup
WAVEGROUPI=   .033406   .044653  1.000000   .000000 MM    #ETERNA wavegroup
WAVEGROUPI=   .060131   .068640  1.000000   .000000 MSF   #ETERNA wavegroup
WAVEGROUPI=   .069845   .080798  1.000000   .000000 MF    #ETERNA wavegroup
WAVEGROUPI=   .096422   .104932  1.000000   .000000 MSTM  #ETERNA wavegroup
WAVEGROUPI=   .106136   .115412  1.000000   .000000 MTM   #ETERNA wavegroup
WAVEGROUPI=   .130192   .143814  1.000000   .000000 MSQM  #ETERNA wavegroup
WAVEGROUPI=   .145166   .249952  1.000000   .000000 MQM   #ETERNA wavegroup
WAVEGROUPI=   .721499   .833113  1.000000   .000000 SGQ1  #ETERNA wavegroup
WAVEGROUPI=   .851181   .859691  1.000000   .000000 2Q1   #ETERNA wavegroup
WAVEGROUPI=   .860895   .870024  1.000000   .000000 SGM1  #ETERNA wavegroup
WAVEGROUPI=   .887326   .896130  1.000000   .000000 Q1    #ETERNA wavegroup
WAVEGROUPI=   .897806   .906316  1.000000   .000000 RO1   #ETERNA wavegroup
WAVEGROUPI=   .921940   .930450  1.000000   .000000 O1    #ETERNA wavegroup
WAVEGROUPI=   .931963   .940488  1.000000   .000000 TAU1  #ETERNA wavegroup
WAVEGROUPI=   .958085   .966757  1.000000   .000000 NO1   #ETERNA wavegroup
WAVEGROUPI=   .968564   .974189  1.000000   .000000 CHI1  #ETERNA wavegroup
WAVEGROUPI=   .989048   .998029  1.000000   .000000 P1    #ETERNA wavegroup
WAVEGROUPI=   .999852  1.000148  1.000000   .000000 S1    #ETERNA wavegroup
WAVEGROUPI=  1.001824  1.013690  1.000000   .000000 K1    #ETERNA wavegroup
WAVEGROUPI=  1.028549  1.034468  1.000000   .000000 TET1  #ETERNA wavegroup
WAVEGROUPI=  1.036291  1.044801  1.000000   .000000 J1    #ETERNA wavegroup
WAVEGROUPI=  1.064840  1.071084  1.000000   .000000 SO1   #ETERNA wavegroup
WAVEGROUPI=  1.072582  1.080945  1.000000   .000000 OO1   #ETERNA wavegroup
WAVEGROUPI=  1.099160  1.216398  1.000000   .000000 NU1   #ETERNA wavegroup
WAVEGROUPI=  1.719380  1.837970  1.000000   .000000 EPS2  #ETERNA wavegroup
WAVEGROUPI=  1.853919  1.862429  1.000000   .000000 2N2   #ETERNA wavegroup
WAVEGROUPI=  1.863633  1.872143  1.000000   .000000 MU2   #ETERNA wavegroup
WAVEGROUPI=  1.888386  1.896749  1.000000   .000000 N2    #ETERNA wavegroup
WAVEGROUPI=  1.897953  1.906463  1.000000   .000000 NU2   #ETERNA wavegroup
WAVEGROUPI=  1.923765  1.942754  1.000000   .000000 M2    #ETERNA wavegroup
WAVEGROUPI=  1.958232  1.963709  1.000000   .000000 LAM2  #ETERNA wavegroup
WAVEGROUPI=  1.965826  1.976927  1.000000   .000000 L2    #ETERNA wavegroup
WAVEGROUPI=  1.991786  1.998288  1.000000   .000000 T2    #ETERNA wavegroup
WAVEGROUPI=  1.999705  2.000767  1.000000   .000000 S2    #ETERNA wavegroup
WAVEGROUPI=  2.002590  2.013690  1.000000   .000000 K2    #ETERNA wavegroup
WAVEGROUPI=  2.031287  2.047391  1.000000   .000000 ETA2  #ETERNA wavegroup
WAVEGROUPI=  2.067578  2.182844  1.000000   .000000 2K2   #ETERNA wavegroup
WAVEGROUPI=  2.753243  3.081255  1.000000   .000000 M3    #ETERNA wavegroup
WAVEGROUPI=  3.791963  3.937898  1.000000   .000000 M4    #ETERNA wavegroup


#METEOPARAM=         0      3.20airpress. hPa             #ANALYZE meteorol.
#STORENEQSY=         1

# End of file template.ini'''

def get_staDb_llh(staDb_path):
    '''Returns dataframe with staDb stations and llh that can be used for eterna ini file or nloadf'''
    max_t = 3.0e8
    staDb = StationDataBase.StationDataBase()  # creating staDb object

    
    staDb.read(staDb_path)# reading staDb into staDb object
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
    
def analyse_et(env_et,eterna_path,station_name,project_name,tmp_dir,staDb_path,remove_outliers,force,otl_env=False):
    '''Ignores options needed for PREDICT for now (INITIALEPO and PREDICSPAN)
    otl_env switch means creating tmp_otl_et directory and not standard tmp_et'''
    eterna_exec = _os.path.join(eterna_path,'bin/analyse')
    commdat_path = _os.path.join(eterna_path,'commdat')
    comp_path_list = []

    tmp_station_path = _os.path.join(tmp_dir,'gd2e',project_name,station_name,'tmp_otl_et' if otl_env else 'tmp_et')
    
    components = ['e_eterna','n_eterna','v_eterna']

    if force: #force removes eterna tmp folders
        print('Using "force" option', end=' | ')
        if _os.path.exists(tmp_station_path):
            _shutil.rmtree(tmp_station_path)

    components_exist = []
    for component in components:
        prn_exists = _os.path.exists(_os.path.join(tmp_station_path,component,component+'.prn'))
        components_exist.append(prn_exists)
    eterna_exists = _np.min(components_exist) #if at least one is missing -> False

    llh = (get_staDb_llh(staDb_path).loc[station_name]).round(4)



    if not eterna_exists:
        print('Processing', station_name,'with Eterna...',end=' | ')

        _os.makedirs(tmp_station_path)
        for i in range(len(components)):
            comp_path = _os.path.join(tmp_station_path,components[i])
            _os.makedirs(comp_path)
            #create a symlink to commdat folder as needed for eterna
            _os.symlink(commdat_path,_os.path.join(comp_path,'commdat'))   
            #Writing Eterna dat file for specific component and station
            _write_ETERNA(dataset=env_et.iloc[:,[i,]],filename=_os.path.join(comp_path,components[i]+'.dat'),sampling=1800)

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

            # Executing ETERNA
            # run_eterna(eterna_exec,comp_path)
            comp_path_list.append([eterna_exec,comp_path])

        # Running Eterna analysis of 3 components in parallel
        with Pool(3) as p:
            p.map(run_eterna, comp_path_list)

    if eterna_exists and not force:
        print('Found previous Eterna session for', station_name + '. Extracting processed as not forced.', end=' | ')
        
    return extract_et(tmp_station_path,llh['LON'])

def extract_et(tmp_station_path,lon): #In development. Should extract lon from staDb to do proper correction of the phase
    lon-=360 if lon>180 else 0 #as the operator is -= then else will be -=parameter !!!
    lon+=360 if lon<-180 else 0
    print(lon)
    components = ['east','north','up'] #should be in alphabetical order. Not sure why
    '''Function to return blq-like table from 3 component analysis of eterna.'''
    columns_mlevel = _pd.MultiIndex.from_product([components,['amplitude','phase'],['value','std']])
    df_blq = _pd.DataFrame(columns = columns_mlevel,index = ['M2','S2','N2','K2','K1','O1','P1','Q1','MF','MM','SSA'])
    
    et_components = ['e_eterna','n_eterna','v_eterna']

    for i in range(3):
        prn_file = _os.path.join(tmp_station_path,et_components[i],et_components[i]+'.prn')
        with open(prn_file,'r') as file:
            data = file.read()

        data_lines = data.split('\n')
        begin_line = [i for i in range(len(data_lines)) if "adjusted tidal parameters :" in data_lines[i]][0]+6

        data_lines_part = data_lines[begin_line:]
        end_line = [i for i in range(len(data_lines_part)) if "M4" in data_lines_part[i]][0] #CORRECT!!!

        footer = len(data_lines) - (begin_line+end_line)
        df = _pd.read_fwf(prn_file,sep='\n',skip_blank_lines=False,skiprows=begin_line,header=None,skipfooter=footer,widths=(14,9,5,9,10,9,9,9),names = ['from','to','wave','theor_a','a_factor','a_stdv','phase','phase_stdv'])
        waves_extracted = df.wave.values
        df.set_index(waves_extracted,inplace=True)

        df_blq[components[i]]['amplitude']['value'].update(((df.theor_a * df.a_factor)/1000).round(5))
        df_blq[components[i]]['amplitude']['std'].update(((df.theor_a * df.a_stdv)/1000).round(5))

        coeff = _pd.DataFrame([['Q1',1],['O1',1],['M1',1],['P1',1],['S1',1],['K1',1],['PSI1',1],['PHI1',1],['J1',1],['OO1',1],['14h',1],\
                               ['MF',0],['MM',0],['SSA',0],\
                   ['2N2',2],['N2',2],['M2',2],['L2',2],['S2',2],['K2',2],['M3',3],['M4',2]],columns=['','coeff']).set_index('')


        df_blq[components[i]]['phase']['value'].update((df['phase'] * -1) - lon*coeff['coeff'])
        df_blq[components[i]]['phase']['std'].update(df['phase_stdv'])
        
    df_blq.update(df_blq.loc(axis=1)[['east','north'],['phase',],['value',]]+180)
        
        

    df_blq.update(df_blq.loc(axis=1)[:,['phase',],['value',]].loc[['MF','MM','SSA']] -180)
    df_blq[df_blq.loc(axis=1)[:,['phase',],['value',]] < -180] += 360
    df_blq[df_blq.loc(axis=1)[:,['phase',],['value',]] > 180] -= 360
    
    return df_blq[['up','east','north']]

def analyze_env(envs,stations_list,eterna_path,tmp_dir,staDb_path,project_name,remove_outliers,restore_otl,blq_file,sampling,hardisp_path,force):
    blq_array = _np.ndarray((len(stations_list)),dtype=object)

    if not restore_otl:
        for i in range(blq_array.shape[0]):
            # runing eterna analyse on each env
            env_et = env2eterna(envs[i],remove_outliers)
            blq_array[i] = analyse_et(env_et,eterna_path,stations_list[i],project_name,tmp_dir,staDb_path,remove_outliers)
    else:
        for i in range(blq_array.shape[0]):
            # If restore otl -> ge synthetic otl and add back to the env signal and run analyse on each component
            env_et = env2eterna(envs[i],remove_outliers)
            synth_otl = gen_synth_otl(dataset = env_et,station_name = stations_list[i],hardisp_path=hardisp_path,blq_file=blq_file,sampling=sampling)
            restored_et = env_et + synth_otl
            blq_array[i] = analyse_et(restored_et,eterna_path,stations_list[i],project_name,tmp_dir,staDb_path,remove_outliers,force)

    return blq_array

def test_analyze(envs,stations_list,eterna_path,tmp_dir,staDb_path,project_name,remove_outliers,blq_file,sampling,hardisp_path,force):
    '''This is a test method that should return same parameters as input blq file'''
    blq_array = _np.ndarray((len(stations_list)),dtype=object)
    for i in range(blq_array.shape[0]):
        env_et = env2eterna(envs[i],remove_outliers)
        synth_otl = gen_synth_otl(dataset = env_et,station_name = stations_list[i]+'/tmp_synth_otl',hardisp_path=hardisp_path,blq_file=blq_file,sampling=sampling)

        blq_array[i] = analyse_et(synth_otl,eterna_path,stations_list[i],project_name,tmp_dir,staDb_path,remove_outliers,force)

    return blq_array