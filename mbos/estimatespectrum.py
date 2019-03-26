# estimatespectrum.py
#
# Estimate the power spectral density from a mom-class
#
# Reference
# ---------
# Burkhard Buttkus (2000), Spectral Analysis and Filter Theory in Applied 
#     Geophysics. Springer-Verlag Berlin Heidelberg, 
#     DOI:10.1007/978-3-642-57016-2
#
# 4/2/2019  Machiel Bos, Coimbra
#==============================================================================

import math
import mominterface
import numpy as np

#==============================================================================
# Subroutines
#==============================================================================

def Parzen(i, M, fraction):
    """ apply Parzen window function from [-M:M]
    fraction is how much of the data is used in the window function. Buttkus
    says 10% is normal but I like higher values. Parzen filter is applied
    to segments [-M:-0.9M] and [0.9M:M] with 1 in between and zeros outside.
 
    Parameters
    ----------
    i : int
        index between 0 and M (location)
    M : int
        half-width of window [-M:M]
    fraction :float
        the fraction inside the window which gets adjusted m=fraction*M

    Returns
    -------
    w : float
        value between 0.0 and 1.0 of window function
    """

    if i<0:              # this is a symmetric window function
        i = -i           
    if i>=M:             # outside range always zero
        return 0.0       
    
    m = int(fraction*M)  # width of interval that gets adjusted
    if i<M-m:            # untouced by filter
      return 1.0
    else:                # filter applies
      if m>0:
          #--- i ranges from M-m to M, s ranges from 0 to 1
          s = float(i-(M-m))/float(m)
      else:
          s = 0.0
      
    
    if i<M-m/2:
        w = 1.0 - 6.0*s*s + 6.0*s*s*s
    else:
        s = 1.0 - s  # function is: 2.0*(1-s)^3
        w = 2.0*s*s*s
    
    #--- Return value of Parzen window function which is between 0 and 1
    return w



def compute_periodogram(ts, m):
    """ Compute the periodogram using m segments

    Parameters
    ----------
    ts : time series class containing pandas DataFrame
        metadate + time series are stored in this class
    m  : int
        number of segments into which the time series is divided
    
    Returns
    -------
    freq : np.array 
        array of frequencies for which the power is computed (Hz)
    G    : np.array 
        array with one sided power spectral density values
    """
    dt = ts.sampling_period*24*3600.0   # unit is Hz
    fraction = 0.5                      # I changed from 0.1 to 0.5
    
    # First, compute the segment length: L= n/segments
    n  = len(ts.data.index)
    L  = n//m
    K  = 2*m-1  # Total number of segments using half overlap
    
    print("Number of data points n : {0:d}".format(n))
    print("Number of segments    K : {0:d}".format(K))
    print("Length of segments    L : {0:d}".format(L))
    
    #--- Compute how much the window function alters the scale
    U = 0.0
    for i in range(0,L):
      U += pow(Parzen(i-L//2,L//2,fraction),2.0)
    U /= float(L) # follow equation 9.96
    scale = dt/(U*float(L))
    
    print("U : {0:f}".format(U))
    print("dt: {0:f}".format(dt))
    
    Variance_xt = 0.0 # Total variance, page 167, SAaFT
    j = 0
    for i in range(0,n):
        x = ts.data.iloc[i,0]
        if len(ts.data.columns)==2:
            x -= ts.data.iloc[i,1]
        if not math.isnan(x): # Skip NaN's
            Variance_xt += x*x
            j += 1
      
    #--- Avoid catastrophes
    if (j>1): 
        Variance_xt /= float(j-1)
    else:
        Variance_xt  = 0.0

    print("Total variance in signal (time domain): {0:f}".\
                                                  format(Variance_xt))
    
    #--- Allocate memory for np.arrays
    G = np.zeros(L//2 + 1, dtype=float)
    Y = np.zeros(L//2 + 1, dtype=complex)
    f = np.zeros(L//2 + 1)
    dummy = np.zeros(L)
    
    #--- For each segment, apply Parzen window function and then FFT
    Variance_Gf = 0.0
    for j in range(0,K):
        #--- Fill dummy array to process next segment
        for i in range(0,L):
            x = ts.data.iloc[j*L//2+i,0]
            if len(ts.data.columns)==2:
                x -= ts.data.iloc[j*L//2+i,1]
            if math.isnan(x)==True: 
                dummy[i] = 0.0;
            else:
                dummy[i] = x * Parzen(i-L//2,L//2,fraction)
       
        #--- Perform real - FFT         
        Y = np.fft.rfft(dummy)
        for i in range(0,L//2+1):
            #--- Compute power
            G[i] += 2.0*scale*(pow(Y[i].real,2.0) + pow(Y[i].imag,2.0))
            
    #--- Divide total to get averaged PSD, which is more accurate
    Variance_Gf = 0.0
    for i in range(0,L//2+1):
        G[i] /= float(K)
        if i==0 or i==L//2:  Variance_Gf += G[i]/(2.0*dt*float(L))
        else:                Variance_Gf += G[i]/(dt*float(L))

        f[i] = float(i)/(dt*float(L)) # compute frequencies
    
    print("Total variance in signal (spectrum)   : {0:f}".format(Variance_Gf))
    print("freq0: {0:e}".format(f[1]))     # first frequency after zero
    print("freq1: {0:e}".format(f[L//2]))  # Nyquist frequency
    
    #--- Return array of frequencies (Hz) and power spectral densities
    return [f,G]


        
      

