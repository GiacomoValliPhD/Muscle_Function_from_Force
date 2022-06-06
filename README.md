# Muscle_Function_from_Force
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

The user only needs to run the script and read the instructions in the interactive figures

The script automatically filters the signal from noise caused by the alternate current
with a low-pass, fourth order, Zero-lag Butterworth filter.

Instructions on what to do can be found in the plots' titles

To work with the plots:
    - Any letter of the keyboard adds a point
    - Mouse right click deletes the point
    - Enter terminates the task (press it once all the points have been selected)
    - You can zoom-in the plot after pressing the magnifier icon
    - Press home to restore the original view

If you use the script for different purposes, please double check the results.