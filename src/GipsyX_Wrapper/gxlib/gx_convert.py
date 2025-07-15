import glob as _glob
import logging
import os as _os
from multiprocessing import Pool as _Pool
from pathlib import Path
from shutil import copy as _copy
from shutil import rmtree as _rmtree
from subprocess import Popen as _Popen
from typing import List

import numpy as _np
import pandas as _pd
import tqdm as _tqdm

from .gx_aux import prepare_dir_struct_dr, rnx_dr_lbl


def rnxpaths2df(station_files: List[str]):
    rnx_path = _pd.Series(station_files)
    df = rnx_path.str.extract(r"(?P<station_name>[^\W/]{4})(?:(\d{4}\.\d{2})|[^\W/]+_(\d{7}))", expand=True)

    df["doy"] = 0
    df["year"] = 0
    df["rnx_version"] = 2
    rinex_2_mask = df[1].notna()
    df.loc[rinex_2_mask, "doy"] = df[1][rinex_2_mask].str[:3].astype(int)
    df.loc[rinex_2_mask, "year"] = df[1][rinex_2_mask].str[-2:].astype(int)

    df.loc[~rinex_2_mask, "rnx_version"] = 3
    df.loc[~rinex_2_mask, "doy"] = df[2][~rinex_2_mask].str[-3:].astype(int)
    df.loc[~rinex_2_mask, "year"] = df[2][~rinex_2_mask].str[:4].astype(int)

    df.loc[df["year"] < 100, "year"] += 1900
    df.loc[df["year"] < 1950, "year"] += 100
    df["station_name"] = df["station_name"].str.upper()
    df["rnx_path"] = rnx_path
    return df.drop(columns=[1, 2])

def select_rnx(stations_list, years_list, rnx_dir, tmp_dir, cddis=False):
    """
    Outputs a dataframe with rinex files base information: 
    year (int) | station_name (caps) | doy (int) | rnx_path (object) | dr_path (object)
    Works with both RINEX2 and RINEX3 files.
    If cddis is True, it will expect YYd directory to be present inside DOY directory.
    """
    logger = logging.getLogger(__name__)

    rnx_dir = Path.resolve(rnx_dir)
    tmp_dir = Path.resolve(tmp_dir)

    station_files = []
    for station in stations_list:
        for year in years_list:
            station_case_ignore = "".join([f"[{s.upper()}{s.lower()}]" for s in station])
            cddis_dir = "*/" if cddis else ""
            glob_path = f"{rnx_dir}/{str(year)}/*/{cddis_dir}{station_case_ignore}*{str(year)[2:]}*"
            station_files = _glob.glob(glob_path)
            if len(station_files) > 0:
                station_files.extend(station_files)
            else:
                msg = f"gx_convert.select_rnx: No RNX files found for {station}, {year}. Please check rnx_in folder, current pattern is: {glob_path}"
                logger.error(msg)
    if len(station_files) == 0:
        msg = f"gx_convert.select_rnx: No RNX files found for {stations_list}, {years_list}."
        raise ValueError(msg)

    df = rnxpaths2df(station_files)

    dr_dir = f"{tmp_dir}/{rnx_dr_lbl}/"
    dr_filename = (
        df["station_name"].str.lower()
        + df["doy"].astype(str).str.zfill(3)
        + "0."
        + df["year"].astype(str).str.slice(2)
        + ".dr.gz"
    )
    df["dr_path"] = dr_dir + df["year"].astype(str) + "/" + df["doy"].astype(str).str.zfill(3) + "/" + dr_filename
    # preparing dir structure
    prepare_dir_struct_dr(begin_year=df["year"].min(), end_year=df["year"].max(), tmp_dir=tmp_dir)
    return df


def _2dr(rnx2dr_path):
    '''Opens process rxEditGde.py to convert specified rnx to dr file for GipsyX. The subprocess is used in order to run multiple instances at once.
    If converted file is already present, nothing happens
    We might want to dump and kill service tree files and stats'''
    in_file_path = rnx2dr_path[0]
    out_file_path = rnx2dr_path[1]
    cache_path = rnx2dr_path[2]
    staDb_path = rnx2dr_path[3]

    out_dir = _os.path.dirname(out_file_path)

    cache_dir = _os.path.join(cache_path,_os.path.basename(out_file_path)) #smth like /cache/anau2350.10d.dr.gz/
    if not _os.path.exists(cache_dir):
        _os.makedirs(cache_dir)
    _copy(src = in_file_path, dst = cache_dir) #copy 
    in_file_cache_path = _os.path.join(cache_dir,_os.path.basename(in_file_path))
    out_file_cache_path = _os.path.join(cache_dir,_os.path.basename(out_file_path))

    process = _Popen(['rnxEditGde.py', '-dataFile', in_file_cache_path,'-staDb',staDb_path, '-o', out_file_cache_path],cwd = cache_dir)
    process.wait()
    _copy(src = out_file_cache_path, dst = out_dir) #copy result to destination
    #clear folder in ram
    _rmtree(cache_dir)



def rnx2dr(selected_df,num_cores,tqdm,cache_path,staDb_path,cddis=False):
    '''Runs rnxEditGde.py for each file in the class object in multiprocessing'''
    #Checking files that are already in place so not to overwrite
    print('staDb_path:',staDb_path)
    if_exists_array = _np.ndarray((selected_df.shape[0]),dtype=bool)
    for i in range(if_exists_array.shape[0]):
        if_exists_array[i] = not _os.path.exists(selected_df['dr_path'][i])
    selected_df = selected_df[if_exists_array]


    selected_df2convert = selected_df[['rnx_path','dr_path']].copy()
    selected_df2convert['cache_path'] = cache_path #populating df with cache path value
    selected_df2convert['staDb_path'] = staDb_path #populating with staDb_path which is needed as rnx files may lack receiver information
    selected_df2convert = selected_df2convert.values
     
    if selected_df2convert.shape[0] > 0:
        num_cores = num_cores if selected_df2convert.shape[0] > num_cores else selected_df2convert.shape[0]
        print ('Number of files to process:', selected_df2convert.shape[0],'| Adj. num_cores:', num_cores,end=' ')

        with _Pool(processes = num_cores) as p:
            if tqdm: list(_tqdm.tqdm_notebook(p.imap(_2dr, selected_df2convert), total=selected_df2convert.shape[0]))
            else: p.map(_2dr, selected_df2convert)
    else:
        #In case length of unconverted files array is 0 - nothing will be converted
        print('RNX files converted.\nNothing to convert. All available rnx files are already converted')
