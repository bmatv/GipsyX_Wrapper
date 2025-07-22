import re as _re
import glob as _glob, os as _os, sys as _sys
import pandas as _pd
import numpy as _np
from multiprocessing import Pool as _Pool
from .gx_aux import uncompress
from shutil import rmtree as _rmtree, copy as _copy
import tqdm as _tqdm

re_begin = _re.compile(rb"START\sOF\s(TEC.+\n|RMS.+\n)")
re_end =   _re.compile(rb"END\sOF\s(TEC.+\n|RMS.+\n)")

def prep_ionex_file(file_path, cache_path):
    file_name = _os.path.basename(file_path)
    tmp_cache_path = _os.path.abspath(_os.path.join(cache_path,file_name)) #create tmp folder in cache
    if not _os.path.exists(tmp_cache_path):
        _os.makedirs(tmp_cache_path)

    _copy(src = file_path, dst = tmp_cache_path) #copy .Z file to cache
    cached_file_path = _os.path.abspath(_os.path.join(tmp_cache_path,_os.path.basename(file_path)))
    uncompress(cached_file_path)
    

    file_path = _os.path.join(_os.path.dirname(cached_file_path),_os.path.splitext(file_name)[0])
    return file_path

def GIM_data_extraction(in_set):
    # Extracting ionex data from file
    file_path = in_set[0]
    cache_path = in_set[1]
    
    
    
    file = prep_ionex_file(file_path, cache_path)

    with open (file, 'rb') as ionex:
        ionex_data = ionex.read()
        GIM_match_begin = [];GIM_match_end = []
        
        matches_begin = _re.finditer(re_begin, ionex_data)
        matches_end   = _re.finditer(re_end, ionex_data)

        for matchNum, match in enumerate(matches_begin):
            GIM_match_begin.append(match.end())

        for matchNum, match in enumerate(matches_end):
            GIM_match_end.append(match.start()-60) #60 is the number of symbols from the end of the map to marker
            
        frame_n = len(GIM_match_begin)//2
        GIM_boundaries_b = _np.asarray(GIM_match_begin).reshape((2,frame_n))
        GIM_boundaries_e = _np.asarray(GIM_match_end).reshape((2,frame_n))
        
        TEC = RMS = _np.ndarray((frame_n),dtype=object)

        for i in range(frame_n):
            TEC[i] = ionex_data[GIM_boundaries_b[0,i]:GIM_boundaries_e[0,i]].decode('ascii')
            RMS[i] = ionex_data[GIM_boundaries_b[1,i]:GIM_boundaries_e[1,i]].decode('ascii')
            
        Datetime = _pd.to_datetime(_pd.Series(TEC).str.slice(2,36),format= '%Y %m %d %H %M %S')
#         print (_pd.concat((Datetime,_pd.Series(TEC),_pd.Series(RMS)),axis=1).head())
    _rmtree(_os.path.dirname(file)) #clean tmp
    return _pd.concat((Datetime,_pd.Series(TEC),_pd.Series(RMS)),axis=1)


class ionex:
    '''FILES SHOULD BE DECOMPRESSED PRIOR TO PROCESSING. As for the script as for GipsyX processing if fetched by one file'''
    
    def __init__(self,
                ionex_prods_dir,#='/mnt/Data/bogdanm/Products/IONEX_Products', #IONEX dir
                ionex_type, #='igs', #type of files
                num_cores,
                cache_path,
                tqdm): #we take cache_path as files will be copied and decompressed before read
        self.ionex_type = ionex_type #add checker here
        self.ionex_prods_dir = _os.path.abspath(ionex_prods_dir)
        self.output_path = _os.path.abspath(_os.path.join(self.ionex_prods_dir,_os.pardir))
        self.num_cores = num_cores    
        self.cache_path = cache_path
        self.tqdm = tqdm
             

    def get_merge_lists(self):
        return self._create_lists4merge(self._extended_list(),self.years_present())

    def _extended_list(self):
        """
        Generates a DataFrame containing metadata and file paths for IONEX files in the specified directory.

        Depending on the `ionex_type` attribute, the method searches for IONEX files using glob patterns:
        - For 'jpl' type: Searches for files matching 'y[1-2][0-9][0-9][0-9]/JPLG*.gz' in the `ionex_prods_dir`.
        - For other types: Searches for files matching '[1-2][0-9][0-9][0-9]/*/<ionex_type>*.Z' in the `ionex_prods_dir`.

        The method extracts relevant properties from the file paths (such as year and file name components),
        and returns a pandas DataFrame with these properties and the full file paths.

        Raises:
            ValueError: If no IONEX files are found for 'jpl' type.

        Returns:
            pandas.DataFrame: A DataFrame containing extracted properties and corresponding file paths.
        """

        if self.ionex_type == 'jpl': #jpl is jpl_native by default
            path_series = _pd.Series(sorted(_glob.glob(_os.path.abspath(_os.path.join(self.ionex_prods_dir,'y[1-2][0-9][0-9][0-9]/JPLG*.gz'))))) #assure we take .Z files
            if path_series.empty:
                msg = f"No IONEX files found at {self.ionex_prods_dir}"
                raise ValueError(msg)
            properties_series = path_series.str.split('/',expand=True).iloc[:,-2:]

            properties_series.insert(loc=1,column=0,value=properties_series.iloc[:,-1].str.slice(4,7))
            properties_series.iloc[:,0] = properties_series.iloc[:,0].str.slice(1).astype(int)
        else:
            path_series = _pd.Series(sorted(_glob.glob(_os.path.abspath(_os.path.join(self.ionex_prods_dir,'[1-2][0-9][0-9][0-9]/*', self.ionex_type+'*.Z'))))) #assure we take .Z files
            if path_series.empty:
                msg = f"No IONEX files found at {self.ionex_prods_dir}"
                raise ValueError(msg)
            properties_series = path_series.str.split('/',expand=True).iloc[:,-3:]
            properties_series.iloc[:,0] = properties_series.iloc[:,0].astype(int)
        return _pd.concat((properties_series,path_series),axis=1)

    def years_present(self):
        return self._extended_list().iloc[:,0].unique()

    def _get_ionex_list(self,year):
        extended_list = self._extended_list()
        if len(extended_list[extended_list.iloc[:,0]==year-1])==0 & len(extended_list[extended_list.iloc[:,0]==year+1])==0:
            list_files_out =  extended_list[extended_list.iloc[:,0]==year]

        if len(extended_list[extended_list.iloc[:,0]==year-1])==0:
            list_files_out =  _pd.concat((extended_list[extended_list.iloc[:,0]==year],
                                         extended_list[extended_list.iloc[:,0]==year+1].head(1)))

        if len(extended_list[extended_list.iloc[:,0]==year+1])==0:
            list_files_out =  _pd.concat((extended_list[extended_list.iloc[:,0]==year-1].tail(1),
                                         extended_list[extended_list.iloc[:,0]==year]))
        else:
            list_files_out =  _pd.concat((extended_list[extended_list.iloc[:,0]==year-1].tail(1),
                                         extended_list[extended_list.iloc[:,0]==year],
                                         extended_list[extended_list.iloc[:,0]==year+1].head(1)))
        return list_files_out.values
    
    def _create_lists4merge(self,ionex_files_list,years_present):
        merge_lists = _np.ndarray((len(years_present)),dtype=object)
        for i in range(len(years_present)):
            merge_lists[i]=self._get_ionex_list(years_present[i])
        return merge_lists
    
           
        
    def _GIM_gen_header(self,in_set,data_GIM_final):
        file_paths = in_set[:,3]
        cache_paths = in_set[:,4]
        
        
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
        first_file_path = prep_ionex_file(file_paths[0], cache_paths[0])
        
        with open (first_file_path,'rb') as ionex_first:
            ionex_data_first = ionex_first.read()

            match_first_epoch = _re.search(regex_first_epoch, ionex_data_first)
        _rmtree(_os.path.dirname(first_file_path))    
        #extracting header part from the last document ignoring aux data
        last_file_path = prep_ionex_file(file_paths[-1], cache_paths[-1])
        with open (last_file_path,'rb') as ionex_last:
            ionex_data_last  = ionex_last.read()
            match_last_epoch = _re.search(regex_first_epoch, ionex_data_last) #EPOCH OF LAST MAP (LAST FILE to continue the header as headers can have different line quantity)
            
            match_num_maps_b = _re.search(regex_num_maps_b, ionex_data_last)
            match_num_maps_e = _re.search(regex_num_maps_e, ionex_data_last)

            match_aux_begin  = _re.search(regex_aux_start, ionex_data_last)
            match_aux_end    = _re.search(regex_aux_end, ionex_data_last)
            match_end_header = _re.search(regex_end_header, ionex_data_last)
        _rmtree(_os.path.dirname(last_file_path)) 
        return ((ionex_data_first[:match_first_epoch.end()]\
                + ionex_data_last[match_last_epoch.end():match_num_maps_b.end()]).decode('ascii')\
                + num_maps\
                + (ionex_data_last[match_num_maps_e.end():match_aux_begin.start()]\
                + ionex_data_last[match_aux_end.end():match_end_header.end()]).decode('ascii'))
    
    def get_ionex_data(self,in_sets):
        

        num_cores = self.num_cores if len(in_sets) > self.num_cores else len(in_sets)
        chunksize = int(_np.ceil(len(in_sets)/num_cores))
        # Collecting ionex maps from multiple files in parallel
        with _Pool(num_cores) as p:
            if self.tqdm:
                GIM_data = list(_tqdm.tqdm(p.imap(GIM_data_extraction, in_sets[:,[3,4]]), total=in_sets.shape[0]))
            else:
                GIM_data = p.map(GIM_data_extraction, in_sets[:,[3,4]])
            # GIM_data_extraction expects only array with filepaths

        # Need this piece of code to kill 00 values eliminating duplicates
        for i in range(len(GIM_data)-1):
            if (GIM_data[i][0].tail(1).dt.hour == 0).iloc[0]:
                GIM_data[i].drop(GIM_data[i][0].tail(1).index[0],inplace = True)

        # Merging all data into two arrays (TEC and RMS) 
        data_GIM_final = _pd.DataFrame()
        for element in GIM_data:
            data_GIM_final = _pd.concat((data_GIM_final,element[[1,2]]))
        # Resulting array with two columns
        return data_GIM_final.values
    
    def merge_ionex_dataset(self,force=False):
        # create dir to where the files will be written
        
        path = self.output_path+'/IONEX_merged/'
        if not _os.path.exists(path):
            _os.makedirs(path)
            
        EOF = '{:<60s}{}{:<9s}\n'.format(' ','END OF FILE',' ')
    
        GIM_data=_np.ndarray((len(self.years_present())),dtype=object)
        for i in range(len(self.years_present())):
            
            merged_file_path = path+self.ionex_type+str(self.years_present()[i])

            if _os.path.exists(merged_file_path) and force: #force mode
                _os.remove(merged_file_path)    
            if not _os.path.exists(merged_file_path):
                merge_list = self.get_merge_lists()[i]
                cache_path_array = _np.ndarray((merge_list.shape[0]),dtype=object)
                cache_path_array.fill(self.cache_path)
                in_sets = _np.column_stack([merge_list,cache_path_array])
                print('Gathering {} {}'.format(self.ionex_type, self.years_present()[i]))

                GIM_data[i] = self.get_ionex_data(in_sets)

                header = self._GIM_gen_header(in_sets,GIM_data[i])

                buf = (header)
                #writing TEC data
                for j in range(len(GIM_data[i])):
                    buf += ('{:6d}{:<54s}{}{:<4s}\n'.format(i+1,' ','START OF TEC MAP',' '))
                    buf += (GIM_data[i][j,0])
                    buf += ('{:6d}{:<54s}{}{:<6s}\n'.format(i+1,' ','END OF TEC MAP',' '))

                #writing RMS data
                for j in range(len(GIM_data[i])):
                    buf += ('{:6d}{:<54s}{}{:<4s}\n'.format(i+1,' ','START OF RMS MAP',' '))
                    buf += (GIM_data[i][j,1])
                    buf += ('{:6d}{:<54s}{}{:<6s}\n'.format(i+1,' ','END OF RMS MAP',' '))

                buf += (EOF)
                with open(merged_file_path,'w') as output:
                    output.write(buf)
            else:
                print('{} already exists'.format(merged_file_path))
# ionex_files = ionex()
# ionex_files.merge_ionex_dataset()


