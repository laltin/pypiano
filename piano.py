import math
import numpy
import pyaudio
import Tkinter


CHANNELS   = 1
SAMP_RATE  = 44100
CHUNK_SIZE = 1024
NOTE_TIME  = 4.0

WAVE_SAMPLES    = int(SAMP_RATE * NOTE_TIME)
SOUND_BUFFER    = []
NOTE_WAVEFORMS  = {}
NOTE_FREQS      = { "a":261.6, 
                    "w":277.2,
                    "s":293.7, 
                    "e":311.1,
                    "d":329.6, 
                    "f":349.2,
                    "t":367.0,
                    "g":392.0, 
                    "y":415.3,
                    "h":440.0,
                    "u":466.2,
                    "j":493.9, 
                    "k":523.3, 
                    "l":587.3, 
                    ";":659.3, 
                    "'":698.5 }
LONG_NOTE_FREQS = { "A":261.6, 
                    "W":277.2,
                    "S":293.7, 
                    "E":311.1,
                    "D":329.6, 
                    "F":349.2,
                    "T":367.0,
                    "G":392.0, 
                    "Y":415.3,
                    "H":440.0,
                    "U":466.2,
                    "J":493.9, 
                    "K":523.3, 
                    "L":587.3, 
                    ":":659.3, 
                    "\"":698.5 }


def amplitude_decay (time):
    return 0.12 * (1-math.exp(-50*time)) * math.exp(-5*time)

def amplitude_decay_long (time):
    return 0.10 * (1-math.exp(-50*time)) * math.exp(-1.5*time)


def sine_wave (frequency, amplitude, reduce=1.0):
    '''
    create a sine wave generator. number of generated samples = WAVE_SAMPLES
    amplitude is a function of time
    '''
    for i in xrange(WAVE_SAMPLES):
        time = float(i) / float(SAMP_RATE)
        yield reduce * amplitude(time) * \
            math.sin(2.0 * math.pi * float(frequency) * time)


def callback (in_data, frame_count, time_info, status):
    window = numpy.zeros(CHUNK_SIZE)
    
    for i, s in enumerate(SOUND_BUFFER):
        try:
            # first element of list is used as offset for where we left
            offset = s[0]
            data = s[offset:offset + CHUNK_SIZE]
            
            s[0] += CHUNK_SIZE
            if s[0] > WAVE_SAMPLES:
                raise StopIteration
            
            # old implementation with generators:
            #data = numpy.array( [s.next() for x in xrange(CHUNK_SIZE)] )
                
        except StopIteration:
            # nothing left to play in buffer, remove current sound
            SOUND_BUFFER.pop(i)
            continue
        
        window = numpy.add(window, data)
    
    data = numpy.around(32767 * window)
    data = numpy.array(data, dtype=numpy.int16)
    return ( data.tostring(), pyaudio.paContinue )
    

def onkeypress (event):
    ch = event.char
    if ch not in NOTE_WAVEFORMS:
        return
        
    # first element of array in sound buffer is offset, so notes will start from
    # second element. for that reason offset value should be 1
    SOUND_BUFFER.append(numpy.insert( NOTE_WAVEFORMS[ch], 0, 1 ))
    

if __name__ == "__main__":
    # precalculate all note samples
    for note in NOTE_FREQS:
        freq = NOTE_FREQS[note]
        
        # harmonics of a piano note. based on C4
        s = numpy.array( list( sine_wave(1*freq, amplitude_decay) ) )
        s = numpy.add(s, list( sine_wave(2*freq, amplitude_decay, reduce=0.52)   ) )
        s = numpy.add(s, list( sine_wave(3*freq, amplitude_decay, reduce=0.033)  ) )
        s = numpy.add(s, list( sine_wave(4*freq, amplitude_decay, reduce=0.033)  ) )
        s = numpy.add(s, list( sine_wave(5*freq, amplitude_decay, reduce=0.0165) ) )
        s = numpy.add(s, list( sine_wave(6*freq, amplitude_decay, reduce=0.0263) ) )
        s = numpy.add(s, list( sine_wave(7*freq, amplitude_decay, reduce=0.052)  ) )
        
        NOTE_WAVEFORMS[note] = s
        
    # precalculate long note samples
    for note in LONG_NOTE_FREQS:
        freq = LONG_NOTE_FREQS[note]
        
        # harmonics of a piano note. based on C4
        s = numpy.array( list( sine_wave(1*freq, amplitude_decay_long) ) )
        s = numpy.add(s, list( sine_wave(2*freq, amplitude_decay_long, reduce=0.52)   ) )
        s = numpy.add(s, list( sine_wave(3*freq, amplitude_decay_long, reduce=0.033)  ) )
        s = numpy.add(s, list( sine_wave(4*freq, amplitude_decay_long, reduce=0.033)  ) )
        s = numpy.add(s, list( sine_wave(5*freq, amplitude_decay_long, reduce=0.0165) ) )
        s = numpy.add(s, list( sine_wave(6*freq, amplitude_decay_long, reduce=0.0263) ) )
        s = numpy.add(s, list( sine_wave(7*freq, amplitude_decay_long, reduce=0.052)  ) )
        
        NOTE_WAVEFORMS[note] = s
        
    # start audio & ui for detecting keypress
    p = pyaudio.PyAudio()
    
    stream = p.open(format=p.get_format_from_width(2),
                    channels=CHANNELS,
                    rate=SAMP_RATE,
                    output=True,
                    frames_per_buffer=CHUNK_SIZE,
                    stream_callback=callback)

    stream.start_stream()

    root = Tkinter.Tk()
    root.title("Music")
    root.geometry("400x100")
    root.bind("<KeyPress>", onkeypress)
    root.mainloop()

    stream.stop_stream()
    stream.close()
