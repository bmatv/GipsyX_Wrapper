from gxlib import gx_aux, gx_compute, gx_convert, gx_extract, gx_filter, gx_merge, gx_trees, gx_tdps, gx_ionex, gx_eterna

class gd2e_class:
    def __init__(self,
                 project_name,
                 stations_list,
                 years_list,
                 tree_options,
                 mode,
                 cddis=False,
                 rnx_dir='/mnt/Data/bogdanm/GNSS_data/BIGF_data/daily30s',
                 tmp_dir='/mnt/Data/bogdanm/tmp_GipsyX',
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
                 num_cores = 8):
        
        self.project_name = project_name
        self.IGS_logs_dir = IGS_logs_dir
        self.rnx_dir=rnx_dir
        self.tmp_dir=tmp_dir
        self.stations_list=stations_list
        self.years_list=years_list
        self.num_cores = num_cores
        self.blq_file = blq_file
        self.VMF1_dir = VMF1_dir
        self.tropNom_type = tropNom_type
        self.tree_options = tree_options
        self.rnx_files = gx_convert.select_rnx(rnx_dir=self.rnx_dir,stations_list=self.stations_list,years_list=self.years_list)
        self.rnx_files_in_out = gx_convert.rnx2dr_gen_paths(rnx_files=self.rnx_files,stations_list=self.stations_list,tmp_dir=self.tmp_dir)
        self.staDb_path= gx_aux.gen_staDb(self.tmp_dir,self.project_name,self.stations_list,self.IGS_logs_dir)
        self.gnss_products_dir = gnss_products_dir
        self.ionex_type=ionex_type
        self.IONEX_products = IONEX_products
        self.ionex = gx_ionex.ionex(ionex_in_files_path=self.IONEX_products, #IONEX dir
                                    ionex_type=self.ionex_type, #type of files
                                    output_path=self.tmp_dir, #output dir that will have type|year files
                                    num_cores=self.num_cores)
        self.rate=rate
        self.refence_xyz_df = gx_aux.get_ref_xyz_sites(staDb_path=self.staDb_path)
        self.mode = self._check_mode(mode)
        self.eterna_path=eterna_path
        self.hardisp_path = hardisp_path
        self.cddis=cddis

    def _check_mode(self,mode):
        modes = ['GPS', 'GLONASS','GPS+GLONASS']
        if mode not in modes:  raise ValueError("Invalid mode. Expected one of: %s" % modes)
        else: return mode
    
    # def analyse(self):
    #     return gx_aux.analyse(rnx_files=self.rnx_files,stations_list=self.stations_list,years_list=self.years_list)
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
        gx_tdps.gen_tropnom(tmp_dir=self.tmp_dir,VMF1_dir=self.VMF1_dir,num_cores=self.num_cores,rate=self.rate,staDb_path=self.staDb_path)
    def gen_trees(self):
        return gx_trees.gen_trees(ionex_type=self.ionex_type,
        tmp_dir=self.tmp_dir,
        tree_options=self.tree_options,
        blq_file=self.blq_file, 
        mode = self.mode)
    def gd2e(self):
        '''merge_table is executed separately to decide based on mode parameter where gd2e will process merged 30h dr file or 24h dr file as both files are in the folder'''
        merge_table = gx_merge.get_merge_table(tmp_dir=self.tmp_dir,mode=self.mode)
        return gx_compute.gd2e(gnss_products_dir=self.gnss_products_dir,
                merge_tables=merge_table,
                num_cores=self.num_cores,
                project_name=self.project_name,
                staDb_path=self.staDb_path,
                stations_list=self.stations_list,
                tmp_dir=self.tmp_dir,
                trees_df=self.gen_trees(),
                tropNom_type=self.tropNom_type,
                years_list=self.years_list)
    def solutions(self):
        return gx_extract.gather_solutions(num_cores=self.num_cores,
                                            project_name=self.project_name,
                                            stations_list=self.stations_list,
                                            tmp_dir=self.tmp_dir)
    def residuals(self):
        return gx_extract.gather_residuals(num_cores=self.num_cores,
                                            project_name=self.project_name,
                                            stations_list=self.stations_list,
                                            tmp_dir=self.tmp_dir)
    def filtered_solutions(self,margin=0.1,std_coeff=3):
        return gx_filter.filter_tdps(margin=margin,std_coeff=std_coeff,tdps=self.solutions())
    
    def envs(self,margin=0.1,std_coeff=3):
        return gx_aux._xyz2env(dataset=self.filtered_solutions(margin=margin,
                                                               std_coeff=std_coeff),
                                                               reference_df=self.refence_xyz_df,
                                                               stations_list=self.stations_list)
    def gen_tdps_penna(self,period=13.9585147,A_East=2, A_North=4, A_Vertical=6):
        gx_tdps.gen_penna_tdp(tmp_path=self.tmp_dir,
                              staDb_path = self.staDb_path,
                              period=period,
                              A_East=A_East,
                              A_North=A_North,
                              A_Vertical=A_Vertical,
                              num_cores = self.num_cores)
    def remove_merged(self):
        '''Removes merged dr files, be it 30h file or 32h file'''
        gx_aux.remove_30h(self.tmp_dir)
        gx_aux.remove_32h(self.tmp_dir)
    def remove_gathers(self):
        gx_extract.rm_solutions_gathers(self.tmp_dir,self.project_name)
        gx_extract.rm_residuals_gathers(self.tmp_dir,self.project_name)

    def get_chalmers(self):
        return gx_aux.get_chalmers(self.staDb_path)

    def analyze_env(self,remove_outliers=True,restore_otl=True,sampling=1800):
        return gx_eterna.analyze_env(
                                    self.envs(),
                                    self.stations_list,
                                    self.eterna_path,
                                    self.tmp_dir,
                                    self.staDb_path,
                                    self.project_name,
                                    remove_outliers,
                                    restore_otl=restore_otl,
                                    blq_file = self.blq_file,
                                    sampling = sampling,
                                    hardisp_path = self.hardisp_path,
                                    )

    def test_analyze(self,remove_outliers=True,sampling=1800):
        '''remove_outliers has no sense here. This is just to get begin and end of the timeline'''
        return gx_eterna.test_analyze(
                                    self.envs(),
                                    self.stations_list,
                                    self.eterna_path,
                                    self.tmp_dir,
                                    self.staDb_path,
                                    self.project_name,
                                    remove_outliers,
                                    blq_file = self.blq_file,
                                    sampling = sampling,
                                    hardisp_path = self.hardisp_path,
                                    )