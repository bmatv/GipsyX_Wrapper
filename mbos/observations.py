# observations.py
#
# A simple interface that reads and writes mom-files and stores
# them into a Python class 'observations'.
#
# 31/1/2019  Machiel Bos, Santa Clara
#==============================================================================

import numpy as np
import pandas as pd
import os
import sys
import math

#==============================================================================
# Class definition
#==============================================================================

class observations:
    """Class to store my time series together with some metadata
    
    Methods
    -------
    momread(fname)
        read mom-file fname and store the data into the mom class
    momwrite(fname)
        write the momdata to a file called fname
    make_continuous()
        make index regularly spaced + fill gaps with NaN's
    """
    
    def __init__(self):
        """This is my time series class
        
        This constructor defines the time series in pandas DataFrame data,
        list of offsets and the sampling period (unit days)
        
        """
        self.data = pd.DataFrame()
        self.offsets = []
        self.sampling_period = 0.0
        self.F = None
    
    def momread(self,fname):
        """Read mom-file fname and store the data into the mom class
        
        Parameters
        ----------
        fname : string
            name of file that will be read
        """
        #--- Check if file exists
        if os.path.isfile(fname)==False:
            print('File {0:s} does not exist'.format(fname))
            sys.exit()
        
        #--- Read the file (header + time series)
        mjd = []
        obs = []
        mod = []
        with open(fname,'r') as fp:
            for line in fp:
                cols = line.split()
                if line.startswith('#')==True:
                    if cols[1]=='sampling' and cols[2]=='period':
                        self.sampling_period = float(cols[3])
                else:
                    if len(cols)<2 or len(cols)>3:
                        print('Found illegal row: {0:s}'.format(line))
                        sys.exit()
                    
                    mjd.append(float(cols[0]))
                    obs.append(float(cols[1]))
                    if len(cols)==3:
                        mod.append(float(cols[2]))
                    
        #---- Create pandas DataFrame
        self.data = pd.DataFrame({'obs':np.asarray(obs)}, \
                                              index=np.asarray(mjd))
        if len(mod)>0:
            self.data['mod']=np.asarray(mod)
            
        #--- Ensure that the observations are regularly spaced
        self.make_continuous()
        
        #--- Create special missing data matrix F
        m = len(self.data.index)
        n = self.data['obs'].isna().sum()
        self.F = np.zeros((m,n))
        j=0
        for i in range(0,m):
            if np.isnan(self.data.iloc[i,0])==True:
                self.F[i,j]=1.0
                j += 1
        
        
                    
        
    def momwrite(self,fname):
        """Write the momdata to a file called fname
        
        Parameters
        ----------
        fname : string
            name of file that will be written
        """
        #--- Try to open the file for writing
        try:
            fp = open(fname,'w') 
        except IOError: 
           print('Error: File {0:s} cannot be opened for written.'. \
                                                         format(fname))
           sys.exit()
        
        #--- Write header
        fp.write('# sampling period {0:f}\n'.format(self.sampling_period))
                 
        #--- Write time series
        for i in range(0,len(self.data.index)):
            if not math.isnan(self.data.iloc[i,0])==True:
                fp.write('{0:12.4f} {1:13.6f}'.format(self.data.index[i],\
                                                  self.data.iloc[i,0]))
                if len(self.data.columns)==2:
                    fp.write(' {0:13.6}\n'.format(self.data.iloc[i,1]))
                else:
                    fp.write('\n')
            
        fp.close()
        
        
    
    def make_continuous(self):
        """Make index regularly spaced + fill gaps with NaN's
        """
        #--- Small number
        EPS = 1.0e-8
        
        #--- Number of observations
        m = len(self.data.index)
        
        mjd0  = self.data.index[0]
        mjd1  = self.data.index[m-1]
        m_new = int((mjd1-mjd0)/self.sampling_period + EPS) + 1
        new_index = np.linspace(mjd0,mjd1,m_new)
        self.data = self.data.reindex(new_index)
        

 
