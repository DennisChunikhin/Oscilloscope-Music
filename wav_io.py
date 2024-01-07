import numpy as np
import numpy.fft as fft

from scipy.signal import find_peaks
from scipy.io import wavfile

# Write stereo wav file
def write_wav(x, y, name, rate=48000, save_path='.', data_type=np.int16):
    data = np.vstack((x, y)).transpose().astype(data_type)

    wavfile.write(f"{save_path}/{name}.wav", rate, data)

# Extract frequencies from sound data using the fourier transform
def get_freqs(data, sampling_rate, distance=10):
    ft = fft.rfft(data)
    vals = np.abs(ft)
    freqs = fft.rfftfreq(len(data), d=1/sampling_rate)
    
    peaks, peak_dict = find_peaks(np.abs(vals), height=0.001, distance=distance) # Check whether finding peaks of vals or of np.abs(vals) is better--likely no difference
    
    indices = np.argsort(peak_dict['peak_heights'])
    p = peaks[indices]
    
    return freqs[p], ft[p]

# Scan through a wav file and extract the frequencies and value using the fourier transform
def freqs_from_wav(wav_data, sampling_rate, scan_window_size=1000, num_freqs=2, distance=10):
    target_freqs = []
    target_vals = []

    for i in range(len(wav_data)//scan_window_size-1):
        start = scan_window_size*i
        end = scan_window_size*(i+1)

        freqs = np.zeros(num_freqs)
        vals = np.zeros(num_freqs)

        data = wav_data[start:end]
        if np.any(data):
            freqs, vals = get_freqs(data, sampling_rate, distance=distance)

            # Take the largest amplitude peaks
            freqs = freqs[-num_freqs:]
            vals = np.abs(vals[-num_freqs:])

            freqs = np.pad(freqs, (0, num_freqs-freqs.size))
            vals = np.pad(vals, (0, num_freqs-vals.size))

            # Normalize peak values
            s = np.sum(np.abs(vals))
            if s != 0:
                vals = vals/s

        target_freqs.append(freqs)
        target_vals.append(vals)

    return np.array(target_freqs), np.array(target_vals)

# interpolate_mode remove means replace with a rest, replace means replace with previous frequency
def process_freqs(freqs, scan_window_size, sample_rate, interpolate_mode='remove', min_freq=20, max_freq=20000, min_fractional_dist=0.002):
    note_freqs = [0]
    note_durations = [0]
    
    delta_t = scan_window_size/sample_rate
    
    for i, freq in enumerate(freqs):
        # Note outside of acceptable frequency range
        if freq < min_freq or freq > max_freq:
            if interpolate_mode=='remove':
                # Add a rest for the note's duration
                note_freqs.append(0)
                note_durations.append(delta_t)
            elif interpolate_mode=='replace':
                # Continue the previous note for this duration
                note_durations[-1] += delta_t
            else:
                # Add the note
                note_freqs.append(freq)
                note_durations.append(delta_t)
            
        # Note close to previous note
        elif np.abs(1 - note_freqs[-1]/freq) <= min_fractional_dist:
            # Continue the previous note
            note_durations[-1] += delta_t
        
        else:
            note_freqs.append(freq)
            note_durations.append(delta_t)
    
    return note_durations, note_freqs

# Preview auido generated by fourier transform
def preview_ft_audio(freqs_list, vals_list, frame_step, rate=48000):
    data = np.array([])

    for i, (freqs, vals) in enumerate(zip(freqs_list, vals_list)):
        audio = lambda t : sum([val * np.sin(2*np.pi*freq*t) for freq, val in zip(freqs, vals)])
        
        data = np.append(data, [audio(t/rate) for t in range(i*frame_step, (i+1)*frame_step)])

    return data

# Preview auido that will be played on the oscilloscope
def preview_audio(note_freqs, note_durations, rate=48000):
    data = np.array([])

    time = 0
    for freq, duration in zip(note_freqs, note_durations):
        t = np.arange(time, time+duration, 1/rate)
        data = np.append(data, np.sin(2*np.pi*freq*t))
        
        time += duration
    
    return data