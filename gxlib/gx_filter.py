'''New filter module
Takes the output gather of .solutions() method and does preliminary filtering
with 0.1 derivative margin for X Y Z and 3*std margin for sigma X Y Z'''
import numpy as _np
import pandas as _pd
from .gx_aux import J2000origin

def _filter_derivative(dataset, margin=0.1):
    value_dataset = dataset['value'].iloc[:,[0,1,2]].values
    
    rolled_dataset =_np.roll(value_dataset,1,axis=0)
    derivative = _np.abs(value_dataset - rolled_dataset)
    
    mask = (derivative<=margin).min(axis=1)
    return dataset[mask]

def _filter_value(dataset,std_coeff=3):
    sigma_cut = dataset['value'].median() + dataset['value'].std()*std_coeff
    mask = (dataset['value']<=sigma_cut).min(axis=1)
    return dataset[mask]

def _filter_sigma(dataset,std_coeff=3):
    sigma_cut = dataset['sigma'].median() + dataset['sigma'].std()*std_coeff
    mask = (dataset['sigma']<=sigma_cut).min(axis=1)
    return dataset[mask]
    
def filter_tdps(tdps,std_coeff=3,margin=0.1):
    filtered_tdps = _np.ndarray((tdps.shape),dtype = object)
    for i in range(tdps.shape[0]):
        step1_filter = _filter_derivative(dataset = tdps[i], margin = margin)
        step2_filter = _filter_value(dataset = step1_filter, std_coeff=std_coeff)
        filtered_tdps[i] = step2_filter
        print('step1: {:.2f}% left. step2: {:.2f}% left.'.format(step1_filter.shape[0]/tdps[i].shape[0]*100, step2_filter.shape[0]/tdps[i].shape[0]*100))
        filtered_tdps[i] = step2_filter
    return filtered_tdps

'''30-minute averaging here'''
def _gen_windows(dataset):
    '''
    Takes dataset indexed by time as an input (This also means it is sorted by time). Time in J2000.
    Returns window configuration. Begin = begin of the first dat's year. End = Last day's year+1 begin.
    Begin year sync.
    Comment: Shall it be sorted? Probably yes'''
    #computing dataset timeseries parameters
    time_frame_in = dataset.index[[0,-1]].values.astype('timedelta64') + J2000origin #Getting first and last time values of the dataset (pandas index)

    time_frame_out = _np.ndarray((time_frame_in.shape),dtype=('datetime64[s]'))
    time_frame_out[0] = time_frame_in[0].astype('datetime64[Y]')
    time_frame_out[1] = time_frame_in[1].astype('datetime64[Y]')+1

    return (time_frame_out - J2000origin).astype(_np.float64)

def _stretch(dataset):
    '''
    Stretches the dataset on timeline putting None values where gaps are.
    To be consistent, takes begin of the start year as timeseries start time
    '''
    stretched_dataset = _np.ndarray((dataset.shape),dtype=object)

    MultiIndex_columns = dataset.columns
    timewindow  = _gen_windows(dataset)
    df_theoretical = _pd.DataFrame(index = _np.arange(timewindow[0],timewindow[1],300))#input sampling of the dataset(5 mins)

    dataset_tmp = dataset.copy()
    dataset_tmp.columns = dataset.columns.to_series().values # flatten dataset columns so join won't produce warnings
    stretched_dataset = _pd.DataFrame.join(df_theoretical,dataset_tmp)
    stretched_dataset.columns = MultiIndex_columns #restoring columns
    return stretched_dataset

def _avg_30(dataset):
    
    dataset_reshaped = dataset.values.reshape((int(dataset.shape[0]/6), 6 ,dataset.shape[1]))
    first_elements_rolled = _np.roll(dataset_reshaped[:,0,:],shift=-1,axis=0) #rolling up. So first element becomes last element of previous timeframe
    first_elements_rolled_reshaped = first_elements_rolled.reshape((first_elements_rolled.shape[0],1,first_elements_rolled.shape[1]))
    dataset_reshaped_centered = _np.hstack((dataset_reshaped,first_elements_rolled_reshaped))
    
    time_margins = dataset.index[[0,-1]]
    corrected_time_series = _np.arange(time_margins[0],time_margins[1],1800)
    return _pd.DataFrame(_np.nanmean(dataset_reshaped_centered,axis=1), index=corrected_time_series, columns=dataset.columns)

def average(solutions):
    averaged_solutions = _np.ndarray((solutions.shape),dtype=object)
    for i in range(averaged_solutions.shape[0]):
        averaged_solutions[i] = _avg_30(_stretch(solutions[i]))
    return averaged_solutions


