from datetime import datetime as _datetime
from subprocess import PIPE as _PIPE
from subprocess import Popen as _Popen

import numpy as _np
import pandas as _pd
from pandas.compat import StringIO as _StringIO

from .gx_const import J2000origin as _J2000origin


def blq2hardisp(blq_file):
    blq_file = _pd.read_csv(blq_file, comment='$', header=None)#[:-2].values
    #we should be ready for different formats: with and without service rows in the end. Namely: Warnings and Errors
    blq_raw = blq_file.squeeze()
    blq_file_read = (blq_raw[(blq_raw!='Warnings:') & (blq_raw!='Errors:')]).values
    
    n_stations = int(blq_file_read.shape[0] / 7)

    sites = (_pd.Series(blq_file_read.reshape(
        (n_stations, 7))[:, 0])).str.strip()

    blq_raw = _pd.Series(blq_file_read.reshape((n_stations, 7))[
                            :, 1:].reshape((n_stations * 6)))
    blq_data = blq_raw.values.reshape((n_stations, 6))

    out = _np.ndarray((n_stations, 2), dtype='object')
    for i in range(n_stations):
        out[i, 0] = sites[i]
        out[i, 1] = _pd.Series(blq_data[i]).to_string(index=False, header=False)

    return out

def reformat_blq(blq_string):
    '''To prevent any problems with Fortran runtime error: Bad value during floating point read
    The problem is with pandas.read_csv that outputs different number of spaces in the beginning and is hard to control'''
    df = _pd.read_csv(_StringIO(blq_string),header=None,delim_whitespace=True)

    amplitude = df.iloc[:3].round(5).to_string(header=None,index=None,float_format='%.5f') #rounding values and string conversion round(5)
    amplitude = _pd.Series(amplitude).str.split('\n',expand=True).T.squeeze().str.split(expand=True).stack().str.lstrip('0').unstack() #formatting with no zero ahead
    
    def a(inp):
        return '{:>6}'.format(inp)
    def b(inp):
        return '{:>7}'.format(inp)
    phase = df.iloc[3:].round(1).to_string(header=None,index=None,formatters=[b,a,a,a,a,a,a,a,a,a,a])

    return amplitude.to_string(header=None,index=None).replace("  "," ") + '\n' + phase

def gen_synth_otl(dataset,station_name,hardisp_path,blq_file,sampling):
    '''Expects stretched dataset. Otherwise can get wrong sampling. Outputs (T, E, N, V) array'''
    _pd.options.display.max_colwidth = 200 #By default truncates text
    begin_J2000 = dataset.index[0];end_J2000 = dataset.index[-1]
    begin = (begin_J2000.astype(int) + _J2000origin).astype(_datetime)
    # end = (end_J2000.astype(int) + _J2000origin).astype(_datetime)
    n_observations = int((end_J2000-begin_J2000)/sampling)+1
    input_blq = blq2hardisp(blq_file)
    input_blq = input_blq[input_blq[:,0] == station_name][0][1]

    '''Takes datetime.datetime format'''
    process = _Popen([hardisp_path, 
                                str(begin.year), 
                                str(begin.month), 
                                str(begin.day), 
                                str(begin.hour), 
                                str(begin.minute), 
                                str(begin.second), str(n_observations), str(sampling)],
                                stdin=_PIPE, stdout=_PIPE, stderr=_PIPE)
    out = _StringIO((process.communicate(input=reformat_blq(input_blq).encode())[0]).decode())
    
    synth_otl = _pd.read_csv(out, error_bad_lines=False, header=None,
                           delim_whitespace=True, names=['dU', 'dS', 'dW']) *1000 #convert to mm as returns in m

    tmp = _pd.DataFrame()
    index=_np.arange(begin_J2000,end_J2000+1,sampling)


    tmp['east'] = synth_otl['dW']*-1 #Conversion to dE. Already checked that it is a correct way (phases) as same as GipsyX does correction (no otl - otl_corrected)
    tmp['north'] = synth_otl['dS']*-1 #Convertion to dN
    tmp['up'] = synth_otl['dU']
    synth_otl['Time']=_pd.Series(_np.arange(begin_J2000,end_J2000+1,sampling))
    hardisp = tmp.set_index(index)
    return hardisp
