import numpy as np
from scipy.io import wavfile
from contour import contour_to_f

# A class for creating oscilloscope drawings
class OscilloscopeDrawer:
    def __init__(self, img_shape, rate=48000, data_type=np.int16, save_path='.'):
        self.Y = img_shape[0]
        self.X = img_shape[1]
        self.rate = rate
        self.save_path = save_path
        
        self.set_data_type(data_type)
    
    def set_data_type(self, data_type):
        self.data_type = data_type
        self.amp = np.iinfo(data_type).max

    # Write x and y channels to a stereo wav file
    def write_wav(self, x, y, name, save_path=None, data_type=None, rate=None):
        if save_path == None:
            save_path = self.save_path
        if data_type == None:
            data_type = self.data_type
        if rate == None:
            rate = self.rate
        
        data = np.vstack((x, y)).transpose().astype(data_type)

        wavfile.write(f"{save_path}/{name}.wav", rate, data)

    # Create oscilloscope drawing that plays a given frequency
    def play_drawing(self, freq, contours, X=None, Y=None):
        if X==None:
            X = self.X
        if Y==None:
            Y = self.Y
        
        x_drawing, y_drawing = np.array([]), np.array([])

        contour_combined_size = sum([len(c) for c in contours])
        num_frames = self.rate/freq
        for contour in contours:
            n_frames = int(num_frames*len(contour)/contour_combined_size)

            if n_frames == 0:
                continue

            t = np.linspace(0, 1, n_frames)
            vals = contour_to_f(contour)(t)

            x_drawing = np.append(x_drawing, np.real(vals)*2*self.amp/X)
            y_drawing = np.append(y_drawing, np.imag(vals)*2*self.amp/Y)

        extra_frames_needed = round(num_frames) - x_drawing.size
        x_drawing = np.append(x_drawing, x_drawing[:-extra_frames_needed:-1])
        y_drawing = np.append(y_drawing, y_drawing[:-extra_frames_needed:-1])
        
        return x_drawing, y_drawing
    
    # Play the given tones using a square wave
    def play_square_wave(self, durations, freqs):
        square_wave = np.array([])
        
        for duration, freq in zip(durations, freqs):
            if freq == 0:
                square_wave = np.append(square_wave, np.zeros(int(duration*self.rate)))
                continue

            # Create oscilloscope drawing
            num_frames = int(self.rate/freq/4)
            square = np.append(np.ones(num_frames), -np.ones(num_frames))*self.amp/2

            # Concatenate oscilloscope drawings for duration
            num_frames = int(duration*self.rate)
            num_drawings = int(num_frames/square.size)+1

            square = np.concatenate([square]*num_drawings)[:num_frames]

            square_wave = np.append(square_wave, square)
        
        return square_wave