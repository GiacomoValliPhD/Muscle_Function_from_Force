""" 
Muscle_Function_from_Force
Version 1.03

Author: Giacomo Valli
Contacts: giacomo.valli@phd.unipd.it

--- Description --

This script was made for UNIPD students, to compute:
- MViF (maximum voluntary isometric force (N)),
- TTP63 (time to reach the 63% of the MViF (mSec)),
- RFD (rate of force development (N/Sec)) after 50, 100, 150 and 200 mSec
- AC (activation capacity (%))

The input is a .mat file containing the reference signal (force)
exported from Labchart at 1000 Hz sampling frequency, but it works also with 
a different sampling frequency

Two sample files can be found in the GitHub repository

The user only needs to run the script and read the instructions in the interactive figures

The script automatically filters the signal from noise caused by the alternate current
with a low-pass, fourth order, Zero-lag Butterworth filter.

The script automatically removes force offset based on the starting point used for
the calculation of TTP63.

Instructions on what to do can be found in the plots' titles

To work with the plots:
    - Any letter of the keyboard adds a point
    - Mouse right click deletes the point
    - Enter terminates the task (press it once all the points have been selected)
    - You can zoom-in the plot after pressing the magnifier icon
    - Press home to restore the original view

If you use the script for different purposes, please double check the results.

Keep everything organised with a virtual enviorment.
To create a virtual enviorment type in the terminal:
- py -m venv mfenv

To install the required libraries type in the terminal:
- py -m pip install -r requirements.txt
"""

############################################# Input part #################################################
from pathlib import Path
"""
You can change the initial directory of the GUI based open-file function
It is useful to speed-up the research of the file to open
"""

initialdir = Path("/")


############################# Start of the script - don't modify here ######################################
from scipy.io import loadmat
from scipy import signal
import matplotlib.pyplot as plt
import pandas as pd
import time
import os
from tkinter import *
from tkinter import filedialog

# Create and hide the tkinter root window necessary for the GUI based open-file function
root = Tk()
root.withdraw()

file_toOpen = filedialog.askopenfilename(initialdir=initialdir,
                                        title="Select a file", 
                                        filetypes=[("Matlab files" , ".mat")]
                                        )

# Destroy the root since it is no longer necessary
root.destroy()

# Extract the name of the file and its location from the file path (file_toOpen)
filename = os.path.basename(file_toOpen)
location = os.path.dirname(file_toOpen)

# Open the selected MATLAB file
mat_file = loadmat(file_toOpen, simplify_cells=True)
refsig = mat_file["data"]
fsamp = mat_file["samplerate"]

# Convert the refsig from array to df
refsig = pd.DataFrame(refsig)

# Convert Kg in N
refsig[0] = refsig[0] * 9.81

# Filter the force signal with a low-pass, fourth order, Zero-lag Butterworth filter
""" 
40 Hz is the best frequency for filtering the AC noise and mantaining the 
resolution of the signal in our setup 
"""
b, a = signal.butter(N=4, Wn=40, fs=fsamp, btype="lowpass")
refsig[0] = signal.filtfilt(b, a, refsig[0]) # Use filtfilt for Zero-lag filtering

""" 
# Notch filter

fs = 1000.0  # Sample frequency (Hz)
f0 = 50.0  # Frequency to be removed from signal (Hz)
Q = 30.0  # Quality factor

# Design notch filter
b, a = signal.iirnotch(f0, Q, fs)

y = signal.filtfilt(b, a, refsig[0])

plt.plot(y)
plt.show()
print("plot y") 
"""



# Main function to call for the analysis, to show the plot and input the points of interest
def showselect(title, nclic, filename=filename, refsig=refsig):
    # Visualise and select the points
    fig = plt.figure(num=filename)
    fig.canvas.manager.full_screen_toggle() # toggle fullscreen mode
    plt.plot(refsig)
    plt.xlabel("Time (Samples)")
    plt.ylabel("MViF (N)")
    plt.title(title, fontweight ="bold")
    ginput_res = plt.ginput(n=-1, timeout=0, mouse_add=None)

    # Clear the plot to avoid seeing the old plot in the subsequent calls
    plt.close()
    
    # Check if the user entered the correct number of clics
    if nclic != len(ginput_res):
        raise Exception("Wrong number of inputs, read the title")
    
    # Act according to the number of clics
    if nclic == 2:
    # Sort the input range
        if ginput_res[0][0] < ginput_res[1][0]:
            start_point = round(ginput_res[0][0])
            end_point = round(ginput_res[1][0])
        else:
            start_point = round(ginput_res[1][0])
            end_point = round(ginput_res[0][0])
        
        return start_point, end_point
    
    elif nclic == 1:
        start_point = round(ginput_res[0][0])
        
        return start_point
    
    elif nclic ==4:
        points = [ginput_res[0][0], ginput_res[1][0], ginput_res[2][0], ginput_res[3][0]]
        # Sort the input range
        points.sort()
        
        start_point_tw = round(points[0])
        end_point_tw = round(points[1])
        start_point_rest = round(points[2])
        end_point_rest = round(points[3])
        
        return start_point_tw, end_point_tw, start_point_rest, end_point_rest



# start_point, end_point only consider the x axes (samples)
# MViF area
title = "Select start/end area for MVC then press enter"
start_point_mvif, end_point_mvif = showselect(title = title, nclic=2)
# MViF is calculated after removing the signal offset
# Offset is identified by the starting point of TTP63

# TTP area
title = "Select the start for Time to Peak then press enter"
start_point_ttp = showselect(title = title, nclic=1)

# Remove offset based on the TTP63 start point
refsig[0] = refsig[0] - refsig[0].iloc[start_point_ttp]

# MViF
mvif = max(refsig[0].iloc[start_point_mvif : end_point_mvif])
#print(f"\nMViF is: {round(mvif,2)} N\n")

# TTP63
n_at_63 = mvif*0.63 # Newton at TTP63
for ind in refsig.index:
    if ind >= start_point_ttp: # For better performance, avoid accessing df values if unnecessary
        if refsig[0].iloc[ind] >= n_at_63:
            end_point = ind
            break
ttp63 = (end_point - start_point_ttp) / fsamp * 1000

# RFD 50, 100, 150, 200
def rfd(ms, fsamp=fsamp):
    ms_insamples = round((ms * fsamp) / 1000)
    
    n_0 = refsig[0].iloc[start_point_ttp]
    n_next = refsig[0].iloc[start_point_ttp + ms_insamples]
    
    rfdval = (n_next - n_0) / (ms/1000) # (ms/1000 to convert mSec in Sec)
    
    return rfdval

rfd50 = rfd(50)
rfd100 = rfd(100)
rfd150 = rfd(150)
rfd200 = rfd(200)

# Activation capacity
""" 
Activation capacity = (1 - (A/B)) * 100
where A represents the superimposed twitch and B the control twitch at rest. """

# AC area
title = "Select 4 points, before/after superimposed and resting twitch then press enter"
start_point_tw, end_point_tw, start_point_rest, end_point_rest = showselect(title = title, nclic=4)

max_a = max(refsig[0].iloc[start_point_tw : end_point_tw])
min_a = min(refsig[0].iloc[start_point_tw : end_point_tw])
A = max_a - min_a
max_b = max(refsig[0].iloc[start_point_rest : end_point_rest])
min_b = min(refsig[0].iloc[start_point_rest : end_point_rest])
B = max_b - min_b

ac = (1 - (A/B)) * 100

# Put the results in a pandas dataframe
# Use [] to avoi the error "If using all scalar values, you must pass an index", because with [] we pass vectors and not scalars
res = {"Participant":[filename[0 : (len(filename)-4)]],
        "MViF (N)":[mvif],
        "TTP63 (mSec)":[ttp63],
        "RFD50 (N/Sec)":[rfd50], "RFD100 (N/Sec)":[rfd100], "RFD150 (N/Sec)":[rfd150], "RFD200 (N/Sec)":[rfd200],
        "AC (%)":[ac]}

# Save the results

res = pd.DataFrame(res)
res = round(res, 2)

print()
print(res)
print()

# Save everything to csv in the same directory of the files
res.to_csv("{}{}".format(location, "\\Risultati AC.csv"))

# Open it
time.sleep(1)
os.startfile("{}{}".format(location, "\\Risultati AC.csv"))