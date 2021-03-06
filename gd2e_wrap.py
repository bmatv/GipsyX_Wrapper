import os as _os
import numpy as _np
import pandas as _pd
from GipsyX_Wrapper.gxlib import (gx_aux, gx_compute, gx_convert, gx_eterna, gx_extract,
                   gx_filter, gx_ionex, gx_merge, gx_tdps, gx_trees)




class gd2e_class:
    def __init__(self,
                 project_name,
                 stations_list,  #add check for duplicates in stations_list as staDb-based functions may crash
                 years_list,
                 tree_options,
                 mode,
                 hatanaka,
                 cddis=False,
                 cache_path='/run/user/1017',
                 rnx_dir='/mnt/Data/bogdanm/GNSS_data/BIGF_data/daily30s',
                 tmp_dir='/mnt/Data/bogdanm/tmp_GipsyX/bigf_tmpX',
                 blq_file = '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf_glo.blq',
                 VMF1_dir = '/mnt/Data/bogdanm/Products/VMF1_Products',
                 tropNom_type = '30h_tropNominalOut_VMF1.tdp',
                 IGS_logs_dir = '/mnt/Data/bogdanm/GNSS_data/BIGF_data/station_log_files',
                 IONEX_products = '/mnt/Data/bogdanm/Products/IONEX_Products',
                 rate = 300,
                 gnss_products_dir = '/mnt/Data/bogdanm/Products/JPL_GPS_Products_IGb08/Final',
                 ionex_type='igs', #No ionex dir required as ionex merged products will be put into tmp directory by ionex class
                 eterna_path='/home/bogdanm/Desktop/otl/eterna',
                 hardisp_path = '/home/bogdanm/Desktop/otl/hardisp/hardisp',
                 num_cores = 8, # integer of string
                 ElMin=7,       # degrees
                 ElDepWeight='SqrtSin', #ElDepWeighting function
                 pos_s = 0.57,  # mm/sqrt(s)
                 wetz_s = 0.1,   # mm/sqrt(s)
                 PPPtype = 'kinematic',
                 static_clk = False,
                 tqdm = True,
                 ambres = True,
                 staDb_path = None,
                 trees_df = None
                 ):
        self.tqdm = tqdm
        self.hatanaka=hatanaka,
        self.cache_path = _os.path.abspath(cache_path)
        self.PPPtype = self._check_PPPtype(PPPtype)
        self.mode = self._check_mode(mode)
        self.project_name_core = project_name # original project name (core or family name)
        self.project_name = project_name  + gx_aux.mode2label(mode=self.mode) #UPDATING PROJECT NAME DEPENDING ON THE MODE
        self.IGS_logs_dir = _os.path.abspath(IGS_logs_dir)
        self.rnx_dir=_os.path.abspath(rnx_dir)
        self.tmp_dir=_os.path.abspath(tmp_dir)
        self.cddis=cddis
        self.stations_list=stations_list
        self.years_list=years_list
        self.num_cores = num_cores
        self.blq_file = blq_file
        self.VMF1_dir = VMF1_dir
        self.tropNom_type = tropNom_type
        self.tree_options = tree_options
        # self.selected_rnx = gx_convert.select_rnx(tmp_dir=self.tmp_dir,rnx_dir=self.rnx_dir,stations_list=self.stations_list,years_list=self.years_list,cddis=self.cddis)
        self.staDb_path= gx_aux.gen_staDb(self.tmp_dir,self.project_name,self.stations_list,self.IGS_logs_dir) if staDb_path is None else staDb_path
        self.gnss_products_dir = _os.path.abspath(gnss_products_dir)
        self.ionex_type=ionex_type
        self.IONEX_products = _os.path.abspath(IONEX_products)
        self.ionex = gx_ionex.ionex(ionex_prods_dir=self.IONEX_products, #IONEX dir
                                    ionex_type=self.ionex_type, #type of files
                                    num_cores=self.num_cores,
                                    cache_path = self.cache_path,
                                    tqdm=self.tqdm)
        self.rate=rate
        self.refence_xyz_df = gx_aux.get_ref_xyz_sites(staDb_path=self.staDb_path)
        self.eterna_path=eterna_path
        self.hardisp_path = hardisp_path
        self.ElMin=ElMin
        self.ElDepWeight = ElDepWeight
        self.static_clk = static_clk
        self.ambres = ambres
        
        self.pos_s = pos_s if self.PPPtype=='kinematic' else 'N/A' # no pos_s for static
        self.wetz_s = wetz_s if self.PPPtype=='kinematic' else 0.05 # penna's value for static
        self.trees_df = trees_df

    def _check_mode(self,mode):
        modes = ['GPS', 'GLONASS','GPS+GLONASS']
        if mode not in modes:  raise ValueError("Invalid mode. Expected one of: %s" % modes)
        else: return mode

    def _check_PPPtype(self,PPPtype):
        PPPtypes = ['static', 'kinematic']
        if PPPtype not in PPPtypes:  raise ValueError("Invalid PPPtype. Expected one of: %s" % PPPtypes)
        else: return PPPtype
    def select_rnx(self):
        return gx_convert.select_rnx(tmp_dir=self.tmp_dir,rnx_dir=self.rnx_dir,stations_list=self.stations_list,years_list=self.years_list,cddis=self.cddis,hatanaka=self.hatanaka)
    def rnx2dr(self):
        gx_convert.rnx2dr(selected_df = self.select_rnx(), num_cores=self.num_cores,cddis=self.cddis, tqdm=self.tqdm, staDb_path=self.staDb_path, cache_path=self.cache_path)

    def get_drInfo(self):
        gx_aux.get_drInfo(num_cores=self.num_cores,tmp_dir=self.tmp_dir,tqdm=self.tqdm,selected_rnx= self.select_rnx())
    
    def _merge_table(self,mode):
        merge_table = gx_merge.get_merge_table(tmp_dir=self.tmp_dir, mode=mode,stations_list=self.stations_list)
        return merge_table
    def dr_merge(self):
        '''This is the only stage where merge_table is being executed with mode=None'''
        gx_merge.dr_merge(merge_table=self._merge_table(mode=None),num_cores=self.num_cores,tqdm=self.tqdm)
    def gen_tropNom(self):
        '''Uses tropNom.nominalTrops to generate nominal troposphere estimates.
        Generates zenith tropnominals from VMF1 model files.'''
        gx_tdps.gen_tropnom(tmp_dir=self.tmp_dir,VMF1_dir=self.VMF1_dir,num_cores=self.num_cores,rate=self.rate,staDb_path=self.staDb_path)
    def gen_trees(self):
        return gx_trees.gen_trees(  ionex_type=self.ionex_type,
                                    tmp_dir=self.tmp_dir,
                                    tree_options=self.tree_options,
                                    blq_file=self.blq_file, 
                                    mode = self.mode,
                                    ElMin=self.ElMin,
                                    pos_s = self.pos_s,
                                    wetz_s = self.wetz_s,
                                    PPPtype = self.PPPtype,
                                    VMF1_dir = self.VMF1_dir,
                                    project_name = self.project_name,
                                    static_clk = self.static_clk,
                                    ambres = self.ambres,
                                    years_list = self.years_list,
                                    ElDepWeight=self.ElDepWeight,
                                    cache_path = self.cache_path) if self.trees_df is None else self.trees_df

    def _gd2e_table(self):
        return gx_compute._gen_gd2e_table(  trees_df = self.gen_trees(),
                                            merge_table = self._merge_table(mode=self.mode),
                                            tmp_dir = self.tmp_dir,
                                            tropNom_type = self.tropNom_type,
                                            project_name = self.project_name,
                                            gnss_products_dir = self.gnss_products_dir,
                                            staDb_path = self.staDb_path,
                                            years_list = self.years_list,
                                            mode=self.mode,
                                            cache_path = self.cache_path,
                                            IONEX_products_dir=self.IONEX_products,
                                            ionex_type = self.ionex_type,
                                            tqdm=self.tqdm)

    def gd2e(self):
        gx_compute.gd2e(gd2e_table = self._gd2e_table(),
                        project_name = self.project_name,
                        num_cores=self.num_cores,
                        tqdm=self.tqdm,
                        cache_path = self.cache_path)

    def solutions(self,single_station=None):
        return gx_extract.gather_solutions(num_cores=self.num_cores,
                                            project_name=self.project_name,
                                            stations_list=self.stations_list,
                                            tmp_dir=self.tmp_dir,
                                            tqdm=self.tqdm,single_station=single_station)
    def residuals(self,single_station=False):
        return gx_extract.gather_residuals(num_cores=self.num_cores,
                                            project_name=self.project_name,
                                            stations_list=self.stations_list,
                                            tmp_dir=self.tmp_dir,
                                            tqdm=self.tqdm,
                                            single_station=single_station)
    def filtered_solutions(self,sigma_cut=0.1,single_station=None):
        return gx_filter.filter_tdps(sigma_cut=sigma_cut,tdps=self.solutions(single_station=single_station))

    
    def envs(self,sigma_cut=0.05,dump=False,force=False,stations_list=None):
        '''checks is dump files exist. if not -> gathers filtered solutions and sends to _xyz2env (with dump option True or False)
        stations_list var can be used to specified block-like load which is useful for big datasets analysis'''
        dump = False if dump is None else dump
        stations_list = self.stations_list if stations_list is None else stations_list
        env_gather_path = _os.path.join(self.tmp_dir,'gd2e/env_gathers',self.project_name_core) #saning to core where all mGNSS env_gathers are located
        if not _os.path.exists(env_gather_path): _os.makedirs(env_gather_path)
        envs = _np.ndarray((len(stations_list)),dtype=object)
        incomplete=False
        for i in range(envs.shape[0]):
            env_path = _os.path.join(env_gather_path,'{}{}.zstd'.format(stations_list[i].lower(),gx_aux.mode2label(self.mode))) #naming convention as site_gps.zstd 
            if force:
                if _os.path.exists(env_path): _os.remove(env_path)
            if _os.path.exists(env_path):
                envs[i] = gx_aux._dump_read(env_path)
            else: 
                incomplete=True
                break
        if incomplete:
            envs = gx_aux._xyz2env(dataset=self.filtered_solutions(sigma_cut=sigma_cut), #filtered_solutions takes most of the time
                        reference_df=self.refence_xyz_df,mode=self.mode,dump = env_gather_path if dump else None)
        return envs
    def gen_tdps_penna(self,period=13.9585147,A_East=2, A_North=4, A_Vertical=6):
        gx_tdps.gen_penna_tdp(tmp_path=self.tmp_dir,
                              staDb_path = self.staDb_path,
                              period=period,
                              A_East=A_East,
                              A_North=A_North,
                              A_Vertical=A_Vertical,
                              num_cores = self.num_cores,
                              tqdm=self.tqdm)
    def remove_merged(self):
        '''Removes merged dr files, be it 30h file or 32h file'''
        gx_aux.remove_30h(self.tmp_dir)
        gx_aux.remove_32h(self.tmp_dir)
    def remove_gathers(self):
        gx_extract.rm_solutions_gathers(self.tmp_dir,self.project_name)
        gx_extract.rm_residuals_gathers(self.tmp_dir,self.project_name)

    def get_chalmers(self):
        return gx_aux.get_chalmers(self.staDb_path)

    def analyze_env(self,envs=None,mode=None,remove_outliers=True,restore_otl=True,sampling=1800,force=False,otl_env=False,begin=None,end=None,return_sets=False):
        '''should accept stations_list and break it into chunks. Not envs which take long to read and occupy lots of RAM'''
        if begin is None: 
            begin, end = gx_aux.check_date_margins(begin=begin, end=end, years_list=self.years_list)
        mode = self.mode if mode is None else mode

        if envs is None:
            stations_sublists = gx_aux.split10(array=self.stations_list,split_arrays_size=self.num_cores)
            
            # envs = self.envs() if envs is None else envs #can break the envs into blocks of up to ten stations
            buf=[]
            for stations_sublist in stations_sublists:
                print('Chunking the stations_list. Processing',stations_sublist)
                #for each sublist run analyze_env. concat the output afterwards
                envs = self.envs(stations_list = stations_sublist)
                buf.append(
                    gx_eterna.analyze_env(  envs,
                                            self.stations_list,self.eterna_path,self.tmp_dir,self.staDb_path,self.project_name,
                                            remove_outliers,restore_otl=restore_otl,blq_file = self.blq_file,sampling = sampling,hardisp_path = self.hardisp_path,
                                            force=force,num_cores = self.num_cores,mode=mode,otl_env=otl_env,begin = begin,end = end,return_sets = return_sets))
            return _pd.concat(buf,axis=0) #concatanating partial dataframes

        else:return gx_eterna.analyze_env(  envs,
                                            self.stations_list,self.eterna_path,self.tmp_dir,self.staDb_path,self.project_name,
                                            remove_outliers,restore_otl=restore_otl,blq_file = self.blq_file,sampling = sampling,hardisp_path = self.hardisp_path,
                                            force=force,num_cores = self.num_cores,mode=mode,otl_env=otl_env,begin = begin,end = end,return_sets = return_sets)
        


    def analyze_wetz(self,wetz_gather=None,parameter='WetZ',begin=None,end=None,sampling=1800,force=False,return_sets=False,otl_env=False,v_type='value'):
        '''v_type can be value, nomvalue and sigma. Be careful as it does not create separate dirs but overwrites each v_type. 
        Need to use force option to get the values'''
        if begin is None: 
            begin, end = gx_aux.check_date_margins(begin=begin, end=end, years_list=self.years_list)
        if wetz_gather is None: #wetz_gather may be fascilitated by mGNSS class so different cionstellation solutions will be in sync
            wetz_gather = _np.ndarray((len(self.stations_list)),dtype=object)
            for station in self.stations_list:
                wetz_array = self.filtered_solutions(single_station=station)#ideally a function that can dump wetz gathers. Need to make it concurrent per station
            
            # for i in range(wetz_gather.shape[0]): #for each station effectively
                tmp  = wetz_array[i].loc(axis=1)[:,'.Station.{}.Trop.WetZ'.format(self.stations_list[i].upper())]
                wetz_gather[i] = gx_aux._update_mindex(gx_aux._update_mindex(tmp,self.stations_list[i].upper()),self.mode)

        return gx_eterna.analyze_env(wetz_gather,
                                    self.stations_list,
                                    self.eterna_path,
                                    self.tmp_dir,
                                    self.staDb_path,
                                    self.project_name,
                                    remove_outliers = False,
                                    restore_otl=False,
                                    blq_file = self.blq_file,
                                    sampling = sampling,
                                    hardisp_path = self.hardisp_path,
                                    force=force,
                                    num_cores = self.num_cores,
                                    mode=self.mode,
                                    otl_env=False,
                                    begin = begin,
                                    end = end,
                                    return_sets = return_sets,
                                    v_type=v_type,
                                    parameter=parameter)
    def wetz(self):
        '''Returns WetZ values dataframe'''
        return gx_aux.wetz(self.filtered_solutions())


