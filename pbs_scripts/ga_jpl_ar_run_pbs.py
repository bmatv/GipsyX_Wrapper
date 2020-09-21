
import sys as _sys
import os as _os
import numpy as _np

GIPSY_WRAP_PATH="/scratch/bogdanm/gipsyx/"
if GIPSY_WRAP_PATH not in _sys.path:
    _sys.path.insert(0,GIPSY_WRAP_PATH)

import GipsyX_Wrapper.trees_options as trees_options
from GipsyX_Wrapper.gxlib.gx_aux import _project_name_construct, gen_staDb, prepare_dir_struct_dr, prepare_dir_struct_gathers
from GipsyX_Wrapper.gxlib.gx_pbs import gen_code, qsub_python_code
from GipsyX_Wrapper.gxlib.gx_trees import gen_trees

#parameters to change-----------------------------------------------------------------------------------------------

project_name = 'ga_jpl_cm'
ionex_type='jpl' #igs ionex map igsg2260.15i is missing data
# gnss_products_dir = '/scratch/bogdanm/Products/JPL_GPS_Products_IGb08/source/Final' #missing files for 2018
gnss_products_dir = '/scratch/bogdanm/Products/JPL_GNSS_Products/source/Final'

#585 stations in total. Below are 423 GPS sites from 2016-01-01 - now. After preleminary cleaning - 363 sites
stations_list= [    #'00NA' and '01NA' removed due to SEPPOLANT_X_MF, '02NA'; '3CA2','3DA2','3DA3','3PAK', '4AUG' no files
                    #'4BYO', '4CB2', '4CHR', '4CRN', '4CRY', '4RMA', '8BAL';'7DLN' very leittle files
        'ALBU', 'ALBY', 'ALIC', 'ANDA',#'ADEL', '8BUN' very little files, , 'ADE1', 'ADE2'
        'ANGS', 'ANNA', 'ANTW', 'APSL', 'ARDL', 'ARMC', 'ARMD', 'ARRT',
        'ARUB', 'ASHF', 'BALA', 'BALL', 'BALM', 'BALN',#'BAIR', 'BALI' removed as no files available, 
        'BANK', 'BARR', 'BATH', 'BBOO', 'BCUS', 'BDST', 'BDVL',#'BDLE' removed
        'BEE2', 'BEEC', 'BEGA', 'BEUA', 'BIGG', 'BING', 'BJCT',#'BINN' no files
        'BKNL', 'BLCK', 'BLRN', 'BMAN', 'BNDC', 'BNDY', 'BNLA', 'BOLC',
        'BOMB', 'BOOR', 'BORA', 'BORT', 'BRBA', 'BRDW', 'BRLA', #'BOOL' processing problems with XYZ
        'BRO1', 'BROC', 'BRWN', 'BUCH', 'BULA', 'BUR2', 'BURA',#'BUR1',
        'BURK', 'CANR', 'CARG', 'CBAR', 'CBLA', 'CBLE', 'CBLT',#'BUSS',
        'CBRA', 'CEDU', 'CKWL', 'CLAC', 'CLAH', 'CLBI', 'CLBN', 'CLEV',
        'CLYT', 'CNBN', 'CNDA', 'CNDO', 'COFF', 'COBG', 'COEN', 'COLE', #'COLL',
        'COMA', 'COOB', 'COOL', 'COPS', 'CRAN', 'CRDX', 'CRSY', 'CSNO',
        'CTMD', 'CUT0', 'CWN2', 'CWRA', 'DARW', 'DBBO', 'DKSN',#'CUND',
        'DLQN', 'DODA', 'DORA', 'DORR', 'DRGO', 'DUNE',#'DWEL','DPRT',
        'DWHY', 'EBNK', 'ECHU', 'ECOR', 'EDEN', 'EDSV', 'EPSM',# 'DWNI' removed
        'ERMG', 'ESPA', 'EXMT', 'FLND', 'FORB', 'FORS', 'FROY', 'FTDN',
        'GABO', 'GASC', 'GATT', 'GFEL', 'GFTH', 'GGTN',#'GELA', 'GFTN', 
        'GILG', 'GLB2', 'GLBN', 'GLDN', 'GLEN', 'GLIN', 'GNGN', 'GNOA',
        'GONG', 'GOOL', 'GORO', 'GUNN', 'GURL', #'GROT', 'HAMI','GWAB',
        'HATT', 'HAY1', 'HERN', 'HILL', 'HLBK', #'HMLT', 'HIL1', 'HNIS' removed
        'HNSB', 'HOB2', 'HOTH', 'HRSM', 'HUGH', 'HYDN', 'IHOE', 'INVL',
        'IPSR', 'IRYM', 'JAB2', 'JERI', 'JERV', 'JLCK',#'KAL5', 'JAB1',
        'KALG', 'KARR', 'KAT1', 'KAT2', 'KELN', 'KEPK', 'KGIS',#'KDAL',
        'KILK', 'KILM', 'KIRR', 'KMAN', 'KRNG', 'KTMB', 'KTON', 'KULW',
        'KUNU', 'LALB', 'LAMB', 'LARR', 'LDHI', 'LGOW', 'LIAW', 'LILY',
        'LIPO', 'LIRI', 'LKHT', 'LKYA', 'LONA', 'LORD', 'LOTH', 'LURA',
        'MACK', 'MAFF', 'MAIN', 'MANY', 'MARY', 'MCHL', 'MEDO',#'MDAH',
        'MENA', 'MENO', 'MGRV', 'MIMI', 'MITT', 'MLAK', 'MNDE',#'MIDL',
        'MNGO', 'MNSF', 'MOBS', 'MOOR', 'MOUL', 'MRBA', 'MREE', 'MRNO',
        'MRNT', 'MRO1', 'MRWA', #'MRT1', 'MRT2', 'MRT3', 'MRT4', 'MRT5'; MRT* sites have limited data of ~2yr 
        'MSVL', 'MTBU', 'MTCV', 'MTDN', 'MTEM', 'MTHR', 'MTIS', 'MTMA',
        'MUDG', 'MULG', 'MURR', 'MWAL', 'MYRT', 'NBRI', 'NBRK', 'NCLF',
        'NDRA', 'NEBO', 'NELN', 'NEWE', 'NEWH', 'NGAN', 'NHIL', 'NMBN',
        'NMTN', 'NNOR', 'NORS', 'NRMN', 'NSTA', 'NTJN', 'NWCS',#'NOOS',
        'NWRA', 'NYMA', 'OBRN', 'OMEO', 'ORNG', 'OVAL', 'PACH',#'ORBO',
        'PARK', 'PBOT', 'PERI', 'PERT', 'PIAN', 'PKVL', 'PMAC', 'POCA',
        'POON', 'PRCE', 'PRKS', 'PRTF', 'PTHL', 'PTKL', 'PTSV',#'PTLD',
        'PUTY', 'QCLF', 'QUAM', 'RAND', 'RANK', 'RAVN', 'RBVL', 'RGLN',
        'RHPT', 'RKLD', 'RNBO', 'RNSP', 'ROBI', 'RSBY',#'RNIS','ROTT',
        'RUTH', 'RUUS', 'RYLS', 'SA45', 'SCON', 'SEAL', 'SEMR', 'SKIP',
        'SNGO', 'SPBY', 'SPWD', 'SRVC', 'STHG', 'STNY', 'STR1', 'STR2',
        'STR3', 'STRH', 'SWNH', 'SYDN', 'SYM1', 'TAMW', 'TARE', 'TATU',
        'TBOB', 'TELO', 'THEV', 'THOM', 'TID1', 'TIDB', 'TITG', 'TLPA',
        'TMBA', 'TMBO', 'TMRA', 'TMUT', 'TNTR', 'TOMP', 'TOOG',#'TOOW', 
        'TOTT', 'TOW2', 'TULL', 'TURO', 'UCLA', 'ULLA', 'UNDE',#'TORK',
        'VLWD', 'WAGN', 'WAKL', 'WALW', 'WARA', 'WARI', 'WARW', 'WBEE',
        'WDBG', 'WEDD', 'WEEM', 'WEND', 'WFAL', 'WGGA', #'WEIP','WHIY'
        'WILU', 'WLAL', 'WLCA', 'WLGT', 'WLWN', 'WMGA', 'WORI',#'WOOL',
        'WOTG', 'WRRN', 'WTCF', 'WWLG', 'WYCH', 'WYNG', 'YALL', 'YANK',
        'YAR2', 'YAR3', 'YARO', 'YARR', 'YARS', 'YASS', 'YEEL',#'YAR1', 
        'YELO', 'YIEL', 'YMBA', 'YNKI', 'YRRM', 'YULA', 'YUNG']

years_list=[2013,2014,2015,2016,2017,2018,2019,2020];num_cores = 28
num_nodes = 20 #default is 10 . nz gd2e shows full load of 20 nodes
if num_nodes > len(stations_list): num_nodes = len(stations_list) #in case staions num is less than num_nodes => num_nodes = stations num
#-------------------------------------------------------------------------------------------------------------------
#We need to generate unique staDb with all the stations
tmp_dir='/scratch/bogdanm/tmp_GipsyX/au_tmpX/'
rnx_dir='/scratch/bogdanm/GNSS_data/GA'
hatanaka=True
# rnx_dir='/scratch/bogdanm/GNSS_data/linz'
# hatanaka=True

IGS_logs_dir = '/scratch/bogdanm/GNSS_data/station_log_files/au_logs'

cddis=False
tree_options = trees_options.rw_otl
blq_file = '/scratch/bogdanm/Products/otl/ocnld_coeff/ga/GA_FES2004_GBe_CM.blq' #need to change this
ElMin = 7
pos_s = 3.2
wetz_s=0.1
PPPtype='kinematic'
VMF1_dir = '/scratch/bogdanm/Products/VMF1_Products'
static_clk = False
ambres = True
cache_path = '/dev/shm'#'/scratch/bogdanm/cache' 
tropNom_input = 'trop'
IONEX_products = '/scratch/bogdanm/Products/IONEX_Products'
rate = 300
eterna_path='/scratch/bogdanm/Products/otl/eterna'
hardisp_path = '/scratch/bogdanm/Products/otl/hardisp/hardisp'
tree_options_code = 'trees_options.rw_otl'
tqdm=False
ElDepWeight = 'SqrtSin'

prepare_dir_struct_dr(begin_year=_np.min(years_list), end_year = _np.max(years_list),tmp_dir=tmp_dir) #prepare dir struct for dr files
project_name_construct = _project_name_construct(project_name=project_name,PPPtype=PPPtype,pos_s=pos_s,wetz_s=wetz_s,tropNom_input=tropNom_input,ElMin=ElMin,ambres=ambres)
prepare_dir_struct_gathers(tmp_dir=tmp_dir,project_name=project_name_construct)

pbs_base = _os.path.join('/scratch/bogdanm/pbs',project_name) #break down by project folders as gets slow on hpc with multiple files
project_name_construct = _project_name_construct(project_name,PPPtype,pos_s,wetz_s,tropNom_input,ElMin,ambres)
#generating tree files that won't be overwritten as crc32 will be the same
gen_trees(  ionex_type=ionex_type,tmp_dir=tmp_dir,tree_options=tree_options,blq_file=blq_file,mode = 'GPS+GLONASS',ElDepWeight=ElDepWeight,
            ElMin = ElMin,pos_s = pos_s,wetz_s = wetz_s,PPPtype = PPPtype,years_list=years_list,cache_path = cache_path,
            VMF1_dir = VMF1_dir,project_name = project_name_construct,static_clk = static_clk,ambres = ambres)#the GNSS_class single project name

staDb_path = gen_staDb(tmp_dir = tmp_dir, project_name = project_name, stations_list = stations_list, IGS_logs_dir = IGS_logs_dir)
stations_list_arrays = _np.array_split(stations_list,num_nodes)
for i in range(len(stations_list_arrays)):
    code = gen_code(stations_list = list(stations_list_arrays[i]), cache_path = cache_path,tropNom_input=tropNom_input, ambres = ambres,ElMin=ElMin,ElDepWeight=ElDepWeight,
                    staDb_path = staDb_path,years_list=years_list,num_cores=num_cores,tmp_dir=tmp_dir,project_name=project_name,IGS_logs_dir=IGS_logs_dir,blq_file=blq_file,
                    VMF1_dir = VMF1_dir,pos_s = pos_s,wetz_s = wetz_s,PPPtype = PPPtype,ionex_type=ionex_type,IONEX_products = IONEX_products,rate = rate,
                    gnss_products_dir = gnss_products_dir,eterna_path=eterna_path,hardisp_path = hardisp_path,rnx_dir=rnx_dir,
                    hatanaka=hatanaka,cddis=cddis,tree_options = tree_options_code,tqdm=False,
                    command='dr_merge();kinematic_project.gps.gd2e();kinematic_project.gps.envs(dump=True)')

    qsub_python_code(code,name='{}{}{}'.format(project_name,str(ElMin) if ElMin != 7 else '',str(i)),
    email='bogdan.matviichuk@utas.edu.au',cleanup=False,pbs_base = pbs_base, walltime='24:00:00')

# dr_merge();kinematic_project.gps.gd2e();kinematic_project.gps.envs(dump=True)
# 'gps.gd2e();kinematic_project.gps.envs(dump=True)'
# rnx2dr();kinematic_project.get_drInfo()