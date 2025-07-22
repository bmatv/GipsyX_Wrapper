import subprocess
import sys as _sys, os as _os
from pathlib import Path

import numpy as _np

from GipsyX_Wrapper.mGNSS_class import mGNSS_class
from GipsyX_Wrapper import trees_options
from GipsyX_Wrapper.gxlib.gx_aux import _project_name_construct, gen_staDb, prepare_dir_struct_dr, prepare_dir_struct_gathers, j2000_to_datetime
from GipsyX_Wrapper.gxlib.gx_trees import gen_trees

#parameters to change-----------------------------------------------------------------------------------------------

project_name = 'demo_jpl_cm'
ionex_type='jpl'
gnss_products_dir = '/home/bogdanm/gnss/products/JPL_GNSS_Products_IGS14/Final'

stations_list= ['HOB2','ALIC', 'STR2'] # STR2 is not in the blq file
years_list=[2014,]

#We need to generate unique staDb with all the stations
tmp_dir='/home/bogdanm/gnss/tmp_GipsyX/demo_2014_tmpX'
rnx_dir='/home/bogdanm/gnss/data'
IGS_logs_dir = '/home/bogdanm/gnss/site-logs' # should be one more level here
hatanaka=True #True if you want to use d.Z or d.gz files, False for o.Z or o.gz
tree_options = trees_options.rw_otl
blq_file = (Path(__file__).absolute().parent/"demo.blq").as_posix()
ElMin = 7
pos_s = 3.2
wetz_s=0.1
PPPtype='kinematic'
VMF1_dir = '/home/bogdanm/gnss/products/VMF1'
static_clk = False
ambres = True
cddis=False 
cache_path = '/dev/shm'#'/scratch/bogdanm/cache' 
tropNom_input = 'trop'
IONEX_products = '/home/bogdanm/gnss/products/IONEX_final'
rate = 300
eterna_path='/scratch/bogdanm/Products/otl/eterna'
hardisp_path = '/scratch/bogdanm/Products/otl/hardisp/hardisp'
tree_options_code = 'trees_options.rw_otl'
tqdm=True
ElDepWeight = 'SqrtSin'

num_cores = 20


# pip install blosc pandas pyarrow tqdm

prepare_dir_struct_dr(begin_year=_np.min(years_list), end_year = _np.max(years_list),tmp_dir=tmp_dir) #prepare dir struct for dr files
# project_name_construct is only needed for dir structure creation
project_name_construct = _project_name_construct(project_name=project_name,PPPtype=PPPtype,pos_s=pos_s,wetz_s=wetz_s,tropNom_input=tropNom_input,ElMin=ElMin,ambres=ambres)
prepare_dir_struct_gathers(tmp_dir=tmp_dir,project_name=project_name_construct)
# we use project_name below

#generating tree files that won't be overwritten as crc32 will be the same
gen_trees(  ionex_type=ionex_type,tmp_dir=tmp_dir,tree_options=tree_options,blq_file=blq_file,mode = 'GPS+GLONASS',ElDepWeight=ElDepWeight,
            ElMin = ElMin,pos_s = pos_s,wetz_s = wetz_s,PPPtype = PPPtype,years_list=years_list,cache_path = cache_path,
            VMF1_dir = VMF1_dir,project_name = project_name,static_clk = static_clk,ambres = ambres)#the GNSS_class single project name

staDb_path = gen_staDb(tmp_dir = tmp_dir, project_name = project_name, stations_list = stations_list, IGS_logs_dir = IGS_logs_dir)
print(staDb_path)
print(stations_list)


kinematic_project = mGNSS_class(project_name = project_name,
                                staDb_path = staDb_path,
                                tmp_dir = tmp_dir,
                                cache_path = cache_path,
                                rnx_dir = rnx_dir,
                                hatanaka = hatanaka,
                                stations_list = stations_list,
                                years_list = years_list,
                                tree_options = tree_options,
                                num_cores = num_cores,
                                blq_file = blq_file,
                                VMF1_dir = VMF1_dir,
                                tropNom_input = tropNom_input,
                                IGS_logs_dir = IGS_logs_dir,
                                IONEX_products = IONEX_products,
                                rate = rate,
                                gnss_products_dir = gnss_products_dir,
                                ionex_type = ionex_type,
                                eterna_path = eterna_path,
                                hardisp_path = hardisp_path,
                                pos_s = pos_s,
                                wetz_s = wetz_s,
                                PPPtype = PPPtype,
                                cddis = cddis,
                                ambres = ambres,
                                ElMin = ElMin,
                                ElDepWeight= ElDepWeight,
                                tqdm = tqdm)

kinematic_project.rnx2dr()
kinematic_project.get_drInfo()
kinematic_project.gather_drInfo() # trop nominals are taken from here
kinematic_project.dr_merge()
kinematic_project.gen_tropNom()
kinematic_project.ionex.merge_ionex_dataset()

print(kinematic_project.gps.get_chalmers())

# kinematic_project.gps.gd2e()
