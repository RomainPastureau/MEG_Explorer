import tkinter as tk
from tkinter import filedialog
import ctypes
import mne
from mne.preprocessing import find_bad_channels_maxwell as fbcm
from pathlib import Path
from psutil._common import bytes2human
from datetime import datetime as dt
import os.path as op

def get_readable_filesize(text_file: Path):
    return bytes2human(text_file.stat().st_size)

# Message box
def message_box(title, text, style):
    """Creates a message box"""
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

root = tk.Tk()
root.withdraw()

mne.set_config("MNE_BROWSER_BACKEND", "qt")

def preprocess_data():
    # FIF file
    print("1/3: Asking for the first FIF file")
    message_box('Step 1 of 3',
                'First, select the first FIF file containing your data. Click on OK to open the browser.', 0)
    path_fif = filedialog.askopenfilename(parent=root, title="Select the first FIF file containing your data",
                                          filetypes=[("FIF file", "*.fif")])

    # Crosstalk file
    print("2/3: Asking for the crosstalk file")
    message_box('Step 2 of 3', 'Next, select the crosstalk file. It should start with "ct_sparse".', 0)
    path_ct = filedialog.askopenfilename(parent=root, title="Select the crosstalk file, starting with ct_sparse",
                                         filetypes=[("FIF file", "*.fif")])

    # Calibration file
    print("3/3: Asking for the calibration file")
    message_box('Step 3 of 3', 'Finally, select the calibration file. It should start with "sss_cal."', 0)
    path_cal = filedialog.askopenfilename(parent=root, title="Select the calibration file, starting with sss",
                                          filetypes=[("DAT file", "*.dat")])

    time_begin = dt.now()

    # Read FIF
    print("Reading the FIF file")
    time_before = dt.now()
    raw_fif = mne.io.read_raw_fif(path_fif, preload=False, verbose=False)
    print(f"Step performed in {dt.now() - time_before}")

    # Calculate the size
    size = 0
    for file in raw_fif._filenames:
        size += Path(file).stat().st_size

    # Get automatic bad channels
    print("Detecting the bad channels")
    time_before = dt.now()
    auto_noisy_channels, auto_flat_channels, auto_scores = fbcm(raw_fif, cross_talk=path_ct, calibration=path_cal,
                                                                return_scores=True, duration=30, min_count=10,
                                                                verbose=False)
    raw_fif.info['bads'] = auto_noisy_channels + auto_flat_channels
    print(f"Step performed in {dt.now() - time_before}")

    # Compute head positions
    print("Computing the cHPI amplitudes")
    time_before = dt.now()
    chpi_amplitudes = mne.chpi.compute_chpi_amplitudes(raw_fif, t_window=0.5, t_step_min=0.1, verbose=False)
    print(f"Step performed in {dt.now() - time_before}")
    
    print("Computing the cHPI positions")
    time_before = dt.now()
    chpi_locs = mne.chpi.compute_chpi_locs(raw_fif.info, chpi_amplitudes, verbose=False)
    print(f"Step performed in {dt.now() - time_before}")
    del chpi_amplitudes
    
    print("Computing the head positions")
    time_before = dt.now()
    head_pos = mne.chpi.compute_head_pos(raw_fif.info, chpi_locs, verbose=False)
    del chpi_locs
    print(f"Step performed in {dt.now() - time_before}")

    # Maxwell filter
    print("Applying the Maxwell filter")
    time_before = dt.now()
    raw_sss = mne.preprocessing.maxwell_filter(raw_fif, cross_talk=path_ct, calibration=path_cal, head_pos=head_pos,
                                               st_duration=10, st_correlation=0.98, verbose=False)
    del head_pos
    del raw_fif
    print(f"Step performed in {dt.now() - time_before}")

    print("Filtering the data")
    time_before = dt.now()
    raw_filtered = raw_sss.filter(l_freq=0.01, h_freq=120, picks='meg', phase='zero-double', n_jobs=6, verbose=False)
    print(f"Step performed in {dt.now() - time_before}")

    print(f"Full pre-processing performed in {dt.now() - time_before}")

    print("Saving the data")

    result = message_box('Saving the data',
                f'Do you want to save the preprocessed data? If you do, you need approximately {bytes2human(size)} of '
                f'free space', 4)
    if result == 6:
        time_before = dt.now()
        path_output = filedialog.askdirectory(parent=root, title="Select the first FIF file containing your data")
        raw_filtered.save(op.join(path_output, path_fif.split("/")[-1][:-4] + "_preprocessed.fif"), overwrite=True, verbose=False)
        print(f"Step performed in {dt.now() - time_before}")

    return raw_filtered

def choose_data_to_plot():
    # FIF file
    print("Asking for the first FIF file")
    message_box('Locate the data',
                'Please select the first FIF file containing your data. Click on OK to open the browser.', 0)
    path_fif = filedialog.askopenfilename(parent=root, title="Select the first FIF file containing your data",
                                          filetypes=[("FIF file", "*.fif")])

    # Read FIF
    print("Reading the FIF file")
    time_before = dt.now()
    raw_fif = mne.io.read_raw_fif(path_fif, preload=False, verbose=False)
    print(f"Step performed in {dt.now() - time_before}")

    return raw_fif

# Plot
def plot_data(data):
    print("Plotting the data")
    data.plot(theme="light")

if __name__ == "__main__":
    # Select if to pre-process or no
    result = message_box("What do you want to do?", "Do you want to preprocess the data first?", 3)
    if result == 6:  # Yes
        print("Preprocessing the data")
        data = preprocess_data()
        plot_data(data)
    elif result == 7:  # No
        print("Plotting the data")
        data = choose_data_to_plot()
        plot_data(data)
    elif result == 2: # Cancel
        print("User pressed cancel: program aborted.")
