#
# Hear-Say CW-training audio files (MP3) generator
#
# May 22st 2023, Michele Giugliano, PhD
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
import sys                      # for command line arguments
import numpy as np              # for array handling
from tqdm import tqdm           # for progress bar
import scipy.io.wavfile as wav  # for reading wav files
from pydub import AudioSegment  # for saving mp3 files

# Global variables
pause_duration = 0.3            # Pause duration (in seconds) between characters (and voice cues)
n_repetitions = 3000            # Number of repetitions of the random sequence of characters (NOTE: it taje 25 min to generate 2000 repetitions of 0.5s pause)
voice_cue     = 0               # If 1, voice cues are added to the output audio file; otherwise set it to 0

input_dir = './primitives/'   # Input directory, where "primtive" audio files are stored
output_dir = './output/'             # Output directory, where the generated audio files will be stored
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

# Extract the duration of each audio file (in samples)
duration_cw = {}
for char in char_list:
    duration_cw[char] = len(cw_data[char])

duration_cue = {}
for char in char_list:
    duration_cue[char] = len(voice_cues[char])

# Generate the random sequence of characters
sequence = np.random.randint(0, len(char_list), n_repetitions)

# Calculating the total duration of the output audio file (in samples)
total_duration = 0
for i in range(n_repetitions):
    total_duration += duration_cw[char_list[sequence[i]]] + int(fs * pause_duration) + voice_cue * duration_cue[char_list[sequence[i]]]

# Core routine: generate the output audio file, randomly selecting the characters and the pauses...
# Allocate the entire output_array upfront as a numpy array dtype=int16
# As opposed to append, this is orders of magnitude faster!
output_array = np.zeros(total_duration, dtype=np.int16)

# Fill the output array with the random sequence of characters
print("Generating the output audio file...")
index = 0
for i in tqdm (range (n_repetitions), desc="Generating..."):
#for i in range(n_repetitions):
    cw_dur = duration_cw[char_list[sequence[i]]]
    cue_dur = duration_cue[char_list[sequence[i]]]
    output_array[index:index + cw_dur] = cw_data[char_list[sequence[i]]]
    index += cw_dur
    output_array[index:index + int(fs * pause_duration)] = np.zeros(int(fs * pause_duration))
    index += int(fs * pause_duration)
    if voice_cue:
        output_array[index:index + cue_dur] = voice_cues[char_list[sequence[i]]]
        index += cue_dur

T = len(output_array) / fs
print("Done! " + str(T) + " s [i.e. " + str(T/60.) + "min] of audio generated.")

#print("Saving on disk the output audio file as wav...")
#wav.write(output_dir + output_file, fs, output_array.astype(np.int16))  # Let's write on disk the output wav file
#print("Done!")

if (voice_cue==1):
    fname = 'hear_say'
else:
    fname = 'hear_miss'

print("Saving on disk the output audio file as mp3...")
rawdata = output_array.astype(np.int16)
rawdata = rawdata.tobytes('F')    # was F The same using 'C' or none
sound = AudioSegment(data=rawdata, sample_width=2, frame_rate=fs, channels=1)
sound.export(output_dir + fname + str(pause_duration) + '.mp3', format='mp3')#, bitrate="128k")
