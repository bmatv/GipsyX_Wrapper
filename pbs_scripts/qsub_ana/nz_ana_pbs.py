#!/scratch/bogdanm/miniconda3/envs/py37/bin/python
#PBS -l walltime=48:00:00
#PBS -l select=1:ncpus=28
#PBS -j oe
#PBS -N nz_cod_ana
#PBS -o /scratch/bogdanm/pbs/nz_cod_ana.log
#PBS -m ae
#PBS -M bogdan.matviichuk@utas.edu.au
import os as _os, sys as _sys
GIPSY_WRAP_PATH="/scratch/bogdanm/gipsyx/GipsyX_Wrapper"
if GIPSY_WRAP_PATH not in _sys.path:
    _sys.path.insert(0,GIPSY_WRAP_PATH)

from mGNSS_class import mGNSS_class; import trees_options


kinematic_project = mGNSS_class(project_name = 'nz_cod_ce',
                                staDb_path = '/scratch/bogdanm/tmp_GipsyX/nz_tmpX//staDb/nz_cod_ce/nz_cod_ce.staDb',
                                tmp_dir = '/scratch/bogdanm/tmp_GipsyX/nz_tmpX/',
                                cache_path = '/dev/shm',
                                rnx_dir = '/scratch/bogdanm/GNSS_data/geonet_nz',
                                stations_list= ['ANAU', 'AUCK', 'BLUF', 'CHTI', 'CORM', 'DNVK', 'DUND', 'DUNT', 'FRTN',
                                                'GISB', 'GLDB', 'HAAS', 'HAMT', 'HAST', 'HIKB', 'HOKI', 'KAIK', 'KTIA',
                                                'LEXA', 'LEYL', 'LKTA', 'MAHO', 'MAKO', 'MAVL', 'METH', 'MKNO', 'MNHR',
                                                'MQZG', 'MTJO', 'NLSN', 'NPLY', 'NRSW', 'OROA', 'PKNO', 'RAHI', 'RAKW',
                                                'RAUM', 'RGHL', 'RGKW', 'RGMT', 'TAUP', 'TAUW', 'TGRI', 'TRNG', 'TRWH',
                                                'VGMT', 'WAIM', 'WANG', 'WARK', 'WEST', 'WGTN', 'WHKT', 'WHNG', 'WITH'],
                                years_list = [2014, 2015, 2016, 2017, 2018],
                                tree_options = trees_options.rw_otl,
                                num_cores = 28,
                                blq_file = '/scratch/bogdanm/Products/otl/ocnld_coeff/FES2004_GBe.blq',
                                VMF1_dir = '/scratch/bogdanm/Products/VMF1_Products',
                                tropNom_input = 'trop',
                                IGS_logs_dir = '/scratch/bogdanm/GNSS_data/station_log_files/nz_logs',
                                IONEX_products = '/scratch/bogdanm/Products/IONEX_Products',
                                rate = 300,
                                gnss_products_dir = '/scratch/bogdanm/Products/CODE/init/com',
                                ionex_type = 'cod',
                                eterna_path = '/scratch/bogdanm/Products/otl/eterna',
                                hardisp_path = '/scratch/bogdanm/Products/otl/hardisp/hardisp',
                                pos_s = 3.2,
                                wetz_s = 0.1,
                                PPPtype = 'kinematic',
                                tqdm = False)
kinematic_project.analyze()