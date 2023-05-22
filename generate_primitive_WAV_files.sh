#!/bin/bash
#
# Generate "primitive" WAV files(macos version)
# Bash script - Version 0.1
#
# Requires: ebook2cw (to generate CW audio) and say (text-to-speech) - both in the path
#
# May the Morse be with you!

WPM=29 		 # (Character) speed, word per minute
TONE=650  	 # Tone frequency [Hz]
SRATE=32000  # Sampling rate [Hz]
VOICE=Moira  # This voice sounds very natural to me (try "say -v ?" to see the list of available voices)
#VOICE=Alice # This voice sounds very natural to me (Alice is in italian)
VRATE=200    # Voice rate (words per minute)

chars=abcdefghijklmnopqrstuvwxyz1234567890/   # The characters to be used (37 characters)
/bin/mkdir -p ./primitives
/bin/rm -f ./primitives/*.wav

/bin/mkdir -p ./output

echo "Generating the CW characters and voice cue WAV files - iv3ifz Michele Giugliano, PhD - 2023"
echo " "
echo "Character speed: $WPM WPM"
echo "Tone frequency: $TONE Hz"
echo "Sampling rate: $SRATE Hz"
echo "Voice: $VOICE"
echo "Voice rate: $VRATE WPM"
echo "Characters: $chars"
echo "Output directory: ./primitives"
echo " "
echo "Please wait..."
echo " "

#---------------------------------------------------------------------------------------
sp="/-\|"
sc=0
spin() {
   printf "\b${sp:sc++:1}"
   ((sc==${#sp})) && sc=0
}
endspin() {
   printf "\r%s\n" "$@"
}
#---------------------------------------------------------------------------------------

echo "Generating the CW primitive WAV files as sounds..."
# For each character in 'chars', generate a wav file containing its CW sound
NCHARS=$(( ${#chars} - 1 ))
for i in `seq 0 $NCHARS`; do
#for i in `seq 0 36`; do
    spin
    # Generate the cw waveform by ebook2cw (thanks Fabian Kurz, DJ1YFK!)
    echo ${chars:$i:1} | ebook2cw -s $SRATE -w $WPM -f $TONE -T 0 -q 9 -o cw > /dev/null

    # Let's use sox to convert the mp3 files to wav files
    if [ ${chars:$i:1} = "/" ]; then # if the character is a slash, it cannot be the name of the file
      sox cw0000.mp3 ./primitives/slash.wav rate -s -a $SRATE dither -s > /dev/null
    else
      sox cw0000.mp3 ./primitives/${chars:$i:1}.wav rate -s -a $SRATE dither -s > /dev/null
    fi
    rm cw0000.mp3 > /dev/null
done
endspin
echo "Done!"

echo "Generating the voice cue primitive WAV files as sounds..."
# Now, let's generate the audio files for the characters
# (the audio files will be named as the characters themselves)
for i in `seq 0 $NCHARS`; do
#for i in `seq 0 36`; do
    spin
    # Generate the voice synthesis cue by 'say' (thanks Apple!)
    echo [[char LTRL]] ${chars:$i:1} | say --voice=$VOICE --rate=$VRATE -o tmp.aiff

    # Let's use sox to convert the mp3 files to wav files
    if [ ${chars:$i:1} = "/" ]; then # if the character is a slash, it cannot be the name of the file
      sox tmp.aiff ./primitives/v_slash.wav rate -s -a $SRATE dither -s > /dev/null
    else
        sox tmp.aiff ./primitives/v_${chars:$i:1}.wav rate -s -a $SRATE dither -s > /dev/null
    fi
    rm tmp.aiff > /dev/null
done
endspin
echo "Done!"

echo "Removing silence at the beginning and end of the files..."
# Let's remove the silence at the beginning and end of the files
for f in ./primitives/*.wav; do
   spin
   sox ./primitives/${f##*/} ./primitives/t_${f##*/} silence 1 0.001 0.1% reverse silence 1 0.001 0.1% reverse #> /dev/null
   # trim silence (anything less than 1% volume) until we encounter sound lasting more than 0.01 seconds in duration.
done
endspin
echo "Done!"


echo "Removing the temporary files..."
# Let's remove the files whose filename does not start with "t_"
for f in ./primitives/*.wav; do
   spin
   if [[ ${f##*/} != t_* ]]; then
      rm ./primitives/${f##*/} > /dev/null
   fi
done
endspin

# Let's rename the files removing the leading two characters (i.e. "t_")
for f in ./primitives/*.wav; do
   spin
   fname=${f##*/}
    mv ./primitives/$fname ./primitives/${fname:2}
done
endspin


# Let's now convert it to mp3
