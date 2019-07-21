#!/scratch/bogdanm/miniconda3/envs/py37/bin/python
#PBS -l walltime=48:00:00
#PBS -l select=1:ncpus=28
#PBS -j oe
#PBS -N eu_cod_ana
#PBS -o /scratch/bogdanm/pbs/eu_cod_ana.log
#PBS -m ae
#PBS -M bogdan.matviichuk@utas.edu.au
import os as _os, sys as _sys
GIPSY_WRAP_PATH="/scratch/bogdanm/gipsyx/GipsyX_Wrapper"
if GIPSY_WRAP_PATH not in _sys.path:
    _sys.path.insert(0,GIPSY_WRAP_PATH)

from mGNSS_class import mGNSS_class; import trees_options


kinematic_project = mGNSS_class(project_name = 'eu_cod_ce',
                                staDb_path = '/scratch/bogdanm/tmp_GipsyX/bigf_tmpX//staDb/eu_cod_ce/eu_cod_ce.staDb',
                                tmp_dir = '/scratch/bogdanm/tmp_GipsyX/bigf_tmpX/',
                                cache_path = '/dev/shm',
                                rnx_dir = '/scratch/bogdanm/GNSS_data/geonet_nz',
                                stations_list= ['LERI','PADT', 'PMTH', 'PRAE', 'APPL', 'EXMO',
                                                'TAUT', 'PBIL', 'POOL','SANO','CHIO','CARI', 'SWAS',
                                                'ANLX','HERT','LOFT','WEAR','CAMO','BRAE','BRST','ZIM2'],
                                years_list = [2010, 2011, 2012, 2013],
                                tree_options = trees_options.rw_otl,
                                num_cores = 28,
                                blq_file = '/scratch/bogdanm/Products/otl/ocnld_coeff/FES2004_GBe.blq',
                                VMF1_dir = '/scratch/bogdanm/Products/VMF1_Products',
                                tropNom_input = 'trop',
                                IGS_logs_dir = '/scratch/bogdanm/GNSS_data/station_log_files/bigf_igs_logs',
                                IONEX_products = '/scratch/bogdanm/Products/IONEX_Products',
                                rate = 300,
                                gnss_products_dir = '/scratch/bogdanm/Products/CODE/init/REPRO_2015',
                                ionex_type = 'cod',
                                eterna_path = '/scratch/bogdanm/Products/otl/eterna',
                                hardisp_path = '/scratch/bogdanm/Products/otl/hardisp/hardisp',
                                pos_s = 3.2,
                                wetz_s = 0.1,
                                PPPtype = 'kinematic',
                                tqdm = False)
kinematic_project.analyze()