import subprocess

import numpy as np

TEMPLATE_SERIAL = """#!/scratch/bogdanm/miniconda3/envs/py37/bin/python
#PBS -l walltime=48:00:00
#PBS -l select=1:ncpus=28
#PBS -j oe
#PBS -N {name}
#PBS -o {logfile_path}
#PBS -m ae
#PBS -M {email}
{code}
"""

import os as _os, sys as _sys
import trees_options
from .gx_aux import gen_staDb, _project_name_construct
from .gx_trees import gen_trees

def qsub_python_code(code,name,email='bogdan.matviichuk@utas.edu.au',cleanup=False,pbs_base = '/scratch/bogdanm/pbs'):
    '''name should have number in it'''
    if not _os.path.exists(pbs_base):
        _os.makedirs(pbs_base)
    logfile_path = '{}/{}.log'.format(pbs_base,name)
    pbs_script_path = '{}/{}.qsub'.format(pbs_base,name)
    with open(pbs_script_path,'w') as pbs_script:
        pbs_script.write(TEMPLATE_SERIAL.format(name=name, logfile_path = logfile_path, email=email, code=code))

    try:
        subprocess.call('qsub {}'.format(pbs_script_path),shell=True)
    finally:
        if cleanup:
            _os.remove(pbs_script_path)

TEMPLATE_MGNSS = '''import os as _os, sys as _sys
GIPSY_WRAP_PATH="/scratch/bogdanm/gipsyx/GipsyX_Wrapper"
if GIPSY_WRAP_PATH not in _sys.path:
    _sys.path.insert(0,GIPSY_WRAP_PATH)

from mGNSS_class import mGNSS_class; import trees_options


kinematic_project = mGNSS_class(project_name = '{project_name}',
                                staDb_path = '{staDb_path}',
                                tmp_dir = '{tmp_dir}',
                                cache_path = '{cache_path}',
                                rnx_dir = '{rnx_dir}',
                                stations_list = {stations_list},
                                years_list = {years_list},
                                tree_options = {tree_options},
                                num_cores = {num_cores},
                                blq_file = '{blq_file}',
                                VMF1_dir = '{VMF1_dir}',
                                tropNom_input = '{tropNom_input}',
                                IGS_logs_dir = '{IGS_logs_dir}',
                                IONEX_products = '{IONEX_products}',
                                rate = {rate},
                                gnss_products_dir = '{gnss_products_dir}',
                                ionex_type = '{ionex_type}',
                                eterna_path = '{eterna_path}',
                                hardisp_path = '{hardisp_path}',
                                pos_s = {pos_s},
                                wetz_s = {wetz_s},
                                PPPtype = '{PPPtype}',
                                ambres = {ambres},
                                tqdm = {tqdm})
kinematic_project.{command}
print('Done!')'''
                            

def gen_code(   stations_list,years_list,num_cores,command,project_name,tmp_dir,IGS_logs_dir,staDb_path,blq_file,VMF1_dir,pos_s, wetz_s,PPPtype, ionex_type,  cache_path,
                tropNom_input, ambres,
                IONEX_products = '/scratch/bogdanm/Products/IONEX_Products',
                rate = 300,
                gnss_products_dir = '/scratch/bogdanm/Products/CODE/init/com', #we should use COD MGEX, ESA and GFZ later
                eterna_path='/scratch/bogdanm/Products/otl/eterna',
                hardisp_path = '/scratch/bogdanm/Products/otl/hardisp/hardisp',
                rnx_dir='/scratch/bogdanm/GNSS_data/geonet_nz',
                tree_options = 'trees_options.rw_otl',
                tqdm=False):
    return TEMPLATE_MGNSS.format(project_name = project_name,staDb_path = staDb_path,tmp_dir=tmp_dir,rnx_dir=rnx_dir,stations_list=stations_list,years_list=years_list,tree_options = tree_options,num_cores=num_cores,
                            blq_file = blq_file,VMF1_dir = VMF1_dir,tropNom_input = tropNom_input,IGS_logs_dir = IGS_logs_dir,IONEX_products = IONEX_products,rate = rate, cache_path = cache_path,ambres = ambres,
                            gnss_products_dir = gnss_products_dir,ionex_type=ionex_type,eterna_path=eterna_path,hardisp_path = hardisp_path,pos_s = pos_s, wetz_s=wetz_s,PPPtype=PPPtype,tqdm=tqdm,command=command)
#------------------------------------------------------------------------------------------
'''Execution part here''' 
stations_list= ['ANAU', 'AUCK', 'BLUF', 'CHTI', 'CORM', 'DNVK', 'DUND', 'DUNT', 'FRTN',
                'GISB', 'GLDB', 'HAAS', 'HAMT', 'HAST', 'HIKB', 'HOKI', 'KAIK', 'KTIA',
                'LEXA', 'LEYL', 'LKTA', 'MAHO', 'MAKO', 'MAVL', 'METH', 'MKNO', 'MNHR',
                'MQZG', 'MTJO', 'NLSN', 'NPLY', 'NRSW', 'OROA', 'PKNO', 'RAHI', 'RAKW',
                'RAUM', 'RGHL', 'RGKW', 'RGMT', 'TAUP', 'TAUW', 'TGRI', 'TRNG', 'TRWH',
                'VGMT', 'WAIM', 'WANG', 'WARK', 'WEST', 'WGTN', 'WHKT', 'WHNG', 'WITH']
# stations_list= ['DUNT']
#'SCTB' station removed as it is in Anatarctica and almost no OTL
years_list=[2014,2015,2016,2017,2018];num_cores = 28
num_nodes = 20 #default is 10 . nz gd2e shows full load of 20 nodes
if num_nodes > len(stations_list): num_nodes = len(stations_list) #in case staions num is less than num_nodes => num_nodes = stations num


project_name_construct = _project_name_construct(project_name,PPPtype,pos_s,wetz_s,tropNom_input,ElMin)
#generating tree files that won't be overwritten as crc32 will be the same
gen_trees(  ionex_type=ionex_type,tmp_dir=tmp_dir,tree_options=tree_options,blq_file=blq_file,mode = 'GPS+GLONASS',
            ElMin = ElMin,pos_s = pos_s,wetz_s = wetz_s,PPPtype = PPPtype,years_list=years_list,cache_path = cache_path,
            VMF1_dir = VMF1_dir,project_name = project_name_construct,static_clk = static_clk,ambres = ambres)#the GNSS_class single project name

staDb_path = gen_staDb(tmp_dir = tmp_dir, project_name = project_name, stations_list = stations_list, IGS_logs_dir = IGS_logs_dir)
stations_list_arrays = np.array_split(stations_list,num_nodes)
for i in range(len(stations_list_arrays)):
    code = gen_code(stations_list = list(stations_list_arrays[i]), cache_path = cache_path,tropNom_input=tropNom_input, ambres = ambres,
                    staDb_path = staDb_path,years_list=years_list,num_cores=num_cores,tmp_dir=tmp_dir,project_name=project_name,IGS_logs_dir=IGS_logs_dir,blq_file=blq_file,
                    VMF1_dir = VMF1_dir,pos_s = pos_s,wetz_s = wetz_s,PPPtype = PPPtype,ionex_type=ionex_type,
                    command='dr_merge();kinematic_project.gd2e();kinematic_project.gather_mGNSS()')
    qsub_python_code(code,name='{}{}'.format(project_name,str(i)),cleanup=False,pbs_base = '/scratch/bogdanm/pbs')
