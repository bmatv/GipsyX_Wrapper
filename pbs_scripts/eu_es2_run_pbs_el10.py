import numpy as np
import sys as _sys
GIPSY_WRAP_PATH="/scratch/bogdanm/gipsyx/GipsyX_Wrapper"
if GIPSY_WRAP_PATH not in _sys.path:
    _sys.path.insert(0,GIPSY_WRAP_PATH)
import trees_options
from gxlib.gx_aux import gen_staDb, _project_name_construct
from gxlib.gx_trees import gen_trees
from gxlib.gx_pbs import gen_code, qsub_python_code

#parameters to change-----------------------------------------------------------------------------------------------

project_name = 'eu_es2_ce'
ionex_type='esa' #igs ionex map igsg2260.15i is missing data
gnss_products_dir = '/scratch/bogdanm/Products/IGS_GNSS_Products/init/es2' #we should use COD MGEX, ESA and GFZ later


'''Execution part here''' 
stations_list= ['LERI','PADT', 'PMTH', 'PRAE', 'APPL', 'EXMO',
                'TAUT', 'PBIL', 'POOL','SANO','CHIO','CARI', 'SWAS',
                'ANLX','HERT','LOFT','WEAR','CAMO','BRAE','BRST','ZIM2']
#'SCTB' station removed as it is in Anatarctica and almost no OTL
years_list=[2010,2011,2012,2013];num_cores = 28
num_nodes = 10
if num_nodes > len(stations_list): num_nodes = len(stations_list) #in case staions num is less than num_nodes => num_nodes = stations num
#-------------------------------------------------------------------------------------------------------------------

#We need to generate unique staDb with all the stations
tmp_dir='/scratch/bogdanm/tmp_GipsyX/bigf_tmpX/'
rnx_dir='/scratch/bogdanm/GNSS_data/BIGF_data/daily30s'
IGS_logs_dir = '/scratch/bogdanm/GNSS_data/station_log_files/bigf_igs_logs'
tree_options = trees_options.rw_otl
blq_file = '/scratch/bogdanm/Products/otl/ocnld_coeff/FES2004_GBe.blq'
ElMin = 10
pos_s = 3.2
wetz_s=0.1
PPPtype='kinematic'
VMF1_dir = '/scratch/bogdanm/Products/VMF1_Products'
static_clk = False
ambres = False
cache_path = '/dev/shm'#'/scratch/bogdanm/cache' 
tropNom_input = 'trop'
IONEX_products = '/scratch/bogdanm/Products/IONEX_Products'
rate = 300
eterna_path='/scratch/bogdanm/Products/otl/eterna'
hardisp_path = '/scratch/bogdanm/Products/otl/hardisp/hardisp'
tree_options_code = 'trees_options.rw_otl'
tqdm=False

project_name_construct = _project_name_construct(project_name,PPPtype,pos_s,wetz_s,tropNom_input,ElMin)
#generating tree files that won't be overwritten as crc32 will be the same
gen_trees(  ionex_type=ionex_type,tmp_dir=tmp_dir,tree_options=tree_options,blq_file=blq_file,mode = 'GPS+GLONASS',
            ElMin = ElMin,pos_s = pos_s,wetz_s = wetz_s,PPPtype = PPPtype,years_list=years_list,cache_path = cache_path,
            VMF1_dir = VMF1_dir,project_name = project_name_construct,static_clk = static_clk,ambres = ambres)#the GNSS_class single project name

staDb_path = gen_staDb(tmp_dir = tmp_dir, project_name = project_name, stations_list = stations_list, IGS_logs_dir = IGS_logs_dir)
stations_list_arrays = np.array_split(stations_list,num_nodes)
for i in range(len(stations_list_arrays)):
    code = gen_code(stations_list = list(stations_list_arrays[i]), cache_path = cache_path,tropNom_input=tropNom_input, ambres = ambres, ElMin=ElMin,
                    staDb_path = staDb_path,years_list=years_list,num_cores=num_cores,tmp_dir=tmp_dir,project_name=project_name,IGS_logs_dir=IGS_logs_dir,blq_file=blq_file,
                    VMF1_dir = VMF1_dir,pos_s = pos_s,wetz_s = wetz_s,PPPtype = PPPtype,ionex_type=ionex_type,IONEX_products = IONEX_products,rate = rate,
                    gnss_products_dir = gnss_products_dir,eterna_path=eterna_path,hardisp_path = hardisp_path,rnx_dir=rnx_dir,tree_options = tree_options_code,tqdm=False,
                    command='gd2e();kinematic_project.gather_mGNSS()')
    qsub_python_code(code,name='{}el10_{}'.format(project_name,str(i)),email='bogdan.matviichuk@utas.edu.au',cleanup=False,pbs_base = '/scratch/bogdanm/pbs')

#gen_tropNom can not be run rhis way as we need all the stations to be present
# kinematic_project.get_drInfo()   .gather_drInfo()
# 'gd2e()' was executed!!! ALL OK