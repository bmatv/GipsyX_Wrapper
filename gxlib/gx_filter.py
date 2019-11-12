'''New filter module
Takes the output gather of .solutions() method and does preliminary filtering
with 0.1 derivative margin for X Y Z and 3*std margin for sigma X Y Z'''
import warnings

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

def _filter_sigma(dataset):
    sigma_cut = 0.1 #100 mm hard sigma cut ignoring clk sigma values
    mask = (dataset.sigma.iloc[:,[1,2,3]]<=sigma_cut).min(axis=1)
    return dataset[mask]

def _filter_clk(dataset):
    mask = dataset.sigma.iloc[:,0] < 3000
    # mask =(dataset['value'].iloc[:,0].abs() > 0.01) & (dataset['value'].iloc[:,0].abs() <100)
    return dataset[mask]
    
def filter_tdps(tdps,std_coeff=3,margin=0.1):
    filtered_tdps = _np.ndarray((tdps.shape),dtype = object)
    for i in range(tdps.shape[0]):

        clk_filter = _filter_clk(dataset = tdps[i])
        sigma_filter = _filter_sigma(dataset = clk_filter)
        filtered_tdps[i] = sigma_filter
       
        # sigma_filter = _filter_sigma(dataset = clk_filter, std_coeff=std_coeff)
        print('Clk.Bias Filter: {:.2f} left. Sigmas Filter: {:.2f} left.'.format(clk_filter.shape[0]/tdps[i].shape[0]*100,sigma_filter.shape[0]/tdps[i].shape[0]*100))
        # print('Clk.Bias sigma Filter (<1e8): {:.2f} left. XYZ sigma Filter (<0.1 m): {:.2f} left.'.format(filtered_tdps[i].shape[0]/tdps[i].shape[0]*100))
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

def _stretch(dataset,sampling=300):
    '''
    Stretches the dataset on timeline putting None values where gaps are.
    To be consistent, takes begin of the start year as timeseries start time
    '''
    stretched_dataset = _np.ndarray((dataset.shape),dtype=object)

    MultiIndex_columns = dataset.columns
    timewindow  = _gen_windows(dataset)
    df_theoretical = _pd.DataFrame(index = _np.arange(timewindow[0],timewindow[1],sampling))#input sampling of the dataset(5 mins)

    dataset_tmp = dataset.copy()
    dataset_tmp.columns = dataset.columns.to_series().values # flatten dataset columns so join won't produce warnings
    stretched_dataset = _pd.DataFrame.join(df_theoretical,dataset_tmp)
    stretched_dataset.columns = MultiIndex_columns #restoring columns
    return stretched_dataset

def _avg_30(dataset):

    '''Expects stretched dataset'''
    dataset_reshaped = dataset.values.reshape((int(dataset.shape[0]/6), 6 ,dataset.shape[1]))
    first_elements_rolled = _np.roll(dataset_reshaped[:,0,:],shift=-1,axis=0) #rolling up. So first element becomes last element of previous timeframe
    first_elements_rolled_reshaped = first_elements_rolled.reshape((first_elements_rolled.shape[0],1,first_elements_rolled.shape[1]))
    dataset_reshaped_centered = _np.hstack((dataset_reshaped,first_elements_rolled_reshaped))
    
    time_margins = dataset.index[[0,-1]]
    corrected_time_series = _np.arange(time_margins[0],time_margins[1],1800)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        avg_30 = _pd.DataFrame(_np.nanmean(dataset_reshaped_centered,axis=1), index=corrected_time_series, columns=dataset.columns)
    return avg_30

def average(solutions):
    averaged_solutions = _np.ndarray((solutions.shape),dtype=object)
    for i in range(averaged_solutions.shape[0]):
        averaged_solutions[i] = _avg_30(_stretch(solutions[i]))
    return averaged_solutions
