from gd2e_wrap import gd2e_class, gx_convert, gx_aux, gx_ionex, gx_eterna, gx_merge, gx_tdps
from gxlib import gx_hardisp
import trees_options
import pandas as _pd
import os as _os

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
                rnx_dir='/mnt/Data/bogdanm/GNSS_data/BIGF_data/daily30s',
                tmp_dir='/mnt/Data/bogdanm/tmp_GipsyX/bigf_tmpX/',
                blq_file = '/mnt/Data/bogdanm/Products/otl/ocnld_coeff/bigf_complete.blq',
                VMF1_dir = '/mnt/Data/bogdanm/Products/VMF1_Products',
                tropNom_input = 'trop',
                IGS_logs_dir = '/mnt/Data/bogdanm/GNSS_data/station_log_files/',
                IONEX_products = '/mnt/Data/bogdanm/Products/IONEX_Products',
                rate = 300,
                gnss_products_dir = '/mnt/Data/bogdanm/Products/IGS_GNSS_Products/init/es2_30h_init/',
                ionex_type='igs', #No ionex dir required as ionex merged products will be put into tmp directory by ionex class
                eterna_path='/home/bogdanm/Desktop/otl/eterna',
                hardisp_path = '/home/bogdanm/Desktop/otl/hardisp/hardisp',
                num_cores = 8,
                ElMin = 7,
                pos_s = 0.57, # mm/sqrt(s)
                wetz_s = 0.1, # mm/sqrt(s)
                PPPtype = 'kinematic',
                cddis = False):
        
        
        self.IGS_logs_dir = IGS_logs_dir
        self.rnx_dir=rnx_dir
        self.cddis=cddis
        self.tmp_dir=tmp_dir
        self.stations_list=stations_list
        self.years_list=years_list
        self.num_cores = num_cores
        self.blq_file = blq_file
        self.VMF1_dir = VMF1_dir
        self.tropNom_input = self._check_tropNom_input(tropNom_input) # trop or trop+penna
        self.tropNom_type = self._check_tropNom_type(self.tropNom_input) # return file type based on input trop value
        self.tree_options = tree_options
        self.rnx_files = gx_convert.select_rnx(rnx_dir=self.rnx_dir,stations_list=self.stations_list,years_list=self.years_list,cddis=self.cddis)
        self.rnx_files_in_out = gx_convert.rnx2dr_gen_paths(rnx_files=self.rnx_files,stations_list=self.stations_list,tmp_dir=self.tmp_dir,cddis=self.cddis)
        self.gnss_products_dir = gnss_products_dir
        self.ionex_type=ionex_type
        self.IONEX_products = IONEX_products
        self.ionex = gx_ionex.ionex(ionex_in_files_path=self.IONEX_products, #IONEX dir
                                    ionex_type=self.ionex_type, #type of files
                                    output_path=self.tmp_dir, #output dir that will have type|year files
                                    num_cores=self.num_cores)
        self.ElMin=ElMin
        self.rate=rate
        self.eterna_path=eterna_path
        self.hardisp_path = hardisp_path
        self.mode_table = _pd.DataFrame(data = [['GPS','_g'],['GLONASS','_r'],['GPS+GLONASS','_gr']],columns = ['mode','label'])
        self.PPPtype = self._check_PPPtype(PPPtype)     
        
          
        self.pos_s = pos_s if self.PPPtype=='kinematic' else 'N/A' # no pos_s for static
        self.wetz_s = wetz_s if self.PPPtype=='kinematic' else 0.05 # penna's value for static

        self.project_name = self._project_name_construct(project_name) #static projects are marked as project_name_[mode]_static
        
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

    def get_tropNom_type(self,tropNom_input):
        '''Might be worthy to check if all files exist and station needed exists in tropNom'''
        if tropNom_input == 'trop': tropNom_type = '30h_tropNominalOut_VMF1.tdp'
        if tropNom_input == 'trop+penna': tropNom_type = '30h_tropNominalOut_VMF1.tdp_penna'
        return tropNom_type


    def _project_name_construct(self,project_name,tropNom_type):
        '''pos_s and wetz_s are im mm/sqrt(s)'''
        if self.PPPtype=='kinematic':
            project_name = '{}_{}_{}'.format(str(project_name),str(self.pos_s),str(self.wetz_s))
        if self.PPPtype=='static':
            project_name = '{}_static'.format(str(project_name))
        #adding _synth if tropNom type == trop+penna
        return project_name
        
    def init_gd2e(self, mode):
        '''Initialize gd2e instance wth above parameters but unique mode and updates the poroject_name regarding the mode selected'''
        return gd2e_class(project_name = self.project_name + self.mode2label(mode),
                stations_list = self.stations_list,
                years_list = self.years_list,
                tree_options = self.tree_options,
                mode = mode,
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
                pos_s = self.pos_s,
                wetz_s = self.wetz_s,
                PPPtype = self.PPPtype)
    
    def gen_trees(self):
        self.gps.gen_trees()
        self.glo.gen_trees()
        self.gps_glo.gen_trees()
        
    
    def rnx2dr(self):
        gx_convert.rnx2dr(rnx_files=self.rnx_files, stations_list=self.stations_list, tmp_dir=self.tmp_dir, num_cores=self.num_cores,cddis=self.cddis)
        
    def get_drInfo(self):
        gx_aux.get_drinfo(num_cores=self.num_cores,rnx_files_in_out=self.rnx_files_in_out,stations_list=self.stations_list,tmp_dir=self.tmp_dir,years_list=self.years_list)
        
    def dr_merge(self):
        '''This is the only stage where merge_table is being executed with mode=None'''
        merge_table = gx_merge.get_merge_table(tmp_dir=self.tmp_dir, mode=None)
        gx_merge.dr_merge(merge_table=merge_table,num_cores=self.num_cores,stations_list=self.stations_list)
        
    def gen_tropNom(self):
        '''Uses tropNom.nominalTrops to generate nominal troposphere estimates.
        Generates zenith tropnominals from VMF1 model files.'''
        gx_tdps.gen_tropnom(tmp_dir=self.tmp_dir,VMF1_dir=self.VMF1_dir,num_cores=self.num_cores,rate=self.rate,staDb_path=self.gps.staDb_path)

    def gen_synth_tropNom(self):
        '''First, run gen_tropNom. This script will create files based on original tropNoms'''
        gx_tdps.gen_penna_tdp(tmp_path=self.tmp_dir, staDb_path = self.gps.staDb_path, period=13.9585147, num_cores = self.num_cores, A_East=2, A_North=4, A_Vertical=6)
        
    def mode2label(self,mode):
        '''expects one of the modes (GPS, GLONASS or GPS+GLONASS and returs g,r or gr respectively for naming conventions)'''
        return self.mode_table[self.mode_table['mode']==mode]['label'].values[0]
    
    def _get_common_index(self, gps, glo, gps_glo):
        '''returns common index for 3 mGNSS timeseries of the same station'''
        common_index = gps.index & glo.index & gps_glo.index
        return common_index.values

    def _select_common(self, gps, glo, gps_glo):
        common_index = self._get_common_index(gps,glo,gps_glo)
        return gps.loc[common_index],glo.loc[common_index],gps_glo.loc[common_index]
    
   
    def gather_mGNSS(self):
        env_dir =  _os.path.join(self.tmp_dir,'gd2e','env_gathers')
        if not _os.path.exists(env_dir):
            _os.makedirs(env_dir)

        gather_path =  _os.path.join(env_dir,self.project_name + '.zstd')
        '''get envs. For each station do common index, create unique levels and concat'''
        
        if not _os.path.exists(gather_path):
            gps_envs = self.gps.envs()
            glo_envs = self.glo.envs()
            gps_glo_envs = self.gps_glo.envs()

            gather = []
            for i in range(len(self.stations_list)):
                #get common index
                tmp_gps,tmp_glo,tmp_gps_glo = self._select_common(gps=gps_envs[i],glo = glo_envs[i], gps_glo = gps_glo_envs[i])

                #update column levels
                tmp_mGNSS = _pd.concat([_update_mindex(tmp_gps,'GPS'),_update_mindex(tmp_glo,'GLONASS'),_update_mindex(tmp_gps_glo,'GPS+GLONASS')],axis=1)
                gather.append(tmp_mGNSS)
            gx_aux._dump_write(data = gather,filename=gather_path,num_cores=24,cname='zstd')
        else:
            # print('Found mGNSS gather file', self.project_name + ".zstd" )
            gather = gx_aux._dump_read(gather_path)
        
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
                tmp_mGNSS = _pd.concat([_update_mindex(tmp_gps,'GPS'),_update_mindex(tmp_glo,'GLONASS'),_update_mindex(tmp_gps_glo,'GPS+GLONASS')],axis=1)
                gather.append(tmp_mGNSS)
            gx_aux._dump_write(data = gather,filename=gather_path,num_cores=24,cname='zstd')
        else:
            # print('Found mGNSS gather file', self.project_name + ".zstd" )
            gather = gx_aux._dump_read(gather_path)
        
        return gather
    
    def gather_residuals_mGNSS(self):
        return self.gps.residuals(),self.glo.residuals(),self.gps_glo.residuals()
    
    def analyze(self,restore_otl = True,remove_outliers=True,sampling=1800,force=False):
        eterna_gathers_dir =  _os.path.join(self.tmp_dir,'gd2e','eterna_gathers')
        if not _os.path.exists(eterna_gathers_dir): _os.makedirs(eterna_gathers_dir)

        if restore_otl: gather_path = _os.path.join(eterna_gathers_dir,self.project_name + '_et_otl.zstd') #files with OTL siganl restored
        else: gather_path = _os.path.join(eterna_gathers_dir,self.project_name + '_et_nootl.zstd') #raw files with only residual OTL

        if force: #if force - remove gather file!
            if _os.path.exists(gather_path): _os.remove(gather_path)

        if not _os.path.exists(gather_path):
            '''If force == True -> reruns Eterna even if Eterna files exist'''
            gather = self.gather_mGNSS()
            tmp_blq=[]
            if not restore_otl:
                for i in range(len(gather)): #looping through stations
                    gps_et = gx_eterna.env2eterna(gather[i]['GPS'],remove_outliers)
                    glo_et = gx_eterna.env2eterna(gather[i]['GLONASS'],remove_outliers)
                    gps_glo_et = gx_eterna.env2eterna(gather[i]['GPS+GLONASS'],remove_outliers)
                    
                    tmp_gps = gx_eterna.analyse_et(gps_et,self.eterna_path,self.stations_list[i],self.gps.project_name,self.gps.tmp_dir,self.gps.staDb_path,remove_outliers,force)
                    tmp_glo = gx_eterna.analyse_et(glo_et,self.eterna_path,self.stations_list[i],self.glo.project_name,self.glo.tmp_dir,self.glo.staDb_path,remove_outliers,force)
                    tmp_gps_glo = gx_eterna.analyse_et(gps_glo_et,self.eterna_path,self.stations_list[i],self.gps_glo.project_name,self.gps_glo.tmp_dir,self.gps_glo.staDb_path,remove_outliers,force)
                    
                    tmp_mGNSS = _pd.concat([_update_mindex(tmp_gps,'GPS'),_update_mindex(tmp_glo,'GLONASS'),_update_mindex(tmp_gps_glo,'GPS+GLONASS')],axis=1)
                    tmp_blq.append(tmp_mGNSS)
                    
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
                    
                    #snth analysis to double check. Analysis is done in gps project for now
                    tmp_synth = gx_eterna.analyse_et(synth_otl,self.eterna_path,self.stations_list[i],self.gps.project_name,self.gps.tmp_dir,self.gps.staDb_path,remove_outliers,force,otl_env=True)
                    
                    tmp_gps = gx_eterna.analyse_et(gps_et,self.eterna_path,self.stations_list[i],self.gps.project_name,self.gps.tmp_dir,self.gps.staDb_path,remove_outliers,force)
                    tmp_glo = gx_eterna.analyse_et(glo_et,self.eterna_path,self.stations_list[i],self.glo.project_name,self.glo.tmp_dir,self.glo.staDb_path,remove_outliers,force)
                    tmp_gps_glo = gx_eterna.analyse_et(gps_glo_et,self.eterna_path,self.stations_list[i],self.gps_glo.project_name,self.gps_glo.tmp_dir,self.gps_glo.staDb_path,remove_outliers,force)
                    
                    tmp_mGNSS = _pd.concat([_update_mindex(tmp_synth,'OTL'),_update_mindex(tmp_gps,'GPS'),_update_mindex(tmp_glo,'GLONASS'),_update_mindex(tmp_gps_glo,'GPS+GLONASS')],axis=1)
                    tmp_blq.append(tmp_mGNSS)
            gx_aux._dump_write(data = tmp_blq,filename=gather_path,num_cores=2,cname='zstd') # dumping to disk mGNSS eterna gather

        else:
            tmp_blq = gx_aux._dump_read(gather_path)          
        return tmp_blq
    
    
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



#PARZEN window function
from scipy import signal
import numpy as _np


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

def get_spectra(data):
    data.fillna(0,inplace=True)
    constellation_spectra = []
    for component in data:
        comp_spectrum = _np.asarray(signal.welch(data[component].values,fs=48,return_onesided=True,window=gen_parzen(14016,0.1)))
        tmp_df = _pd.DataFrame(data = comp_spectrum[1],index = comp_spectrum[0], columns = [component])
        constellation_spectra.append(tmp_df)
    constellation_spectra_df = _pd.concat(constellation_spectra,axis=1)
    return constellation_spectra_df


import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


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
#             ax[j].autoscale()
            ax.flat[j].set_title(otl_c[j])
            ax.flat[j].grid()
            ax.flat[j].set(xlabel="", ylabel="")
    # plt.tight_layout()
    ax.flat[0].get_legend().remove()
    fig.legend(loc='lower center',ncol=6)
    fig.suptitle(station_name+' station OTL phasors', fontsize=16)
#     fig.tight_layout(rect=(0,0.05,1,1))
    plt.show()
#     print(scale)

import matplotlib.pyplot as plt
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
    
    
def _update_mindex(dataframe, lvl_name):
    '''Inserts a top level named as lvl_name into dataframe_in'''
    mindex_df = dataframe.columns.to_frame(index=False)
    mindex_df.insert(loc = 0,column = 'add',value = lvl_name)

    dataframe.columns = _pd.MultiIndex.from_arrays(mindex_df.values.T)
    return dataframe