# Stereo Oscilloscope Art
A stereo oscilloscope is used to visualize 2 channels of an audio file. The sound being played by your right speaker is plotted on the x axis and by the left--on the y axis (or vice versa).

If carefully designed, an audio file can draw an image on a stereo oscilloscope.

The scripts in this repository take in an arbitrary image or video as well as an arbitrary audio track and output a .wav audio file that attempts to play the given audio track while drawing the image/video when displayed on a stereo oscilloscope.

## Use Guide
The repository includes four Jupyter Notebooks for working with different inputs types:

| Notebook | Audio Input | Image/Video Input |
| --- | --- | --- |
| `midi-image` | MIDI (tested with type 1 and 2) | Image (tested with .jpg and .png) |
| `midi-video` | MIDI (tested with type 1 and 2) | Video (tested with .mp4) |
| `wav-image` | .wav | Image (tested with .jpg and .png) |
| `wav-video` | .wav | Video (tested with .mp4) |

All notebooks write a .wav file (by default into the Samples directory) which plays the input audio and draws the input image/video when displayed on a stereo oscilloscope.

The scripts use python 3.11.5. To download the required packages, run `pip install -r requirements.txt`

## Limitations

### Chords
The output audio can play at most 2 notes simultaneously--1 note is played by the oscilloscope image and the other is played by a square wave added to the image. Adding a square wave merely duplicates the image, while adding anything else would result in distortion.

In principle, arbitrary 2-tone audio can be represented as a weighted sum of two sinusoids, which can be approximated as a signal with an oscillating amplitude (see [appendix](#appendix-weighted-sum-of-sines)). However the oscilloscope drawing in its current form is not a good approximation of a sinusoid so this method does not work.

Additionally, since the audio values must draw a specific shape, any volume information is lost.

### MIDI Input
Since the output is limited to playing 2 notes, the script will only take 1 note at a time from each MIDI track. If 2 notes are played simultaneously in a MIDI track, the script will only take whichever note is first in the file. For best results, **input MIDI files should be formatted so that only one note is played at a time in each channel.**

### Wav Input
Reading audio from a wav file is suboptimal as the script needs to know note frequencies rather than the raw audio data to play the correct pitches. I approach the issue of extracting frequencies from raw audio data by scanning through the data one window (some small range of samples) at a time, taking the Fourier transform of each window, and retrieving the 2 highest peaks. This is implemented in `wav_io.py`

For this method to produce palatable results, you typically must play at least the two most prominent frequencies. This produces a recognizable but very noisy reproduction of the audio. **It is thus recommended to use a properly formatted MIDI file instead.**

## How It Works

### 1. Extracting Contours
We want to minimize the number of points the oscilloscope must draw to recreate an image, so we focus on just the image contours. Additionally, to maintain the illusion of a consistent image the oscilloscope must be made to trace out the outlines rather than jumping around from point to point. We must therefore begin by extracting the outlines/contours of an image.

This is done using a variation of the marching squares algorithm. In the process of identifying edge segments, the algorithm maintains a list of conotours and adds each new edge segment to the endpoint of the conotour that the segment is part of. Afterwards, the algorithm joins the contours with matching endpoints. The end result is a list of contours, each of which takes the form of a list of vertices that sequntially trace the contour end-to-end. This entire process is implemented in `contour.py`

`contour.py` also includes the function `contour_to_f`, which converts a given contour to a piecewise complex function with period 1, whose real part corresponds to the x coordinate and imagniary part to the y coordinate. This is done to make notation and interpolation simpler and can be used to analyze via Fourier transforms the sound produced when the contour coordinates are converted to audio.

### 2. Playing Sound with Contours
An image can be drawn on an oscilloscope by going through each of its contours and writing the x coordinate to the first audio channel and the y coordinate to the second audio channel.

It turns out that the human ear interprets virtually anything periodic as a pitch. To play a note with frequency $`f`$, it is therefore sufficient to ensure that the drawings of our image have period $`\frac{1}{f}`$. In other words, if the sample rate of our output audio file is $`r`$, we take a total of $`\frac{r}{f}`$ equally spaced points along the image contours and write them to the audio file as before (x coordinate to the first channel, and y coordinate to the second).

`oscilloscope.py` contains an `OscilloscopeDrawer` class which implements these methods.

### 3. Playing a Chord
It would be nice to be able to play at least 2 notes simultaneously, especially when our frequencies are estimated from raw audio data. Moreoever, we must do so while preserving the relative shape of the audio so that it still draws a recognizable image.

A simple way to add a second tone without distorting our image is to play it using a simple square wave. A square wave merely jumps between a positive and negative value on both channels so, when added to the oscilloscope drawing, it changes only its the midpoint. This results in the image being duplicated in the top left and bottom right corners of the oscilloscope (though the corners can be changed by altering the phase of the square waves on both channels). It is noteable that if the frequencies of the image and square wave happen to match, only complementary parts of the image may be drawn in each of the corners--this however only happens rarely.

The `OscilloscopeDrawer` class in `oscilloscope.py` contains the function `play_square_wave` for creating a simple square wave.

Another theoretical approach to playing two tones might be by modulating the amplitude by chosing which contours to play and omit based on their average amplitude. The contours, however, are not good approximations of sinusoidal waves, so using this method with the approximation in the [appendix](#appendix-weighted-sum-of-sines) does not work. Perhaps ordering the contours in a more sophisticated way can be used to address this in the future.

## Appendix: Weighted Sum of Sines
It can be shown geometrically that
```math
a\sin(\theta)+b\sin(\phi) = c\sin(\theta+\chi)
```
where $`c^2 = a^2 + b^2 + 2ab\cos(\alpha)`$, $`\sin(\chi) = \frac{b}{c}\sin(\alpha)`$, and $`\alpha = \phi-\theta`$.

If $`\theta`$ and $`\phi`$ correspond to the first and second most prominent frequencies given by the Fourier transform in that order, we can usually assume that b<<a, meaning b<<c. Note that this assumption is based only on qualitative observations and has some exceptions.

That b is much smaller than c implies that $`\chi`$ is small, more specifically that $`\chi<<\theta`$. Thus, we can approximate the weighted sum of sines as a signal of the more prominent frequency with amplitude modulated by c--that is
```math
a\sin(\theta)+b\sin(\phi) \approx c\sin(\theta)
```

If we assume $`a^2 + b^2 >> 2ab`$, by the first order Taylor approximation we have
```math
c \approx \sqrt{a^2+b^2}\left( 1+\frac{ab}{a^2+b^2}\cos(\alpha) \right)
```

Thus, when two tones have frequencies $`f_1`$ and $`f_2`$, where $`\theta(t)=2 \pi f_1 t`$ and $`\phi(t)=2 \pi f_2 t`$, their combined chord can be represented as signal of frequency $`f_1`$ with amplitude oscillating at a frequency of $`f_2-f_1`$ around the value $`\sqrt{a^2+b^2}`$.

This approximation seems to qualitatively hold well enough. Though it is not currently used in the project, it might be of use in the future.