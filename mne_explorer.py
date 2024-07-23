import tkinter as tk
from tkinter import filedialog
import ctypes
import mne
from mne.preprocessing import find_bad_channels_maxwell as fbcm

# Message box
def message_box(title, text, style):
    """Creates a message box"""
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

# Select fif file from path
root = tk.Tk()
root.withdraw()

# FIF file
message_box('Step 1 of 3', 'First, select the first FIF file containing your data. Click on OK to open the browser.', 0)
path_fif = filedialog.askopenfilename(title="Select the first FIF file containing your data",
                                      filetypes=[("FIF file", "*.fif")])

# Crosstalk file
message_box('Step 2 of 3', 'Next, select the crosstalk file. It should start with "ct_sparse".', 0)
path_ct = filedialog.askopenfilename(title="Select the crosstalk file, starting with ct_sparse",
                                     filetypes=[("FIF file", "*.fif")])

# Calibration file
message_box('Step 3 of 3', 'Finally, select the calibration file. It should start with "sss_cal.', 0)
path_cal = filedialog.askopenfilename(title="Select the crosstalk file, starting with ct_sparse",
                                      filetypes=[("DAT file", "*.dat")])

# Read FIF
raw_fif = mne.io.read_raw_fif(path_fif, preload=False, verbose=False)

# Get automatic bad channels
auto_noisy_channels, auto_flat_channels, auto_scores = fbcm(raw_fif, cross_talk=path_ct, calibration=path_cal,
                                                            return_scores=True, duration=30, min_count=10,
                                                            verbose=False)
raw_fif.info['bads'] = auto_noisy_channels + auto_flat_channels

# Compute head positions
chpi_amplitudes = mne.chpi.compute_chpi_amplitudes(raw_fif, t_window=0.5, t_step_min=0.1, verbose=False)
chpi_locs = mne.chpi.compute_chpi_locs(raw_fif.info, chpi_amplitudes, verbose=False)
head_pos = mne.chpi.compute_head_pos(raw_fif.info, chpi_locs, verbose=False)

# Maxwell filter
raw_sss = mne.preprocessing.maxwell_filter(raw_fif, cross_talk=path_ct, calibration=path_cal, head_pos=head_pos,
                                           st_duration=10, st_correlation=0.98, verbose=False)
raw_filtered = raw_sss.copy().filter(l_freq=0.01, h_freq=120, picks='meg', phase='zero-double', n_jobs=6, verbose=False)

# Plot
raw_filtered.plot()
