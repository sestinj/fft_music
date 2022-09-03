from numpy import fft
import numpy as np
import matplotlib.pyplot as plt
import wave, struct, random, simpleaudio
from time import time
from math import *

sampleRate = 44100.0 # hertz
maxVolume = 32767.0

sampleDuration = 2 #seconds
frames = sampleRate*sampleDuration

n = int(frames) # Number of data points
x = np.arange(0,n)

def play(T, freq, ampfunc=lambda x: 1.0, freqfunc=lambda x: 1.0, duration=2.0):
    #shift to primary frequency
    centroid = np.mean(T*np.arange(T.shape[0]))/np.mean(T)
    shift = int(freq - centroid)
    if shift > 0:
        shiftedT = np.concatenate((np.zeros(shift), T[:n-shift]))
    elif shift < 0:
        shift = abs(shift)
        shiftedT = np.concatenate((T[shift:], np.zeros(shift)))
    else:
        shiftedT = T

    inv_fft = maxVolume*fft.ifft(shiftedT)
    
    #initialize writer
    obj = wave.open('sound.wav','w')
    obj.setnchannels(1)
    obj.setsampwidth(2)
    obj.setframerate(sampleRate)

    #write to file
    for time in range(int(sampleRate*duration)):
        value = inv_fft[time%n]
        value *= ampfunc(time%n)
        data = struct.pack('<h', int(max(0.0, min(maxVolume, value))))
        obj.writeframesraw(data)

    #close writer and play file
    obj.close()
    sound = simpleaudio.WaveObject.from_wave_file("sound.wav")
    play = sound.play()
    play.wait_done()

while True:
    print("<<NEW TIMBRE>>")
    print("-")
    T = np.zeros(n)
    freqs = []
    while True:
        freq = min(n, int(input("FREQ: ")))
        if freq == 0.0: break
        amp = min(1.0, float(input("AMP: ")))
        if amp == 0.0: break
        freqs.append(int(float(n)/freq))
        T[freq] = amp*maxVolume
        print("-")

    inv_fft = fft.ifft(T)

    plt.plot(x, inv_fft)
    plt.title("Waveform")
    plt.xlabel("Time or distance")
    plt.ylabel("Amplitude")

    plt.xlim(0, np.lcm.reduce(freqs))
    
    plt.show()

    while True:
        print("<New note>")
        freq = float(input("FREQ: "))
        ampfunc = input("AMPFUNC: ")
        freqfunc = input("FREQFUNC: ")
        if ampfunc.strip() == "":
            ampfunc = lambda x: 1.0 #These are coefficients as a function of time (x)
        else:
            exec("ampfunc = lambda x: " + ampfunc)
        if freqfunc.strip() == "":
            freqfunc = lambda x: 1.0
        else:
            exec("freqfunc = lambda x: " + freqfunc)
        
        pattern = int(input("PATTERN: "))
        if pattern == 1:
            play(T, freq, ampfunc, freqfunc, 0.25)
            play(T, freq, ampfunc, freqfunc, 0.25)
        else:
            play(T, freq, ampfunc, freqfunc, 4.0)

        if not input("Play Another? ").lower() in ["yes", "y"]:
            break