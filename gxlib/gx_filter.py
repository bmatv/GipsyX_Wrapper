'''New filter module
Takes the output gather of .solutions() method and does preliminary filtering
with 0.1 derivative margin for X Y Z and 3*std margin for sigma X Y Z'''
import numpy as _np

def _filter_derivative(dataset, margin=0.1):
    value_dataset = dataset['value'].iloc[:,[0,1,2]].values
    
    rolled_dataset =_np.roll(value_dataset,1,axis=0)
    derivative = _np.abs(value_dataset - rolled_dataset)
    
    mask = (derivative<=margin).min(axis=1)
    return dataset[mask]

def _filter_sigma(dataset,std_coeff=3):
    sigma_cut = dataset['sigma'].median() + dataset['sigma'].std()*std_coeff
    mask = (dataset['sigma']<=sigma_cut).min(axis=1)
    return dataset[mask]
    
def filter_tdps(tdps,std_coeff=3,margin=0.1):
    filtered_tdps = _np.ndarray((tdps.shape),dtype = object)
    for i in range(tdps.shape[0]):
        step1_filter = _filter_derivative(dataset = tdps[i], margin = margin)
        step2_filter = _filter_sigma(dataset = step1_filter, std_coeff=std_coeff)
        filtered_tdps[i] = step2_filter
        print('step1: {}% left. step2: {}% left.'.format(tdps[i].shape[0]/step1_filter.shape[0]*100, tdps[i].shape[0]/step2_filter.shape[0]*100))
    return filtered_tdps