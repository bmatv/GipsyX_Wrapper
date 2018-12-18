import numpy as _np
import pandas as _pd

from gxlib.gx_aux import J2000origin as _J2000origin
from gxlib.gx_filter import _stretch, _avg_30


def _write_ETERNA(dataset, filename,sampling = 300):
    def a(inp):
        return '{:8d}'.format(inp)
    def b(inp):
        return '{:6d}'.format(inp)
    def c(inp):
        if _np.isnan(inp):

            return '{:9.3s}'.format('')
        else:
            return '{:9.3f}'.format(inp)
        
    #test harmonic dataset
#     data = pandas.DataFrame(data=dataset,columns=['J2000_time','Data'])
    dataset = dataset[~(_pd.isna(dataset.iloc[:,2]))]
    data = _pd.DataFrame(index = dataset.index)
    time_int = dataset.index.values.astype(int)
    data['Time'] = time_int+ _J2000origin

    data['Date_et'] = data['Time'].dt.strftime('%Y%m%d').astype(int)
    data['Time_et'] = data['Time'].dt.strftime('%H%M%S').astype(int)
    data['Data'] = dataset.iloc[:,2]

    file_begin = 'C******************************************************************************\n'
    block_end = '\n99999999\n'
    file_end = '88888888'
    
    #Get blocks if there are gaps:
    block_ends = _np.where(time_int -_np.roll(time_int,1) > sampling)[0]
    block_ends = _np.append(block_ends,-1) #Adding -1 to extract the last block
    block_begin_ind = 0 #Init begin block index which is zero
    
    
    out_buf = file_begin
    for i in range(len(block_ends)):
        block_end_ind = block_ends[i]
        block_begin = 'CAMB               1.0000    1.0000     0.000         0    BLOCK{}\n77777777            0.000\n'.format(i+1)

        out_buf+=(block_begin +
                   data.iloc[block_begin_ind:block_end_ind].to_string(columns=['Date_et', 'Time_et', 'Data'], formatters={'Date_et': a, 'Time_et': b, 'Data': c},
                                  index=False, header=False) + block_end)
        block_begin_ind = block_end_ind
    out_buf+=(file_end)
    
    with open(filename, 'w') as file:
        file.write(out_buf)
        
def _get_trend(dataset,deg=1):
    '''returns''' 
    dataset = dataset[(~_np.isnan(dataset)).min(axis=1)].copy()

    x = dataset.index.values
    y = dataset.values
    p = _np.polyfit(x,y,deg=deg)

    return _pd.DataFrame(p[0]*x[:,_np.newaxis] + p[1],index = x,columns=dataset.columns)

def _remove_outliers(dataset_env,coef=3):
    detrend = dataset_env.value - _get_trend(dataset_env.value)   
    return detrend[(detrend.abs() <= detrend.std()*coef).min(axis=1)]

def _fill_block(block_):
    delta_var = block_.iloc[-1] - block_.iloc[0]
    delta_t = block_.index[-1] - block_.index[0]
    lin_coeff = (delta_var/ delta_t).values
    dT = (block_.index[1:-1]- block_.index[0]).values
    t0_var = block_.iloc[0].values
    block_.iloc[1:-1] = dT[:,_np.newaxis] * lin_coeff + t0_var
    return block_.iloc[1:-1]

def _interp_short_gaps(dataset_avg):
    #expects averaged 30 min sampling ENV dataset as input
    dataset_avg = dataset_avg.copy()
    dataset_breaks = dataset_avg[(~_np.isnan(dataset_avg)).min(axis=1)].copy()
    
    
    dataset_breaks['break_begin'] = _np.roll(dataset_breaks.index,1)
    dataset_breaks['break_end'] = dataset_breaks.index
    dataset_breaks['break_length'] = (((dataset_breaks['break_end'] - dataset_breaks['break_begin']))-1800)/3600 #how many hours is in the break
    short_breaks = dataset_breaks[(dataset_breaks['break_length'] <=12) & (dataset_breaks['break_length'] > 0)] #these are short breaks
    
    tmp=[]
    for i in range(short_breaks.shape[0]):
        begin = short_breaks.iloc[i].break_begin
        end = short_breaks.iloc[i].break_end
        
        block_ = dataset_avg.loc[begin : end]
        tmp.append(_fill_block(block_.copy()))
        
    update = _pd.concat(tmp)
    dataset_avg.loc[update.index] = update
    return dataset_avg

def env2eterna(dataset):
    filt1 = _remove_outliers(dataset)
    filt1_st = _stretch(filt1)
    filt1_avg = _avg_30(filt1_st)
    return _interp_short_gaps(filt1_avg)