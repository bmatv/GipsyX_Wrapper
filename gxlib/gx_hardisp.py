import pandas as _pd
import numpy as _np

from gxlib.gx_aux import J2000origin as _J2000origin
from subprocess import Popen as _Popen, PIPE as _PIPE
from pandas.compat import StringIO as _StringIO
from datetime import datetime as _datetime

_pd.options.display.max_colwidth = 100 #By default truncates text

def blq2hardisp(blq_file = '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq'):
    blq_file_read = _pd.read_csv(blq_file, comment='$', header=None)[:-2].values

    n_stations = int(blq_file_read.shape[0] / 7)

    sites = (_pd.Series(blq_file_read.reshape(
        (n_stations, 7))[:, 0])).str.strip()

    blq_raw = _pd.Series(blq_file_read.reshape((n_stations, 7))[
                            :, 1:].reshape((n_stations * 6)))
    blq_data = blq_raw.values.reshape((n_stations, 6))

    out = _np.ndarray((n_stations, 2), dtype='object')
    for i in range(n_stations):
        out[i, 0] = sites[i]
        out[i, 1] = '  ' + \
            _pd.Series(blq_data[i]).to_string(index=False, header=False)

    return out

def gen_synth_otl(dataset,station_name,hardisp_path = '/home/bogdanm/Desktop/otl/hardisp/hardisp',blq_file = '/mnt/Data/bogdanm/tmp_GipsyX/otl/ocnld_coeff/bigf.blq',sampling = 1800):
    '''Expects stretched dataset. Otherwise can get wrong sampling. Outputs (T, E, N, V) array'''
    begin_J2000 = dataset.index[0];end_J2000 = dataset.index[-1]
    begin = (begin_J2000.astype(int) + _J2000origin).astype(_datetime)
    # end = (end_J2000.astype(int) + _J2000origin).astype(_datetime)
    n_observations = int((end_J2000-begin_J2000)/sampling)+1
    input_blq = blq2hardisp(blq_file)

    '''Takes datetime.datetime format'''
    process = _Popen([hardisp_path, 
                                str(begin.year), 
                                str(begin.month), 
                                str(begin.day), 
                                str(begin.hour), 
                                str(begin.minute), 
                                str(begin.second), str(n_observations), str(sampling)],
                                stdin=_PIPE, stdout=_PIPE, stderr=_PIPE)
    out = _StringIO((process.communicate(input=str(input_blq[input_blq[:,0] == station_name,1][0]).encode())[0]).decode())
    

    synth_otl = _pd.read_csv(out, error_bad_lines=False, header=None,
                           delim_whitespace=True, names=['dU', 'dS', 'dW']) *1000 #convert to mm as returns in m

    tmp = _pd.DataFrame()
    index=_np.arange(begin_J2000,end_J2000+1,sampling)


    tmp[station_name + '.E'] = synth_otl['dW']*-1 #Conversion to dE. Already checked that it is a correct way (phases) as same as GipsyX does correction (no otl - otl_corrected)
    tmp[station_name + '.N'] = synth_otl['dS']*-1 #Convertion to dN
    tmp[station_name + '.V'] = synth_otl['dU']
    synth_otl['Time']=_pd.Series(_np.arange(begin_J2000,end_J2000+1,sampling))
    hardisp = tmp.set_index(index)
    return hardisp