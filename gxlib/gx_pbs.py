import subprocess
import os as _os

TEMPLATE_SERIAL = """#!/scratch/bogdanm/miniconda3/envs/py37/bin/python
#PBS -l walltime={walltime}
#PBS -l select=1:ncpus=28
#PBS -j oe
#PBS -N {name}
#PBS -o {logfile_path}
#PBS -m ae
#PBS -M {email}
{code}
"""


def qsub_python_code(code,name,email,cleanup,pbs_base,walltime='48:00:00'):
    '''name should have number in it
    qsub_python_code(code,name,email='bogdan.matviichuk@utas.edu.au',cleanup=False,pbs_base = '/scratch/bogdanm/pbs')'''
    if not _os.path.exists(pbs_base):
        _os.makedirs(pbs_base)
    logfile_path = '{}/{}.log'.format(pbs_base,name)
    pbs_script_path = '{}/{}.qsub'.format(pbs_base,name)
    with open(pbs_script_path,'w') as pbs_script:
        pbs_script.write(TEMPLATE_SERIAL.format(name=name, logfile_path = logfile_path, email=email, code=code,walltime=walltime))

    try:
        subprocess.call('qsub {}'.format(pbs_script_path),shell=True)
    finally:
        if cleanup:
            _os.remove(pbs_script_path)

TEMPLATE_MGNSS = '''import os as _os, sys as _sys
GIPSY_WRAP_PATH="/scratch/bogdanm/gipsyx"
if GIPSY_WRAP_PATH not in _sys.path:
    _sys.path.insert(0,GIPSY_WRAP_PATH)

from GipsyX_Wrapper.mGNSS_class import mGNSS_class
import GipsyX_Wrapper.trees_options as trees_options


kinematic_project = mGNSS_class(project_name = '{project_name}',
                                staDb_path = '{staDb_path}',
                                tmp_dir = '{tmp_dir}',
                                cache_path = '{cache_path}',
                                rnx_dir = '{rnx_dir}',
                                hatanaka = {hatanaka},
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
                                cddis = {cddis},
                                ambres = {ambres},
                                ElMin = {ElMin},
                                ElDepWeight= '{ElDepWeight}',
                                tqdm = {tqdm})
kinematic_project.{command}
print('Done!')'''                     

def gen_code(   stations_list,years_list,num_cores,command,project_name,tmp_dir,IGS_logs_dir,staDb_path,blq_file,VMF1_dir,pos_s, wetz_s,PPPtype, ionex_type,  cache_path,
                tropNom_input, ambres,IONEX_products,rate,gnss_products_dir,hatanaka, #we should use COD MGEX, ESA and GFZ later
                eterna_path,hardisp_path,rnx_dir,cddis,tree_options,ElMin,ElDepWeight,tqdm=False):
    return TEMPLATE_MGNSS.format(project_name = project_name,staDb_path = staDb_path,tmp_dir=tmp_dir,rnx_dir=rnx_dir,cddis=cddis,stations_list=stations_list,years_list=years_list,tree_options = tree_options,num_cores=num_cores,
                            blq_file = blq_file,VMF1_dir = VMF1_dir,tropNom_input = tropNom_input,IGS_logs_dir = IGS_logs_dir,IONEX_products = IONEX_products,rate = rate, cache_path = cache_path,ambres = ambres,hatanaka = hatanaka,
                            gnss_products_dir = gnss_products_dir,ionex_type=ionex_type,eterna_path=eterna_path,hardisp_path = hardisp_path,pos_s = pos_s, wetz_s=wetz_s, ElMin=ElMin, ElDepWeight=ElDepWeight,PPPtype=PPPtype,tqdm=tqdm,command=command)