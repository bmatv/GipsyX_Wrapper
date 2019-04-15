from gd2e_wrap import gd2e_class, gx_convert, gx_aux, gx_ionex, gx_eterna
from gxlib import gx_hardisp
import trees_options
import pandas as _pd
import os as _os

class mGNSS_class:
    def __init__(self,
                project_name,
                stations_list,
                years_list,
                tree_options,
                rnx_dir='/mnt/Data/bogdanm/GNSS_data/BIGF_data/daily30s',
                tmp_dir='/mnt/Data/bogdanm/tmp_GipsyX',
                blq_file = '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf_complete.blq',
                VMF1_dir = '/mnt/Data/bogdanm/Products/VMF1_Products',
                tropNom_type = '30h_tropNominalOut_VMF1.tdp',
                IGS_logs_dir = '/mnt/Data/bogdanm/GNSS_data/BIGF_data/station_log_files',
                IONEX_products = '/mnt/Data/bogdanm/Products/IONEX_Products',
                rate = 300,
                gnss_products_dir = '/mnt/Data/bogdanm/Products/IGS_GNSS_Products/igs2gipsyx/es2_30h_init/',
                ionex_type='igs', #No ionex dir required as ionex merged products will be put into tmp directory by ionex class
                eterna_path='/home/bogdanm/Desktop/otl/eterna',
                hardisp_path = '/home/bogdanm/Desktop/otl/hardisp/hardisp',
                num_cores = 8,
                cddis = False):
        
        self.project_name = project_name
        self.IGS_logs_dir = IGS_logs_dir
        self.rnx_dir=rnx_dir
        self.cddis=cddis
        self.tmp_dir=tmp_dir
        self.stations_list=stations_list
        self.years_list=years_list
        self.num_cores = num_cores
        self.blq_file = blq_file
        self.VMF1_dir = VMF1_dir
        self.tropNom_type = tropNom_type
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
        self.rate=rate
        self.eterna_path=eterna_path
        self.hardisp_path = hardisp_path
        self.mode_table = _pd.DataFrame(data = [['GPS','_g'],['GLONASS','_r'],['GPS+GLONASS','_gr']],columns = ['mode','label'])
        
        self.gps = self.init_gd2e(mode = 'GPS')
        self.glo = self.init_gd2e(mode = 'GLONASS')
        self.gps_glo = self.init_gd2e(mode = 'GPS+GLONASS')
        
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
                num_cores = self.num_cores)
    
    def rnx2dr(self):
        gx_convert.rnx2dr(rnx_files=self.rnx_files, stations_list=self.stations_list, tmp_dir=self.tmp_dir, num_cores=self.num_cores,cddis=self.cddis)
        
    def get_drInfo(self):
        gx_aux.get_drinfo(num_cores=self.num_cores,rnx_files_in_out=self.rnx_files_in_out,stations_list=self.stations_list,tmp_dir=self.tmp_dir,years_list=self.years_list)
        
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
    
    def _update_mindex(self, dataframe, lvl_name):
        '''Inserts a top level named as lvl_name into dataframe_in'''
        mindex_df = dataframe.columns.to_frame(index=False)
        mindex_df.insert(loc = 0,column = 'add',value = lvl_name)

        dataframe.columns = _pd.MultiIndex.from_arrays(mindex_df.values.T)
        return dataframe
    
    def gather_mGNSS(self):
        gather_path =  _os.path.join(self.tmp_dir,'gd2e',self.project_name + '.zstd')
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
                tmp_mGNSS = _pd.concat([self._update_mindex(tmp_gps,'GPS'),self._update_mindex(tmp_glo,'GLONASS'),self._update_mindex(tmp_gps_glo,'GPS+GLONASS')],axis=1)
                gather.append(tmp_mGNSS)
            gx_aux._dump_write(data = gather,filename=gather_path,num_cores=24,cname='zstd')
        else:
            gather = gx_aux._dump_read(gather_path)
        
        return gather
    
    def analyze(self,restore_otl = True,remove_outliers=True,sampling=1800):
        gather = self.gather_mGNSS()
        tmp_blq=[]
        if not restore_otl:
            for i in range(len(gather)): #looping through stations
                gps_et = gx_eterna.env2eterna(gather[i]['GPS'],remove_outliers)
                glo_et = gx_eterna.env2eterna(gather[i]['GLONASS'],remove_outliers)
                gps_glo_et = gx_eterna.env2eterna(gather[i]['GPS+GLONASS'],remove_outliers)
                
                tmp_gps = gx_eterna.analyse_et(gps_et,self.eterna_path,self.stations_list[i],self.gps.project_name,self.gps.tmp_dir,self.gps.staDb_path,remove_outliers)
                tmp_glo = gx_eterna.analyse_et(glo_et,self.eterna_path,self.stations_list[i],self.glo.project_name,self.glo.tmp_dir,self.glo.staDb_path,remove_outliers)
                tmp_gps_glo = gx_eterna.analyse_et(gps_glo_et,self.eterna_path,self.stations_list[i],self.gps_glo.project_name,self.gps_glo.tmp_dir,self.gps_glo.staDb_path,remove_outliers)
                
                tmp_mGNSS = _pd.concat([self._update_mindex(tmp_gps,'GPS'),self._update_mindex(tmp_glo,'GLONASS'),self._update_mindex(tmp_gps_glo,'GPS+GLONASS')],axis=1)
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
                tmp_synth = gx_eterna.analyse_et(synth_otl,self.eterna_path,self.stations_list[i],self.gps.project_name,self.gps.tmp_dir,self.gps.staDb_path,remove_outliers)
                
                tmp_gps = gx_eterna.analyse_et(gps_et,self.eterna_path,self.stations_list[i],self.gps.project_name,self.gps.tmp_dir,self.gps.staDb_path,remove_outliers)
                tmp_glo = gx_eterna.analyse_et(glo_et,self.eterna_path,self.stations_list[i],self.glo.project_name,self.glo.tmp_dir,self.glo.staDb_path,remove_outliers)
                tmp_gps_glo = gx_eterna.analyse_et(gps_glo_et,self.eterna_path,self.stations_list[i],self.gps_glo.project_name,self.gps_glo.tmp_dir,self.gps_glo.staDb_path,remove_outliers)
                
                tmp_mGNSS = _pd.concat([self._update_mindex(tmp_synth,'OTL'),self._update_mindex(tmp_gps,'GPS'),self._update_mindex(tmp_glo,'GLONASS'),self._update_mindex(tmp_gps_glo,'GPS+GLONASS')],axis=1)
                tmp_blq.append(tmp_mGNSS)
                
        return tmp_blq
    
    def gd2e(self):
        for project in [self.gps,self.glo,self.gps_glo]:
            project.gd2e()
#mode should be different automatically