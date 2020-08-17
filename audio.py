import pyaudio
import numpy as np
import wave

song = wave.open('song.wav', 'r')
CHUNK = 1024 # number of data points to read at a time
RATE = 44100 # time resolution of the recording device (Hz)

p=pyaudio.PyAudio() # start the PyAudio class
stream=p.open(
    format=p.get_format_from_width(song.getsampwidth()),
    channels=song.getnchannels(),
    rate=song.getframerate(),
    output=True,
    input=True
    )

data = song.readframes(CHUNK)
npdata = np.frombuffer(data, dtype=np.int16)

print(len(npdata))

while data != b'':
    npdata = np.frombuffer(data, dtype=np.int16)
    peak = np.average(np.abs(npdata)) * 2
    bars="#"*int(peak/2000)
    print(f'{int(peak)} {bars}')
    stream.write(data)
    data = song.readframes(CHUNK)

# close the stream gracefully
stream.stop_stream()
stream.close()
p.terminate()