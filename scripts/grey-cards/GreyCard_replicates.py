#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Tue Jun 3 17:23:38 2025

@author: tjor

# Extraction of diffuse reflectance spectra from Lambda Perkin spectrophotometer 
asc files. 

# The asc files can be output as either absorbance (convertable to 
diffuse reflectance) or transmittance (equivalent to diffuse reflectance for 
the measurement the protcol used)
                                       
# 3 replicates from each card batch (CISRO, DDQ, JJC) were measured. The   
reflectance outputs are saved as a CSV file where columns are wavelength bins, 
row 1 is mean reflectance, row 2 is uncertainty (standard error on mean, at 95% 
confidence interval), row 3 is percentage uncertainty.
                         
"""


import pandas as pd
import numpy as np
import glob   
import matplotlib.pyplot as plt
import os
import uuid

def read_abs_ref(card_files_Abs):   
    '''Reads a batch of absorbance asc files, derives diffuse reflectance,
    then calculates means and uncertainties. Outputs as dataframe.'''
    
    A = [] # absorbance matrix (log scale)
    R = [] # reflection matrix - this equals transmission files
    sample_id = []
    
    for i in range(len(card_files_Abs)):
        
        data_i = pd.read_csv(card_files_Abs[i], skiprows = 90, sep='\t')
        A_i = np.flip(data_i.iloc[:,1].values)
        R_i = 10**(-A_i)*100 # converts abs to linear percentage units - I think this ends up being equivalent to R_diffuse?

        with open(card_files_Abs[i], "r") as file: # this extracts the sample id
            for j in range(9):
                 line = next(file).strip() 
        
        sample_id.append(line)      
        A.append(A_i)
        R.append(R_i)
    
    # stack into np arrays and calcuate mean, uncertainty, and pct uncertainty
    A = np.array(A)
    meanA = np.mean(A, 0)
    uncA = (1.96)*np.std(A ,0)/np.sqrt(3) # 95 % confidence limits define calculated standard error on mean *
    puncA = 100*(uncA/meanA)

    R = np.array(R)
    meanR = np.mean(R, 0)
    uncR = (1.96)*np.std(R ,0)/np.sqrt(3) # 95 % confidence limits define calculated standard error on mean *
    puncR = 100*(uncR/meanR)
    
    wl = np.flip(data_i.iloc[:,0]).values     
    
    A_df = pd.DataFrame(columns=wl, dtype=None, copy=None)
    R_df = pd.DataFrame(columns=wl, dtype=None, copy=None)
    # R_df = pd.DataFrame(R, columns=wl, index=sample_id, dtype=None, copy=None) # includes each spectrum
    # A_df = pd.DataFrame(A, columns=wl, index=sample_id, dtype=None, copy=None)
    
    A_df.loc[len(A_df) + 1,:] = meanA
    A_df = A_df.rename(index={len(A_df): 'Mean'})
    A_df.loc[len(A_df) + 1,:] = uncA
    A_df = A_df.rename(index={len(A_df): 'Unc'})
    A_df.loc[len(A_df) + 1,:] = puncA
    A_df = A_df.rename(index={len(A_df): 'Unc_pct'})
    
    R_df.loc[len(R_df) + 1,:] = meanR
    R_df = R_df.rename(index={len(R_df): 'Mean'})
    R_df.loc[len(R_df) + 1,:] = uncR
    R_df = R_df.rename(index={len(R_df): 'Unc'})
    R_df.loc[len(R_df) + 1,:] = puncR
    R_df = R_df.rename(index={len(R_df): 'Unc_pct'})
    
    return A_df, R_df


def read_trans(card_files_Trans):   
    '''Reads a batch of tranmission (diffuse reflectance) asc files'
    'then calculates means and uncertainties. Outputs as dataframe'''
    
    T = [] # absorbance matrix (log scale)
    sample_id = []
    
    for i in range(len(card_files_Trans)):
        data_i = pd.read_csv(card_files_Trans[i], skiprows = 90, sep='\t')
        T_i = np.flip(data_i.iloc[:,1].values)

        with open(card_files_Trans[i], "r") as file: # this extracts the sample id
            for j in range(9):
                 line = next(file).strip() 
        
        sample_id.append(line)      
        T.append(T_i)

    
    # stack into np arrays and calcuate mean, uncertainty, and pct uncertainty
    T = np.array(T)
    meanT = np.mean(T, 0)
    uncT = (1.96)*np.std(T ,0)/np.sqrt(3) # 95 % confidence limits define calculated standard error on mean *
    puncT = 100*(uncT/meanT)

    wl = np.flip(data_i.iloc[:,0]).values     
    
    T_df = pd.DataFrame(columns=wl, dtype=None, copy=None)

    T_df.loc[len(T_df) + 1,:] = meanT
    T_df = T_df.rename(index={len(T_df): 'Mean'})
    T_df.loc[len(T_df) + 1,:] = uncT
    T_df = T_df.rename(index={len(T_df): 'Unc'})
    T_df.loc[len(T_df) + 1,:] = puncT
    T_df = T_df.rename(index={len(T_df): 'Unc_pct'})
    
    return T_df


def plot_grey_card(R_CISRO, R_DDQ, R_JJC):
    'Spectral plots comparing Reflectance for the 3 card samples'
       
    wl = np.array(list(R_DDQ.columns.values))
  
    i_400 = 225 # wl indices at 400 and 680 nm
    i_680 =  225 + 281
    wl_mean_CISRO = np.mean(R_CISRO.iloc[0, i_400: i_680]) # mean reflectance on [400,680] nm
    wl_mean_DDQ =   np.mean(R_DDQ.iloc[0, i_400: i_680])
    wl_mean_JJC =   np.mean(R_JJC.iloc[0, i_400: i_680])
     
    plt.figure(figsize=(14,8))
    plt.rcParams.update({'font.size': 18})  
    plt.title('Grey card reflectance (mean of 3 replicate measurements)') 
    plt.plot(wl, R_CISRO.iloc[0,:], label='CISRO')
    plt.plot(wl, R_DDQ.iloc[0,:], label='DDQ')
    plt.plot(wl, R_JJC.iloc[0,:], label='JJC')
    plt.ylabel('Diffuse Reflectance [%]')
    plt.xlabel('Wavelength [nm]')
    plt.legend()
    plt.ylim(6,24)
    plt.xlim(300,2000)
    
    filename  =  dir_save + '/'  + 'Greycard_R_fullspectrum.png'
    plt.savefig(filename,dpi=300)
     
    plt.figure(figsize=(14,8))
    plt.title('Grey card reflectance (mean of 3 replicate measurements)')
    plt.rcParams.update({'font.size': 18})
    plt.plot(wl, R_CISRO.iloc[0,:], label='CISRO: R(400-680 mean)='  + str(round(wl_mean_CISRO,1)) + '%')
    plt.plot(wl, R_DDQ.iloc[0,:], label='DDQ: R(400-680 mean)='  + str(round(wl_mean_DDQ,1)) + '%')
    plt.plot(wl, R_JJC.iloc[0,:], label='JJC: R(400-680 mean)='  + str(round(wl_mean_JJC,1)) + ' %')
    plt.ylabel('Diffuse Reflectance [%]')
    plt.xlabel('Wavelength [nm]')
    plt.legend()
    plt.ylim(14,24)
    plt.xlim(380,700)
    
    filename  =  dir_save + '/'  + 'Greycard_R_visiblespectrum.png'
    plt.savefig(filename,dpi=300)
     
     
    #
    wl_mean_CISRO = np.mean(R_CISRO.iloc[1, i_400: i_680])
    wl_mean_DDQ = np.mean(R_DDQ.iloc[1, i_400: i_680])
    wl_mean_JJC = np.mean(R_JJC.iloc[1, i_400: i_680])
     
    plt.figure(figsize=(14,8))
    plt.title('Grey card reflectance (uncertainty of 3 replicate measurements)')
    plt.rcParams.update({'font.size': 18})
    plt.plot(wl, R_CISRO.iloc[1,:], label='CISRO')
    plt.plot(wl, R_DDQ.iloc[1,:], label='DDQ')
    plt.plot(wl, R_JJC.iloc[1,:], label='JJC')
    plt.ylabel('Diffuse Reflectance Uncertainty [%]')
    plt.xlabel('Wavelength [nm]')
    plt.legend()
    plt.ylim(0,1)
    plt.xlim(300,2000)

        
    filename  =  dir_save + '/'  + 'Greycard_R_unc_fullspectrum.png'
    plt.savefig(filename,dpi=300)
          

    plt.figure(figsize=(14,8))
    plt.title('Grey card reflectance  (uncertainty of 3 replicate measurements)')
    plt.rcParams.update({'font.size': 18})
    plt.plot(wl, R_CISRO.iloc[1,:], label='CISRO: R(400-680 mean)='  + str(round(wl_mean_CISRO,4)) + '%')
    plt.plot(wl, R_DDQ.iloc[1,:], label='DDQ: R(400-680 mean)='  + str(round(wl_mean_DDQ,4)) + '%')
    plt.plot(wl, R_JJC.iloc[1,:], label='JJC: R(400-680 mean)='  + str(round(wl_mean_JJC,4)) + ' %')
    plt.ylabel('Diffuse Reflectance Uncertainty [%]')
    plt.xlabel('Wavelength [nm]')
    plt.legend()
    plt.ylim(0,1)
    plt.xlim(380,700)
    
    filename  =  dir_save + '/'  + 'Greycard_R_unc_visiblespectrum.png'
    plt.savefig(filename,dpi=300)   

    return


def write_card_file(R, name, dir_save):
    
   'Saves reflectance data as CSV file, using UUID ID'
    
   ID = name + '_' + str(uuid.uuid4())
   card_file = dir_save + ID  
 
   R.to_csv(card_file, sep = '\t' )

   return




if __name__ == '__main__':

   ###########################################
   # Data directories
   ############################################
   
   dir_main = '/users/rsg-new/tjor/ISPEX_openscience/Source/ispex-analysis/' # if re-using script, change path to your local version of ispex-analysis/' 
   dir_data = dir_main + '/data/grey-cards/20240418_Scan_grey_cards_2000nm_03062025/' # path to folders containing asc files
   dir_save = dir_data + '/Reflectance_output/' # folder where refletance data are output
  
   ############################################
   # Reflectance derived from absorption asc files - these were used to check tranmission
   ############################################

   # dir_card_CISRO = dir_data +'/Abs/CISRO/'
   # card_files_CISRO = sorted(glob.glob(dir_card_CISRO + '/*Sample*.asc*'))  
   #A_CISRO, R_CISRO = read_abs_ref(card_files_CISRO) # Abosrption and Reflectance
   
   # dir_card_DDQ =  dir_data +'/Abs/DDQ/'
   # card_files_DDQ = sorted(glob.glob(dir_card_DDQ + '/*Sample*.asc*'))  
   # A_DDQ, R_DDQ = read_abs_ref(card_files_DDQ)
   
   # dir_card_JJC = dir_data +'/Abs/JJC/'
   # card_files_JJC = sorted(glob.glob(dir_card_JJC + '/*Sample*.asc*'))  
   # A_JJC, R_JJC = read_abs_ref(card_files_JJC)
   
   #################################################
   # Reflectance derived from transmission asc files - quicker to work with as T==R for measurement protocol
   ################################################
   
   dir_card_CISRO = dir_data + '/Trans/CISRO/'
   card_files_CISRO = sorted(glob.glob(dir_card_CISRO + '/*Sample*.asc*'))  
   R_CISRO = read_trans(card_files_CISRO)
   
   dir_card_DDQ = dir_data + '/Trans/DDQ/'
   card_files_DDQ = sorted(glob.glob(dir_card_DDQ + '/*Sample*.asc*'))  
   R_DDQ = read_trans(card_files_DDQ)
   
   dir_card_JJC = dir_data +'/Trans/JJC/'
   card_files_JJC = sorted(glob.glob(dir_card_JJC + '/*Sample*.asc*'))  
   R_JJC = read_trans(card_files_JJC)
   
   ############################################
   # Plot output
   #####################################
   plot_grey_card(R_CISRO, R_DDQ, R_JJC)
   
   ###############################
   # Outputs as CSV file 
   ##############################################
   write_card_file(R_CISRO,'CISRO', dir_save)
   write_card_file(R_JJC,'JJC', dir_save)
   write_card_file(R_DDQ,'DDQ', dir_save)