import wave, struct, random, simpleaudio
from math import e, sin, pi, cos, tan, floor
from functools import reduce
import math
import sympy as sp

def keyNum(key):
    #FORMAT: [letter][s/f][octave number] e.g. cs4 = middle c sharp
    notes = ['c', 'cs', 'd', 'ds', 'e', 'f', 'fs', 'g', 'gs', 'a', 'as', 'b']
    num = notes.index(key[0])
    if key[1] == "f": #flat
        num -= 1
        num += 12*(key[2]-4)
    elif key[1] == "s": #sharp
        num += 1
        num += 12*(key[2]-4)
    else:
        num += 12*(key[1]-4)

def keyFreq(n):
    #Middle C is key n=0
    return 261.6*2**(n/12)

def jaggedSin(x):
    if x % (2.0*pi) < pi/2.0:
        return x
    elif x % (2.0*pi) < pi*1.5:
        return 1.0 + pi/2.0 - x
    else:
        return -1 - 1.5*pi - x

def nnTimbre(v, t):
    #2, 4, 6, 6, 4, 1
    shape = [2, 4, 6, 6, 4, 1]
    weights = []
    nodeValues = []
    for i in range(len(shape)-1):
        s = shape[i]
        layer = []
        nodeValuesLayer = []
        for leftNode in range(s):
            nodeValuesLayer.append(random.random())
            weightsFromLeftNode = []
            for rightNode in range(shape[i+1]):
               weightsFromLeftNode.append(random.random())

            layer.append(weightsFromLeftNode)
        nodeValues.append(nodeValuesLayer)
        weights.append(layer)
    
    nodeValues[0] = [v, t]
    for i in range(1,len(shape)-1):
        rightNodes = shape[i]
        leftNodes = shape[i-1]
        for rightNode in range(rightNodes):
            weightedSum = 0
            for leftNode in range(leftNodes):
                weightedSum += nodeValues[i-1][leftNode]*weights[i-1][leftNode][rightNode]
            nodeValues[i][rightNode] = weightedSum
    lastLayer = 0
    for i in range(len(nodeValues[len(nodeValues)-2])):
        weight = weights[len(weights)-2][i][0]
        lastLayer += nodeValues[len(nodeValues)-2][i]*weight
    return lastLayer

def easeIn(value, t):
    noise = random.random()*t*maxVolume*0.01
    nasal = maxVolume*value*sin(t*pi)*0.5
    log = log(t+1.0)*maxVolume
    maxNormalVal = 1.0
    ease = value*t*t*maxNormalVal
    newVal = ease
    cleaned = int(max(0.0, min(maxVolume, newVal)))
    return cleaned

def loadTimbre(A):
    t, f, f0 = sp.symbols('t f f0')
    return sp.simplify(sp.simplify(sp.integrate(sp.sin(t/sampleRate*f*pi)*A(f, f0), (f, lowerBound, upperBound))/(upperBound - lowerBound)))


def defaultTimbre(value, t):
    ##f = value*min(1.0, tan(e**(0.001*t))) #video game
    ##f = value*min(1.0, tan(e**(0.0004*t))) #video game
    #f = value + value*(min(2.0, 3*sin(10*t)) + cos(20*t)) #idk
    ##f = value*max(0.1, e**(-0.0005*t))
    ##f = min(value, value*cos(0.001*t))
    theta = math.asin(value/maxVolume)
    g = value + value*sin(0.5*theta+0.1)
    return g

sampleRate = 44100.0 # hertz
maxVolume = 32767.0
defaultDuration = 0.25
lowerBound = 0
upperBound = 15000 #Bounds of integration for the frequency

def A1(f, f0): #f0 is the center frequency, so more of a parameter. This is really a function taking frequency and returning amplitude
    return maxVolume - maxVolume/10000*(f-f0)**2
    #Downfacing parabola with vertex at (f0, maxVolume) and x-intercepts at +/- 100
t1 = loadTimbre(A1)

def addNote(key, duration=defaultDuration, volume=1.0, timbre=t1):
    print("NOTE " + str(key))
    volume *= maxVolume
    frequency = keyFreq(key)
    frames = int(duration*sampleRate)
    t, f0 = sp.symbols('t f0')
    timbreExpr = sp.simplify(sp.simplify(timbre.subs({f0:frequency})))
    print("TIMBRE EXPR: \n" + str(timbreExpr))
    for time in range(frames):
        #value = int(maxVolume*sin(float(t)/sampleRate*frequency*pi))
        t = sp.symbols('t')
        value = float(timbreExpr.subs({t:time}))
        data = struct.pack('<h', int(max(0.0, min(maxVolume, value))))
        obj.writeframesraw( data )

def addChord(keys, duration=defaultDuration, volume=1.0, timbre=defaultTimbre):
    volume = min(1.0, volume)
    volume *= maxVolume/len(keys)
    frequencies = [keyFreq(key) for key in keys]
    frames = int(duration*sampleRate)
    for t in range(frames):
        total = 0
        for frequency in frequencies:
            total += int(volume*sin(float(t)/sampleRate*frequency*pi))
        data = struct.pack('<h', int(max(0.0, min(maxVolume, timbre(total, t)))))
        obj.writeframesraw(data)

obj = wave.open('sound.wav','w')
obj.setnchannels(1) # mono
obj.setsampwidth(2)
obj.setframerate(sampleRate)

addNote(0)
addNote(4)
addNote(7)
addNote(12)
addNote(7)
addNote(4)
addNote(0)
addChord([0, 4, 7, 12], 2.0)

obj.close()

sound = simpleaudio.WaveObject.from_wave_file("sound.wav")
play = sound.play()
play.wait_done()

