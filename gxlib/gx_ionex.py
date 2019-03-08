import re
import glob, os, sys
import pandas as pd
import numpy as np
from multiprocessing import Pool

re_begin = re.compile(rb"START\sOF\s(TEC.+\n|RMS.+\n)")
re_end =   re.compile(rb"END\sOF\s(TEC.+\n|RMS.+\n)")

def GIM_data_extraction(file):
    # Extracting ionex data from file
    with open (file, 'rb') as ionex:
        ionex_data = ionex.read()
        GIM_match_begin = [];GIM_match_end = []
        
        matches_begin = re.finditer(re_begin, ionex_data)
        matches_end   = re.finditer(re_end, ionex_data)

        for matchNum, match in enumerate(matches_begin):
            GIM_match_begin.append(match.end())

        for matchNum, match in enumerate(matches_end):
            GIM_match_end.append(match.start()-60) #60 is the number of symbols from the end of the map to marker
            
        frame_n = len(GIM_match_begin)//2
        GIM_boundaries_b = np.asarray(GIM_match_begin).reshape((2,frame_n))
        GIM_boundaries_e = np.asarray(GIM_match_end).reshape((2,frame_n))
        
        TEC = RMS = np.ndarray((frame_n),dtype=object)

        for i in range(frame_n):
            TEC[i] = ionex_data[GIM_boundaries_b[0,i]:GIM_boundaries_e[0,i]].decode('ascii')
            RMS[i] = ionex_data[GIM_boundaries_b[1,i]:GIM_boundaries_e[1,i]].decode('ascii')
            
        Datetime = pd.to_datetime(pd.Series(TEC).str.slice(2,36),format= '%Y %m %d %H %M %S')

    return pd.concat((Datetime,pd.Series(TEC),pd.Series(RMS)),axis=1)


class ionex:
    '''FILES SHOULD BE DECOMPRESSED PRIOR TO PROCESSING. As for the script as for GipsyX processing if fetched by one file'''
    
    def __init__(self,
                ionex_in_files_path='/mnt/Data/bogdanm/Products/IONEX_Products', #IONEX dir
                ionex_type='igs', #type of files
                output_path='/mnt/Data/bogdanm/tmp_GipsyX', #output dir that will have type|year files
                num_cores=10):
        self.ionex_type = ionex_type
        self.output_path = output_path
        self.num_cores = num_cores
        self.ionex_files_list = self._extended_list(ionex_in_files_path,ionex_type)
        self.years_present = self.ionex_files_list.iloc[:,0].unique()
        self.merge_lists = self._create_lists4merge(self.ionex_files_list,self.years_present)
             
    def _extended_list(self,ionex_in_files_path,ionex_type):
        path_series = pd.Series(sorted(glob.glob(ionex_in_files_path+'/*/*/'+ionex_type+'*')))
        properties_series = path_series.str.split('/',expand=True).iloc[:,-3:]
        properties_series.iloc[:,0] = properties_series.iloc[:,0].astype(int)
        return pd.concat((properties_series,path_series),axis=1)
    
    def _get_ionex_list(self,year,extended_list):
        if len(extended_list[extended_list.iloc[:,0]==year-1])==0 & len(extended_list[extended_list.iloc[:,0]==year+1])==0:
            list_files_out =  extended_list[extended_list.iloc[:,0]==year]

        if len(extended_list[extended_list.iloc[:,0]==year-1])==0:
            list_files_out =  pd.concat((extended_list[extended_list.iloc[:,0]==year],
                                         extended_list[extended_list.iloc[:,0]==year+1].head(1)))

        if len(extended_list[extended_list.iloc[:,0]==year+1])==0:
            list_files_out =  pd.concat((extended_list[extended_list.iloc[:,0]==year-1].tail(1),
                                         extended_list[extended_list.iloc[:,0]==year]))
        else:
            list_files_out =  pd.concat((extended_list[extended_list.iloc[:,0]==year-1].tail(1),
                                         extended_list[extended_list.iloc[:,0]==year],
                                         extended_list[extended_list.iloc[:,0]==year+1].head(1)))
        return list_files_out.values
    
    def _create_lists4merge(self,ionex_files_list,years_present):
        merge_lists = np.ndarray((len(years_present)),dtype=object)
        for i in range(len(years_present)):
            merge_lists[i]=self._get_ionex_list(years_present[i],ionex_files_list)
        return merge_lists
    
    def GIM_gen_header(self,merge_list,data_GIM_final):
        '''
        No AUX section in the header needed! IGNORING IT
        LINE with # of MAPS is modified
        '''
        num_maps = '{:6d}{:<54s}{}{:<3s}\n'.format(len(data_GIM_final),' ','# OF MAPS IN FILE',' ')
        regex_first_epoch = (rb"EPOCH\sOF\sFIRST\sMAP\s*\n")


        regex_num_maps_b = (rb"INTERVAL\s{12}\n")
        regex_num_maps_e = (rb"#\sOF\sMAPS\sIN\sFILE\s{3}\n")


        regex_aux_start =   (rb"DIFFERENTIAL\sCODE\sBIASES\s+START\sOF\sAUX\sDATA")
        regex_aux_end   =   (rb"DIFFERENTIAL CODE BIASES\s+END OF AUX DATA\s+\n")

        regex_end_header =  (rb"END\sOF\sHEADER\s+\n")

        #extracting header part from the first document
        with open (merge_list[0],'rb') as ionex_first:
            ionex_data_first = ionex_first.read()

            match_first_epoch = re.search(regex_first_epoch, ionex_data_first)
            
        #extracting header part from the last document ignoring aux data
        with open (merge_list[-1],'rb') as ionex_last:
            ionex_data_last  = ionex_last.read()
            match_last_epoch = re.search(regex_first_epoch, ionex_data_last) #EPOCH OF LAST MAP (LAST FILE to continue the header as headers can have different line quantity)
            
            match_num_maps_b = re.search(regex_num_maps_b, ionex_data_last)
            match_num_maps_e = re.search(regex_num_maps_e, ionex_data_last)

            match_aux_begin  = re.search(regex_aux_start, ionex_data_last)
            match_aux_end    = re.search(regex_aux_end, ionex_data_last)
            match_end_header = re.search(regex_end_header, ionex_data_last)

        return ((ionex_data_first[:match_first_epoch.end()]\
                + ionex_data_last[match_last_epoch.end():match_num_maps_b.end()]).decode('ascii')\
                + num_maps\
                + (ionex_data_last[match_num_maps_e.end():match_aux_begin.start()]\
                + ionex_data_last[match_aux_end.end():match_end_header.end()]).decode('ascii'))
    
    def get_ionex_data(self,merge_list):
        num_cores = self.num_cores if len(merge_list) > self.num_cores else len(merge_list)
        chunksize = int(np.ceil(len(merge_list)/num_cores))
        # Collecting ionex maps from multiple files in parallel
        try:
            pool = Pool(num_cores)
            GIM_data = pool.map(GIM_data_extraction, merge_list[:,3],chunksize=chunksize)
            # GIM_data_extraction expects only array with filepaths
        finally:
            pool.close()
            pool.join()

        # Need this piece of code to kill 00 values eliminating duplicates
        for i in range(len(GIM_data)-1):
            if (GIM_data[i][0].tail(1).dt.hour == 0).iloc[0]:
                GIM_data[i].drop(GIM_data[i][0].tail(1).index[0],inplace = True)

        # Merging all data into two arrays (TEC and RMS) 
        data_GIM_final = pd.DataFrame()
        for element in GIM_data:
            data_GIM_final = pd.concat((data_GIM_final,element[[1,2]]))
        # Resulting array with two columns
        return data_GIM_final.values
    
    def merge_ionex_dataset(self):
        # create dir to where the files will be written
        path = self.output_path+'/IONEX_merged/'
        if not os.path.exists(path):
            os.makedirs(path)
            
        EOF = '{:<60s}{}{:<9s}\n'.format(' ','END OF FILE',' ')
    
        GIM_data=np.ndarray((len(self.years_present)),dtype=object)
        for i in range(len(self.years_present)):
            
            
            GIM_data[i] = self.get_ionex_data(self.merge_lists[i])
            header = self.GIM_gen_header(self.merge_lists[i][:,3],GIM_data[i])
            with open(path+self.ionex_type+str(self.years_present[i]),'w') as output:
                output.write(header)
                #writing TEC data
                for j in range(len(GIM_data[i])):
                    output.write('{:6d}{:<54s}{}{:<4s}\n'.format(i+1,' ','START OF TEC MAP',' '))
                    output.write(GIM_data[i][j,0])
                    output.write('{:6d}{:<54s}{}{:<6s}\n'.format(i+1,' ','END OF TEC MAP',' '))
                    
                #writing RMS data
                for j in range(len(GIM_data[i])):
                    output.write('{:6d}{:<54s}{}{:<4s}\n'.format(i+1,' ','START OF RMS MAP',' '))
                    output.write(GIM_data[i][j,1])
                    output.write('{:6d}{:<54s}{}{:<6s}\n'.format(i+1,' ','END OF RMS MAP',' '))
                    
                output.write(EOF)
# ionex_files = ionex()
# ionex_files.merge_ionex_dataset()