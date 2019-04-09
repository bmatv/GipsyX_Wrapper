from gd2e_wrap import gd2e_class, gx_convert, gx_aux, gx_ionex
import trees_options
import pandas as _pd

class mGNSS_class:
    def __init__(self,
                project_name,
                stations_list,
                years_list,
                tree_options,
                rnx_dir='/mnt/Data/bogdanm/GNSS_data/BIGF_data/daily30s',
                tmp_dir='/mnt/Data/bogdanm/tmp_GipsyX',
                blq_file = '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf_glo.blq',
                VMF1_dir = '/mnt/Data/bogdanm/Products/VMF1_Products',
                tropNom_type = '30h_tropNominalOut_VMF1.tdp',
                IGS_logs_dir = '/mnt/Data/bogdanm/GNSS_data/BIGF_data/station_log_files',
                IONEX_products = '/mnt/Data/bogdanm/Products/IONEX_Products',
                rate = 300,
                gnss_products_dir = '/mnt/Data/bogdanm/Products/IGS_GNSS_Products/igs2gipsyx/es2_30h_init/',
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
        self.eterna_path=eterna_path
        self.hardisp_path = hardisp_path
        self.mode_table = _pd.DataFrame(data = [['GPS','_g'],['GLONASS','_r'],['GPS+GLONASS','_gr']],columns = ['mode','label'])
        
        self.gps = self.init_gd2e(mode = 'GPS')
        
    def init_gd2e(self, mode):
        '''Initialize gd2e instance wth above parameters but unique mode and updates the poroject_name regarding the mode selected'''
        return gd2e_class(project_name = self.project_name + self.mode2label(mode),
                stations_list = self.stations_list,
                years_list = self.years_list,
                tree_options = self.tree_options,
                mode = mode,
                rnx_dir=self.rnx_dir,
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
    
    def mode2label(self,mode):
        '''expects one of the modes (GPS, GLONASS or GPS+GLONASS and returs g,r or gr respectively for naming conventions)'''
        return self.mode_table[self.mode_table['mode']==mode]['label'].values[0]

#mode should be different automatically