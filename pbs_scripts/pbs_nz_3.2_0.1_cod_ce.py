#!/scratch/bogdanm/miniconda3/envs/py37/bin/python
#PBS -l walltime=48:00:00
#PBS -l select=1:ncpus=28
#PBS -j oe
#PBS -o /scratch/bogdanm/out_nz_3.2_cod_p1
#PBS -m ae
#PBS -M bogdan.matviichuk@utas.edu.au
#PBS -N gx_nz_cod_ce

import os as _os, sys as _sys

GIPSY_WRAP_PATH="/scratch/bogdanm/gipsyx/GipsyX_Wrapper"
if GIPSY_WRAP_PATH not in _sys.path:
    _sys.path.insert(0,GIPSY_WRAP_PATH)


'''Kunanyi. This is part one of the project'''
from mGNSS_class import mGNSS_class; import trees_options
stations_list= ['ANAU', 'AUCK', 'BLUF', 'CHTI', 'CORM', 'DNVK', 'DUND', 'DUNT', 'FRTN',
                'GISB', 'GLDB', 'HAAS', 'HAMT', 'HAST', 'HIKB', 'HOKI', 'KAIK', 'KTIA',
                'LEXA', 'LEYL', 'LKTA', 'MAHO', 'MAKO', 'MAVL', 'METH', 'MKNO', 'MNHR',
                'MQZG', 'MTJO', 'NLSN', 'NPLY', 'NRSW', 'OROA', 'PKNO', 'RAHI', 'RAKW',
                'RAUM', 'RGHL', 'RGKW', 'RGMT', 'SCTB', 'TAUP', 'TAUW', 'TGRI', 'TRNG',
                'TRWH', 'VGMT', 'WAIM', 'WANG', 'WARK', 'WEST', 'WGTN', 'WHKT', 'WHNG',
                'WITH']

years_list=[2014,2015,2016,2017,2018];num_cores = 28


kinematic_project = mGNSS_class(project_name = 'nz_cod_ce',
                            tmp_dir='/scratch/bogdanm/tmp_GipsyX/nz_tmpX/',
                            rnx_dir='/scratch/bogdanm/GNSS_data/geonet_nz',
                            stations_list=stations_list,
                            years_list=years_list,
                            tree_options = trees_options.rw_otl, 
                            num_cores=num_cores,
                            blq_file = '/scratch/bogdanm/Products/otl/ocnld_coeff/FES2004_GBe.blq', #to be changed in the future
                            VMF1_dir = '/scratch/bogdanm/Products/VMF1_Products',
                            tropNom_input = 'trop',
                            IGS_logs_dir = '/scratch/bogdanm/GNSS_data/station_log_files/nz_logs',
                            IONEX_products = '/scratch/bogdanm/Products/IONEX_Products',
                            rate = 300,
                            gnss_products_dir = '/scratch/bogdanm/Products/IGS_GNSS_Products/init/es2/',
                            ionex_type='cod', #igs ionex map igsg2260.15i is missing data
                            eterna_path='/scratch/bogdanm/Products/otl/eterna',
                            hardisp_path = '/scratch/bogdanm/Products/otl/hardisp/hardisp',
                            pos_s = 3.2, wetz_s=0.1,PPPtype='kinematic',tqdm=False)

# kinematic_project.rnx2dr()
kinematic_project.gen_tropNom()
# kinematic_project.gd2e()


print('Done')
# # 1.rnx2dr()
# # 2.get_drInfo()
# # 3.drMerge()
# # 4.gen_tropNom()
# kinematic_project.gd2e()
