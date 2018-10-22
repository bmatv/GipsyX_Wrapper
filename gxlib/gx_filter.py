def _filter_tdps(tdps,std_coeff=3):
    '''For now commented sigma > 1 filtering'''
    filtered_dataset = _np.ndarray((len(tdps)),dtype=object)
    for i in range(len(tdps)):
        tdp = tdps[i]
        #Step 1. Filtering sigmas - fileter X Y Z sigmas based on <= 3*std, and <1
        filt1_data = tdp [
            #Sigma X
            (tdp['sigma'].iloc[:,0]<=(_np.median(tdp['sigma'].iloc[:,0])+ std_coeff*_np.std(tdp['sigma'].iloc[:,0])))&
            #Sigma Y
            (tdp['sigma'].iloc[:,1]<=(_np.median(tdp['sigma'].iloc[:,1])+ std_coeff*_np.std(tdp['sigma'].iloc[:,1])))&
            #Sigma Z
            (tdp['sigma'].iloc[:,2]<=(_np.median(tdp['sigma'].iloc[:,2])+ std_coeff*_np.std(tdp['sigma'].iloc[:,2])))
            # &
            # #Sigma X
            # (tdp.iloc[:,10]<=1)&
            # #Sigma Y
            # (tdp.iloc[:,11]<=1)&
            # #Sigma Z
            # (tdp.iloc[:,12]<=1)
            ]
        #Step 2. Filtering values - fileter X Y Z values (m) based on -3*std<Value<+3*std
        filt2_data = filt1_data [
            #Value X
            ((filt1_data['value'].iloc[:,0]<=(_np.median(filt1_data['value'].iloc[:,0])+ std_coeff*_np.std(filt1_data['value'].iloc[:,0])))
                                    &(filt1_data['value'].iloc[:,0]>=(_np.median(filt1_data['value'].iloc[:,0])- std_coeff*_np.std(filt1_data['value'].iloc[:,0]))))
            &
            #Value Y
            ((filt1_data['value'].iloc[:,1]<=(_np.median(filt1_data['value'].iloc[:,1])+ std_coeff*_np.std(filt1_data['value'].iloc[:,1])))
                                    &(filt1_data['value'].iloc[:,1]>=(_np.median(filt1_data['value'].iloc[:,1])- std_coeff*_np.std(filt1_data['value'].iloc[:,1]))))
            &
            #Value Z
            ((filt1_data['value'].iloc[:,2]<=(_np.median(filt1_data['value'].iloc[:,2])+ std_coeff*_np.std(filt1_data['value'].iloc[:,2])))
                                    &(filt1_data['value'].iloc[:,2]>=(_np.median(filt1_data['value'].iloc[:,2])- std_coeff*_np.std(filt1_data['value'].iloc[:,2]))))
            ]
        #Step 3. Second pass over sigma values
        filt3_data = filt2_data[
            #Sigma X
            (filt2_data['sigma'].iloc[:,0]<=(_np.median(filt2_data['sigma'].iloc[:,0])+ std_coeff*_np.std(filt2_data['sigma'].iloc[:,0])))&
            #Sigma Y
            (filt2_data['sigma'].iloc[:,1]<=(_np.median(filt2_data['sigma'].iloc[:,1])+ std_coeff*_np.std(filt2_data['sigma'].iloc[:,1])))&
            #Sigma Z
            (filt2_data['sigma'].iloc[:,2]<=(_np.median(filt2_data['sigma'].iloc[:,2])+ std_coeff*_np.std(filt2_data['sigma'].iloc[:,2])))
            ]

        filtered_dataset[i] = filt3_data
    return filtered_dataset