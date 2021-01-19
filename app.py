import streamlit as st
import pyaudio
import time
import os
import wave
import string
from glob import glob
import shutil
import base64

FOLDER  = 'user_recordings'
SAMPLES = 2

def record(filename):
    # KWARGs
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 16_000  # Record at 44100 samples per second
    seconds=1
    
    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('A')

    stream = p.open(format=sample_format,
                        channels=2,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)

    print("B")
    frames = []  # Initialize array to store frames

    # Store data in chunks
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream 
    #stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    #p.terminate()

    print('X')
    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

st.title('Help us gather audio data!')

st.write('''We are trying to build a model that can idenify what letter of the alphabet was said
by a speaker. Please help us gather some labeled data by recording yourself saying some letters.''')

st.markdown('### Instructions')
st.write(f'When you press record, you will be asked to say each letter {SAMPLES} times')
st.write('Note that we are looking for the pronunciation of the letter, not the name.')

FOLDER = st.text_input('Please give this dataset an identifier')

button_cols = st.beta_columns(6)

with button_cols[0]:
    start=st.button('Start')
with button_cols[1]:
    stop=st.button('Stop')
with button_cols[2]:
    review=st.button('Review')
with button_cols[3]:
    save=st.button('Save')
with button_cols[4]:
    clear=st.button('Clear')
with button_cols[5]:
    download=st.button('Download')


if start:
    os.makedirs(FOLDER, exist_ok=True)

    for letter in string.ascii_uppercase:
        st.markdown(f'### {letter}''')

        time.sleep(1)
        for i in range(SAMPLES):
            col1, col2 = st.beta_columns(2)

            with col1:
                st.write('Start')

            filename = f'{FOLDER}/{letter}-{str(i+1).rjust(4, "0")}.wav'
            record(filename)
            with col2:
                st.write('Stop')
            time.sleep(1)

if review:
    files = glob(f'{FOLDER}/*.wav')

    cols = st.beta_columns(SAMPLES)

    for i, file in enumerate(files):
        with cols[i%SAMPLES] as c:
            st.write(os.path.basename(file))
            st.audio(file, format='audio/wav', start_time=0)


if save:
    zip_basename = f'{FOLDER}-{time.time():.0f}'
    shutil.make_archive(zip_basename, 'zip', FOLDER)
    st.write('Saved')

if clear:
    os.system(f'rm {FOLDER}/*')

if download:
    def get_download_link(filename)->str:
        obj = open(filename, 'rb').read()
        b64 = base64.b64encode(obj).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download Zip File</a>'
        return href

    file =  sorted(glob(f'{FOLDER}-*.zip'))[-1]
    st.markdown(get_download_link(file), unsafe_allow_html=True)



