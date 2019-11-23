import os as _os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as _np
import pandas as _pd
#PARZEN window function
from scipy import signal

import trees_options
from gd2e_wrap import (gd2e_class, gx_aux, gx_convert, gx_eterna, gx_ionex,
                       gx_merge, gx_tdps, gx_trees)
from gxlib import gx_hardisp
from gxlib.gx_aux import _update_mindex, check_date_margins, date2yyyydoy


class mGNSS_class:
    '''
    1.rnx2dr()
    2.get_drInfo()
    3.drMerge()
    4.gen_tropNom()
    '''
    def __init__(self,
                project_name,
                stations_list,
                years_list,
                tree_options,
                tmp_dir,
                hatanaka,
                cache_path = '/run/user/1017',
                rnx_dir='/array/bogdanm/GNSS_data/BIGF_data/daily30s',
                blq_file = '/array/bogdanm/Products/otl/ocnld_coeff/bigf_complete.blq',
                VMF1_dir = '/array/bogdanm/Products/VMF1_Products',
                tropNom_input = 'trop',
                IGS_logs_dir = '/array/bogdanm/GNSS_data/station_log_files/',
                IONEX_products = '/array/bogdanm/Products/IONEX_Products',
                rate = 300,
                gnss_products_dir = '/array/bogdanm/Products/IGS_GNSS_Products/init/es2_30h_init/',
                ionex_type='igs', #No ionex dir required as ionex merged products will be put into tmp directory by ionex class
                eterna_path='/array/bogdanm/Products/otl/eterna',
                hardisp_path = '/array/bogdanm/Products/otl/hardisp/hardisp',
                num_cores = 8,
                ElMin = 7,
                ElDepWeight = 'SqrtSin',
                pos_s = 0.57, # mm/sqrt(s)
                wetz_s = 0.1, # mm/sqrt(s)
                PPPtype = 'kinematic',
                cddis = False,
                static_clk = False,
                tqdm = True,
                staDb_path = None,
                ambres = False):
        
        self.tqdm=tqdm
        self.ambres = ambres
        self.IGS_logs_dir = IGS_logs_dir
        self.cache_path = _os.path.abspath(cache_path)
        self.rnx_dir=rnx_dir
        self.cddis=cddis
        self.tmp_dir=tmp_dir
        self.stations_list=stations_list
        self.years_list=years_list
        self.num_cores = num_cores
        self.blq_file = blq_file
        self.VMF1_dir = VMF1_dir
        self.hatanaka = hatanaka
        self.tropNom_input = self._check_tropNom_input(tropNom_input) # trop or trop+penna
        self.tropNom_type = self._get_tropNom_type(self.tropNom_input) # return file type based on input trop value
        self.tree_options = tree_options
        # self.selected_rnx = gx_convert.select_rnx(tmp_dir=self.tmp_dir,rnx_dir=self.rnx_dir,stations_list=self.stations_list,years_list=self.years_list,cddis=self.cddis)
        self.gnss_products_dir = gnss_products_dir
        self.ionex_type=ionex_type
        self.IONEX_products = IONEX_products
        self.ionex = gx_ionex.ionex(ionex_prods_dir=self.IONEX_products, #IONEX dir
                                    ionex_type=self.ionex_type, #type of files
                                    num_cores=self.num_cores,
                                    cache_path = self.cache_path,
                                    tqdm=self.tqdm)
        self.ElMin=int(ElMin)
        self.ElDepWeight = ElDepWeight
        self.rate=rate
        self.eterna_path=eterna_path
        self.hardisp_path = hardisp_path
        self.PPPtype = self._check_PPPtype(PPPtype)     
        
          
        self.pos_s = pos_s if self.PPPtype=='kinematic' else 'N/A' # no pos_s for static
        self.wetz_s = wetz_s if self.PPPtype=='kinematic' else 0.05 # penna's value for static

        self.project_name = gx_aux._project_name_construct( project_name, self.PPPtype,
                                                            self.pos_s, self.wetz_s,
                                                            self.tropNom_input, self.ElMin, ambres = self.ambres) #static projects are marked as project_name_[mode]_static
        self.static_clk = static_clk
        
        
        self.staDb_path = gx_aux.gen_staDb(self.tmp_dir,self.project_name,self.stations_list,self.IGS_logs_dir) if staDb_path is None else staDb_path #single staDb path for all modes.
        #Need to be able to fetch external StaDb for pbs

        self.gps = self.init_gd2e(mode = 'GPS')
        self.glo = self.init_gd2e(mode = 'GLONASS')
        self.gps_glo = self.init_gd2e(mode = 'GPS+GLONASS')
        


    def _check_PPPtype(self,PPPtype):
        PPPtypes = ['static', 'kinematic']
        if PPPtype not in PPPtypes:  raise ValueError("Invalid PPPtype. Expected one of: %s" % PPPtypes)
        else: return PPPtype

    def _check_tropNom_input(self,tropNom_input):
        tropNom_inputs = ['trop', 'trop+penna']
        if tropNom_input not in tropNom_inputs:  raise ValueError("Invalid tropNom input. Expected one of: %s" % tropNom_inputs)
        return tropNom_input

    def _get_tropNom_type(self,tropNom_input):
        '''Might be worthy to check if all files exist and station needed exists in tropNom'''
        if tropNom_input == 'trop': tropNom_type = '30h_tropNominalOut_VMF1.tdp'
        if tropNom_input == 'trop+penna': tropNom_type = '30h_tropNominalOut_VMF1.tdp_penna'
        return tropNom_type



        
    def init_gd2e(self, mode):
        '''Initialize gd2e instance wth above parameters but unique mode and updates the poroject_name regarding the mode selected'''
        return gd2e_class(project_name = self.project_name,
                stations_list = self.stations_list,
                years_list = self.years_list,
                tree_options = self.tree_options,
                mode = mode,
                hatanaka = self.hatanaka,
                cache_path=self.cache_path,
                rnx_dir=self.rnx_dir,
                cddis=self.cddis,
                tmp_dir=self.tmp_dir,
                blq_file = self.blq_file,
                VMF1_dir = self.VMF1_dir,
                tropNom_type = self.tropNom_type,
                IGS_logs_dir = self.IGS_logs_dir,
                IONEX_products = self.IONEX_products,
                rate = self.rate,
                gnss_products_dir = self.gnss_products_dir,
                ionex_type=self.ionex_type, #No ionex dir required as ionex merged products will be put into tmp directory by ionex class
                eterna_path=self.eterna_path,
                hardisp_path = self.hardisp_path,
                num_cores = self.num_cores,
                ElMin = self.ElMin,
                ElDepWeight = self.ElDepWeight,
                pos_s = self.pos_s,
                wetz_s = self.wetz_s,
                PPPtype = self.PPPtype,
                static_clk = self.static_clk,
                tqdm=self.tqdm,
                ambres = self.ambres,
                staDb_path = self.staDb_path,
                trees_df = self.gen_trees()
                )
    
    def gen_trees(self):
        '''Creating single universal tree with GPS+GLONASS mode. Constellation switched in gd2e.py calls'''
        return gx_trees.gen_trees(  ionex_type=self.ionex_type,
                                    tmp_dir=self.tmp_dir,
                                    tree_options=self.tree_options,
                                    blq_file=self.blq_file, 
                                    mode = 'GPS+GLONASS', #mGNSS tree is GPS+GLONASS by default. Should be universal
                                    ElMin=self.ElMin,
                                    ElDepWeight=self.ElDepWeight,
                                    pos_s = self.pos_s,
                                    wetz_s = self.wetz_s,
                                    PPPtype = self.PPPtype,
                                    VMF1_dir = self.VMF1_dir,
                                    project_name = self.project_name, #the GNSS_class single project name
                                    static_clk = self.static_clk,
                                    ambres = self.ambres,
                                    years_list = self.years_list,
                                    cache_path=self.cache_path)
   
    def select_rnx(self):
        return gx_convert.select_rnx(tmp_dir=self.tmp_dir,rnx_dir=self.rnx_dir,stations_list=self.stations_list,years_list=self.years_list,hatanaka=self.hatanaka,cddis=self.cddis)

    def rnx2dr(self):
        gx_convert.rnx2dr(selected_df = self.select_rnx(), num_cores=self.num_cores,cddis=self.cddis, tqdm=self.tqdm,cache_path=self.cache_path)
        
    def get_drInfo(self):
        gx_aux.get_drInfo(num_cores=self.num_cores,tmp_dir=self.tmp_dir,tqdm=self.tqdm,selected_rnx = self.select_rnx())

    def gather_drInfo(self):
        '''Should be run with single node'''
        gx_aux.gather_drInfo(num_cores=self.num_cores,tmp_dir=self.tmp_dir,tqdm=self.tqdm)
        
    def _merge_table(self,mode):
        merge_table = gx_merge.get_merge_table(tmp_dir=self.tmp_dir, mode=mode,stations_list=self.stations_list)
        return merge_table
    def dr_merge(self):
        '''This is the only stage where merge_table is being executed with mode=None'''
        gx_merge.dr_merge(merge_table=self._merge_table(mode=None),num_cores=self.num_cores,tqdm=self.tqdm)
        
    def gen_tropNom(self):
        '''Uses tropNom.nominalTrops to generate nominal troposphere estimates.
        Generates zenith tropnominals from VMF1 model files.'''
        gx_tdps.gen_tropnom(tmp_dir=self.tmp_dir,VMF1_dir=self.VMF1_dir,num_cores=self.num_cores,rate=self.rate,staDb_path=self.gps.staDb_path)

    def gen_synth_tropNom(self):
        '''First, run gen_tropNom. This script will create files based on original tropNoms'''
        gx_tdps.gen_penna_tdp(tmp_path=self.tmp_dir, staDb_path = self.gps.staDb_path, tqdm=self.tqdm, period=13.9585147, num_cores = self.num_cores, A_East=2, A_North=4, A_Vertical=6)
        
    
    def _get_common_index(self, gps, glo, gps_glo):
        '''returns common index for 3 mGNSS timeseries of the same station'''
        common_index = gps.index & glo.index & gps_glo.index
        return common_index.values

    def _select_common(self, gps, glo, gps_glo):
        common_index = self._get_common_index(gps,glo,gps_glo)
        return gps.loc[common_index],glo.loc[common_index],gps_glo.loc[common_index]
    
   
    def gather_mGNSS(self,force=False):
        '''get envs. For each station do common index, create unique levels and concat'''
        gather_path =  _os.path.join(self.tmp_dir,'gd2e','env_gathers',self.project_name)

        if not _os.path.exists(gather_path):
            _os.makedirs(gather_path)

        gather = []
        #perform a quick check of available files
        for i in range(len(self.stations_list)):
            filename = '{}/{}.zstd'.format(gather_path,self.stations_list[i].lower())
            if force:
                if _os.path.exists(filename): _os.remove(filename)
            if not _os.path.exists(filename):
                gps_envs = self.gps.envs(force=force)
                glo_envs = self.glo.envs(force=force)
                gps_glo_envs = self.gps_glo.envs(force=force)
                break
            else:
                gather.append(gx_aux._dump_read(filename))

        # if at least one station is missing:
        for i in range(len(self.stations_list)):
            filename = '{}/{}.zstd'.format(gather_path,self.stations_list[i].lower())
            if not _os.path.exists(filename):

                #get common index
                tmp_gps,tmp_glo,tmp_gps_glo = self._select_common(gps=gps_envs[i],glo = glo_envs[i], gps_glo = gps_glo_envs[i])

                #update column levels
                tmp_mGNSS = _pd.concat([tmp_gps,tmp_glo,tmp_gps_glo],axis=1)
                gx_aux._dump_write(data = tmp_mGNSS,filename=filename,num_cores=self.num_cores,cname='zstd')
                #had to go station specific files as nz dataset is too big for serialization with pa
                gather.append(tmp_mGNSS) 
        return gather

    def gather_wetz(self):
        wetz_dir =  _os.path.join(self.tmp_dir,'gd2e','wetz_gathers')
        if not _os.path.exists(wetz_dir):
            _os.makedirs(wetz_dir)

        gather_path =  _os.path.join(wetz_dir,self.project_name + '_wetz.zstd')
        '''get envs. For each station do common index, create unique levels and concat'''
        
        if not _os.path.exists(gather_path):
            gps_wetz = self.gps.wetz()
            glo_wetz = self.glo.wetz()
            gps_glo_wetz = self.gps_glo.wetz()

            gather = []
            for i in range(len(self.stations_list)):
                #get common index
                tmp_gps,tmp_glo,tmp_gps_glo = self._select_common(gps=gps_wetz[i],glo = glo_wetz[i], gps_glo = gps_glo_wetz[i])

                #update column levels
                tmp_mGNSS = _pd.concat([tmp_gps,tmp_glo,tmp_gps_glo],keys=['GPS','GLONASS','GPS+GLONASS'],axis=1)
                gather.append(tmp_mGNSS)
            gx_aux._dump_write(data = gather,filename=gather_path,num_cores=24,cname='zstd')
        else:
            # print('Found mGNSS gather file', self.project_name + ".zstd" )
            gather = gx_aux._dump_read(gather_path)
        
        return gather
    
    def gather_residuals_mGNSS(self):
        return self.gps.residuals(),self.glo.residuals(),self.gps_glo.residuals()
    
    def analyze(self,restore_otl = True,remove_outliers=True,sampling=1800,force=False,begin=None,end=None):
        begin_date, end_date = check_date_margins(begin=begin, end=end, years_list=self.years_list)
        eterna_gathers_dir =  _os.path.join(self.tmp_dir,'gd2e','eterna_gathers')
        if not _os.path.exists(eterna_gathers_dir): _os.makedirs(eterna_gathers_dir)

        suffix = '.zstd' if restore_otl else 'nootl.zstd'
        filename = '{}_{}_{}_{}'.format(self.project_name, date2yyyydoy(begin_date), date2yyyydoy(end_date), suffix)
        gather_path = _os.path.join(eterna_gathers_dir, filename)

        if force: #if force - remove gather file!
            if _os.path.exists(gather_path): _os.remove(gather_path)

        if not _os.path.exists(gather_path):
            '''If force == True -> reruns Eterna even if Eterna files exist'''
            gather = self.gather_mGNSS()

            if not restore_otl: #no synth otl analysis is needed
                tmp_gps = self.gps.analyze_env(envs = gather,force=force,mode = 'GPS',restore_otl=restore_otl, begin = begin_date, end = end_date)
                tmp_glo = self.glo.analyze_env(envs = gather,force=force,mode='GLONASS',restore_otl=restore_otl, begin = begin_date, end = end_date)
                tmp_gps_glo = self.gps_glo.analyze_env(envs = gather,force=force,mode='GPS+GLONASS',restore_otl=restore_otl, begin = begin_date, end = end_date)
                tmp_blq_concat = _pd.concat([tmp_gps,tmp_glo,tmp_gps_glo],keys=['GPS','GLONASS','GPS+GLONASS'],axis=1)
            else:
                tmp_synth = self.gps.analyze_env(envs = gather.copy(),force=force,mode = 'GPS',otl_env=True, begin = begin_date, end = end_date)
                tmp_gps = self.gps.analyze_env(envs = gather,force=force,mode = 'GPS',restore_otl=restore_otl, begin = begin_date, end = end_date)
                tmp_glo = self.glo.analyze_env(envs = gather,force=force,mode='GLONASS',restore_otl=restore_otl, begin = begin_date, end = end_date)
                tmp_gps_glo = self.gps_glo.analyze_env(envs = gather,force=force,mode='GPS+GLONASS',restore_otl=restore_otl, begin = begin_date, end = end_date)
                tmp_blq_concat = _pd.concat([tmp_synth,tmp_gps,tmp_glo,tmp_gps_glo],keys=['OTL','GPS','GLONASS','GPS+GLONASS'],axis=1)

            gx_aux._dump_write(data = tmp_blq_concat,filename=gather_path,num_cores=2,cname='zstd') # dumping to disk mGNSS eterna gather
            

        else:
            tmp_blq_concat = gx_aux._dump_read(gather_path)          
        return tmp_blq_concat
    
    def analyze_gps(self,restore_otl = True,remove_outliers=True,sampling=1800,force=False,begin=None,end=None):
        #Useful for canalysis of gps only products (e.g. JPL)
        begin_date, end_date = check_date_margins(begin=begin, end=end, years_list=self.years_list)

        eterna_gathers_dir = _os.path.join(self.tmp_dir, 'gd2e', 'eterna_gathers')
        if not _os.path.exists(eterna_gathers_dir):
            _os.makedirs(eterna_gathers_dir)

        suffix = 'gps.zstd' if restore_otl else 'nootl_gps.zstd'
        filename = '{}_{}_{}_{}'.format(self.project_name, date2yyyydoy(begin_date), date2yyyydoy(end_date), suffix)
        gather_path = _os.path.join(eterna_gathers_dir, filename)

        if force: #if force - remove gather file!
            if _os.path.exists(gather_path): _os.remove(gather_path)

        gather = self.gps.envs(dump=True,)
        if not _os.path.exists(gather_path):
            if restore_otl:
                tmp_synth = self.gps.analyze_env(envs = gather,force=force,mode = 'GPS',otl_env=True, begin = begin_date, end = end_date)
                tmp_gps = self.gps.analyze_env(envs = gather,force=force,mode = 'GPS',restore_otl=restore_otl,begin = begin_date, end = end_date)      
                tmp_blq_concat = _pd.concat([tmp_synth,tmp_gps],keys=['OTL','GPS'],axis=1)             
                gx_aux._dump_write(data = tmp_blq_concat,filename=gather_path,num_cores=2,cname='zstd') # dumping to disk mGNSS eterna gather
            else:
                tmp_gps = self.gps.analyze_env(envs = gather,force=force,mode = 'GPS',restore_otl=restore_otl,begin = begin_date, end = end_date)      
                tmp_blq_concat = _pd.concat([tmp_gps],keys=['GPS'],axis=1)             
                gx_aux._dump_write(data = tmp_blq_concat,filename=gather_path,num_cores=2,cname='zstd') # dumping to disk mGNSS eterna gather
        else:
            tmp_blq_concat = gx_aux._dump_read(gather_path)  

        return tmp_blq_concat

    def spectra(self,restore_otl = True,remove_outliers=True,sampling=1800):
        gather = self.gather_mGNSS()
        tmp=[]
        if not restore_otl:
            for i in range(len(gather)): #looping through stations
                gps_et = gx_eterna.env2eterna(gather[i]['GPS'],remove_outliers)
                glo_et = gx_eterna.env2eterna(gather[i]['GLONASS'],remove_outliers)
                gps_glo_et = gx_eterna.env2eterna(gather[i]['GPS+GLONASS'],remove_outliers)
                
                tmp_gps = get_spectra(gps_et)
                tmp_glo = get_spectra(glo_et)                    
                tmp_gps_glo = get_spectra(gps_glo_et)

                tmp_mGNSS = _pd.concat([_update_mindex(tmp_gps,'GPS'),_update_mindex(tmp_glo,'GLONASS'),_update_mindex(tmp_gps_glo,'GPS+GLONASS')],axis=1)
                tmp.append(tmp_mGNSS)
                
        else:
            
            for i in range(len(gather)): #looping through stations
                gps_et = gx_eterna.env2eterna(gather[i]['GPS'],remove_outliers)
                glo_et = gx_eterna.env2eterna(gather[i]['GLONASS'],remove_outliers)
                gps_glo_et = gx_eterna.env2eterna(gather[i]['GPS+GLONASS'],remove_outliers)
                #timeframe is the same so we can take any of three. gps_et in this case
                synth_otl = gx_hardisp.gen_synth_otl(dataset = gps_et,station_name = self.stations_list[i],hardisp_path=self.hardisp_path,blq_file=self.blq_file,sampling=sampling)
                
                gps_et+=synth_otl
                glo_et+=synth_otl
                gps_glo_et+=synth_otl
                

                tmp_gps = get_spectra(gps_et)
                tmp_glo = get_spectra(glo_et)                    
                tmp_gps_glo = get_spectra(gps_glo_et)

                tmp_mGNSS = _pd.concat([_update_mindex(tmp_gps,'GPS'),_update_mindex(tmp_glo,'GLONASS'),_update_mindex(tmp_gps_glo,'GPS+GLONASS')],axis=1)
                tmp.append(tmp_mGNSS)
                
        return tmp
    
    
    def gd2e(self):
        for project in [self.gps,self.glo,self.gps_glo]:
            project.gd2e()
#mode should be different automatically





def gen_parzen(samples,fraction):
    window = _np.ones(samples)
    samples_fraction = round(samples*fraction)

    parzen_window =  signal.parzen(samples_fraction,)

    parzen_window_left = parzen_window[:round(parzen_window.shape[0]/2)]
    parzen_window_right = parzen_window[round(parzen_window.shape[0]/2):]

    window[:parzen_window_left.shape[0]] = parzen_window_left
    window[-parzen_window_right.shape[0]:] = parzen_window_right
#     return parzen_window_left.shape,parzen_window_right.shape
    return window

def get_spectra(data,window_size = 14016):
    data.fillna(0,inplace=True)
    constellation_spectra = []
    for component in data:
        comp_spectrum = _np.asarray(signal.welch(data[component].values,fs=48,return_onesided=True,window=gen_parzen(window_size,0.1)))
        tmp_df = _pd.DataFrame(data = comp_spectrum[1],index = comp_spectrum[0], columns = [component])
        constellation_spectra.append(tmp_df)
    constellation_spectra_df = _pd.concat(constellation_spectra,axis=1)
    return constellation_spectra_df




def plot_tree(blq_df,station_name,normalize=True):
    
    #     otl_c = blq_df.index.values
    otl_c = ['M2', 'S2', 'N2', 'K2', 'K1', 'O1', 'P1','Q1']
    
    blq_df = blq_df.loc[otl_c].copy().astype(float) #SSA PMTH phase std: could not convert string to float: '*********'
    coeff95 = 1.96
    
    amplitude = blq_df.xs(key = ('amplitude','value'),axis=1,level = (2,3),drop_level=True)*1000
    phase = blq_df.xs(key = ('phase','value'),axis=1,level = (2,3),drop_level=True) 
    
    std_a = blq_df.xs(key = ('amplitude','std'),axis=1,level = (2,3),drop_level=True)*1000
    std_p = blq_df.xs(key = ('phase','std'),axis=1,level = (2,3),drop_level=True)

    x = _np.sin(_np.deg2rad(phase)) * amplitude
    y = _np.cos(_np.deg2rad(phase)) * amplitude
    
    if normalize:
        x_norm = x['OTL']
        x['OTL'] -= x_norm
        x['GPS'] -= x_norm
        x['GLONASS'] -= x_norm
        x['GPS+GLONASS'] -= x_norm
        
        y_norm = y['OTL']
        y['OTL'] -= y_norm
        y['GPS'] -= y_norm
        y['GLONASS'] -= y_norm
        y['GPS+GLONASS'] -= y_norm
        
    
    #Get scale:
    x_scale = x.abs().max().max()
    y_scale = y.abs().max().max()
    scale = _np.round(_np.max([x_scale,y_scale]))

    
    semiAxisA = std_a
    semiAxisP = _np.tan(_np.deg2rad(std_p))*amplitude
    
    table = _pd.concat([x.unstack(),y.unstack(),(semiAxisA*2*coeff95).unstack(),(semiAxisP*2*coeff95).unstack(),phase.unstack()],axis=1)
    table.columns=['x','y','width','height','angle']


    fig,ax=plt.subplots(ncols = 4,nrows=2,figsize=(15,10))
    coord_c = ['up','east','north']
    color = ['c','b','y']
    
    for j in range(len(otl_c)):

        for i in range(len(coord_c)):


            otl_xy = table.loc(axis=0)[:,coord_c[i],otl_c[j]].loc['OTL']
           
            gps_xy = table.loc(axis=0)[:,coord_c[i],otl_c[j]].loc['GPS']
            glo_xy = table.loc(axis=0)[:,coord_c[i],otl_c[j]].loc['GLONASS']
            gps_glo_xy = table.loc(axis=0)[:,coord_c[i],otl_c[j]].loc['GPS+GLONASS']

            otl_xy.plot(ax=ax.flat[j],kind='scatter',x='x',y='y',color=color[i],marker='+') #label='OTL'+' '+ coord_c[i],
            gps_xy.plot(ax=ax.flat[j],kind='scatter',x='x',y='y',c='red',marker='+',label='GPS' if (i ==0)&(j==0) else None)
            glo_xy.plot(ax=ax.flat[j],kind='scatter',x='x',y='y',c='green',marker='+',label='GLONASS'if (i ==0)&(j==0) else None)
            gps_glo_xy.plot(ax=ax.flat[j],kind='scatter',x='x',y='y',c='k',marker='+',label='GPS+GLONASS'if (i ==0)&(j==0) else None)

            ax.flat[j].plot(_pd.concat([otl_xy,gps_xy])['x'].values,_pd.concat([otl_xy,gps_xy])['y'].values,c=color[i],zorder=0)
            ax.flat[j].plot(_pd.concat([otl_xy,glo_xy])['x'].values,_pd.concat([otl_xy,glo_xy])['y'].values,c=color[i],zorder=0)
            ax.flat[j].plot(_pd.concat([otl_xy,gps_glo_xy])['x'].values,_pd.concat([otl_xy,gps_glo_xy])['y'].values,c=color[i],zorder=0,label=coord_c[i] if j==0 else None)
            ax.flat[j].autoscale(tight=True)

            ax.flat[j].add_patch(mpatches.Ellipse(xy=(gps_xy[['x','y']].values[0]), width=gps_xy['width'], height=gps_xy['height'],angle=gps_xy['angle'],fc='None',edgecolor='r')) #X4 for 95% confidence
            ax.flat[j].add_patch(mpatches.Ellipse(xy=(glo_xy[['x','y']].values[0]), width=glo_xy['width'], height=glo_xy['height'],angle=glo_xy['angle'],fc='None',edgecolor='g')) #X4 for 95% confidence
            ax.flat[j].add_patch(mpatches.Ellipse(xy=(gps_glo_xy[['x','y']].values[0]), width=gps_glo_xy['width'], height=gps_glo_xy['height'],angle=gps_glo_xy['angle'],fc='None',edgecolor='k')) #X4 for 95% confidence
    
    #     legend(codes=3)
    #     print()
    #     ax.legend(handles, labels,loc=3,frameon=False)    
            ax.flat[j].set_xlim(-scale,scale)
            ax.flat[j].set_aspect('equal','datalim')
            # ax[j].autoscale()
            ax.flat[j].set_title(otl_c[j])
            ax.flat[j].grid()
            ax.flat[j].set(xlabel="", ylabel="")
    # plt.tight_layout()
    ax.flat[0].get_legend().remove()
    fig.legend(loc='lower center',ncol=6)
    fig.suptitle(station_name+' station OTL phasors', fontsize=16)
    # fig.tight_layout(rect=(0,0.05,1,1))
    plt.show()
    # print(scale)

# plt.style.use('ggplot')
plt.style.use('default')
def plot_specta(mGNSSspectra_df):
    components = mGNSSspectra_df.columns.levels[1][::-1]
    n_components = components.shape[0]
    fig, ax = plt.subplots(ncols=n_components)
    ms = 2
    for i in range(n_components):
        mGNSSspectra_df[['GLONASS','GPS','GPS+GLONASS']].iloc[1:].xs(key = components[i],level=1,axis=1,drop_level =True)\
        .plot(ax=ax[i],logx=True,logy=True,sharey=True,sharex=True,figsize=(12,4),alpha=0.5,style='.',ms=ms,legend=[False if i==1 else True]) #style=['red','green','royalblue']
        ax[i].get_legend().remove()
        ax[i].set_title(components[i], position=(0.5, 0.9))
        if i ==0:fig.legend(loc='lower center',markerscale=10/ms,ncol=3,)
    fig.tight_layout(rect=(0,0.05,1,1))
    plt.show()
