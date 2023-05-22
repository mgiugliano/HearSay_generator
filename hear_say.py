#
# Hear-Say CW-training audio files (MP3) generator
#
# May 21st 2023, Michele Giugliano, PhD
#
# This script loads a series of WAV files, and generates a single MP3 file, composed of a (random) sequence of the original files,
# alternating CW character sounds and voice cues, with a desired pause in between. Note that the "primitive" audio files,
# generated using generate_primitive_WAV_files.sh bash script, have been already trimmed to remove unnecessary silence at the beginning
# and at the end of the files. The output MP3 file can be used for CW training, using the "hear-say" method, i.e. listening to the
# CW character sound, and then repeating it aloud. The pause duration between characters can be set by the user, as well as the
# number of repetitions of the random sequence of characters. The output MP3 file is saved in the current directory, with the name
#
# Usage: python hear_say.py
# Note: change 'pause_duration' and 'n_repetitions' variables to set the desired pause duration (in seconds) between characters, and
# the number of repetitions of the random sequence of characters, respectively.
#
# Note: the script requires the following Python packages: numpy, tqdm, scipy, pydub
#

# MIT License (MIT)

import os
#from posix import waitpid       # for file handling
import sys                      # for command line arguments
import numpy as np              # for array handling
from tqdm import tqdm           # for progress bar
import scipy.io.wavfile as wav  # for reading wav files
from pydub import AudioSegment  # for saving mp3 files

# Global variables
pause_duration = 0.5          # Pause duration (in seconds) between characters (and voice cues)
n_repetitions = 2000            # Number of repetitions of the random sequence of characters (NOTE: it taje 25 min to generate 2000 repetitions of 0.5s pause)

input_dir = './primitives/'   # Input directory, where "primtive" audio files are stored
output_dir = './'             # Output directory, where the generated audio files will be stored
output_file = 'hear_say.wav'  # Output file name


#--------------------------------------------------------------------------------------------------------------------------
# Character dictionary
char_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3',
                '4', '5', '6', '7', '8', '9', 'slash']

# File handling and loading...
cw_data = {}                    # Load in memory the content of the CW audio files (as a dictionary of numpy arrays)
for char in char_list:          # Loop over the characters...
    cw_data[char] = wav.read(input_dir + char + '.wav')[1]

voice_cues = {}                 # Load in memory the content of the voice cues (as a dictionary of numpy arrays)
for char in char_list:          # Loop over the characters...
    voice_cues[char] = wav.read(input_dir + 'v_' + char + '.wav')[1]

fs = wav.read(input_dir + char_list[0] + '.wav')[0] # Sampling frequency (Hz)
#--------------------------------------------------------------------------------------------------------------------------

# Core routine: generate the output audio file, randomly selecting the characters and the pauses...
# Declare output_array as a numpy array dtype=int16
output_array = np.array([], dtype=np.int16)
#output_array = np.array([])

# Set the output volume level (between 0 and 1) - WATCH OUT.
output_volume = 1. #0.00001

print("Generating the output audio file...")

for i in tqdm (range (n_repetitions), desc="Generating..."):
#for i in range(n_repetitions):                                      # Loop over the desired number of repetitions
    char = char_list[np.random.randint(0, len(char_list))]          # Random character generated

    # Append the corresponding character sound and voice cue to the output array, with the desired volume
    output_array = np.append(output_array, output_volume   * cw_data[char])
    output_array = np.append(output_array, np.zeros(int(fs * pause_duration)))
    #output_array = np.append(output_array, output_volume   * voice_cues[char])
T = len(output_array) / fs
print("Done! " + str(T) + " s [i.e. " + str(T/60.) + "min] of audio generated.")

#print("Saving on disk the output audio file as wav...")
#wav.write(output_dir + output_file, fs, output_array.astype(np.int16))  # Let's write on disk the output wav file
#print("Done!")

print("Saving on disk the output audio file as mp3...")
rawdata = output_array.astype(np.int16)
rawdata = rawdata.tobytes('F')    # was F The same using 'C' or none
sound = AudioSegment(data=rawdata, sample_width=2, frame_rate=fs, channels=1)
sound.export('hear_say' + str(pause_duration) + '.mp3', format='mp3')#, bitrate="128k")




