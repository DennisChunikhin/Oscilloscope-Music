# Stereo Oscilloscope Art
A stereo oscilloscope is used to visualize 2 channels of an audio file. The sound being played by your right speaker is plotted on the x axis and by the left--on the y axis (or vice versa).

If carefully designed, an audio file can draw an image on a stereo oscilloscope.

The scripts in this repository take in an arbitrary image or video as well as an arbitrary audio track,and outputs a .wav audio file that playes the audio track while drawing the given image/video when displayed on a stereo oscilloscope.

## Use Guide
The project includes four notebooks for producing oscilloscope audio from different inputs:

| Notebook | Audio Input | Image/Video Input |
| --- | --- | --- |
| `midi-image` | MIDI (tested with type 1 and 2) | Image (tested with .jpg and .png) |
| `midi-video` | MIDI (tested with type 1 and 2) | Video (tested with .mp4) |
| `wav-image` | .wav | Image (tested with .jpg and .png) |
| `wav-video` | .wav | Video (tested with .mp4) |

All notebooks write a .wav file which plays the input audio and draws the input image/video when displayed by a stereo oscilloscope.

## Limitations

### Chords
The output audio can play at most 2 notes simultaneously--1 note is played by the image and the other is played by a square wave added to the image. Adding a square wave merely duplicates the image, however adding anything else would result in further distortion.

In principle, the audio can be represented as a weighted sum of two sinusoids, which can be approximated as a signal with an oscillating amplitude (see [appendix](#appendix-weighted-sum-of-sines)). However this approximation does not work with this project's way of creating oscilloscope drawings.

Additionally, since the audio must draw a predetermined shape, any volume information is lost.

### MIDI Input
Since the output is limited to playing 2 tracks, the script will only take 1 note at a time from each MIDI track. If 2 notes are played simultaneously, the script will only take whichever note is first in the file. For best results, **input MIDI files should be formatted so that only one note is played at a time in each channel.**

### Wav Input
Reading audio from a wav file is suboptimal, as the script needs to know note frequencies rather than the raw audio data to play on an oscilloscope. I approach the issue of extracting frequencies from raw aidio data by scanning through the data one window (some small range of samples) at a time, taking the Fourier transform of each window, and retrieving the 2 highest peaks. This is implemented in `wav_io.py`

For this method to produce palatable results, you typically must play the two most prominent frequencies. This produces a recognizable but very noisy reproduction of the audio. It is impressive that much of the orignal information can be preserved by just these 2 frequencies, but the results are nevertheless often too noisy to be of much use. **It is thus recommended to use a properly formatted MIDI file.**

## How It Works

#### 1. Extracting Contours
To maintain the illusion of a consistent image, the oscilloscope must be made to trace out the image rather than jumping around from point to point. To do so, it is necessary to extract the outlines/contours of an image.

This is done using a modified version of the marching squares algorithm. This version of marching squares maintains a list of conotours and adds each new edge to the correct conotours endpoint. Afterwards, the algorithm joins the contours with matching endpoints. The end result is a list of contours, each of which takes the form of a list of vertices that sequntially draw the contour. These algorithms are implemented in `contour.py`

`contour.py` also includes the function `contour_to_f`, which converts a given contour to a piecewise complex function with period 1 whose real part corresponds to the x coordinate and imagniary part to the y coordinate. This is done to make notation simpler and can be used to analyze via Fourier transforms the sound produced when the contour coordinates are converted to audio.

#### 2. Playing Sound with Contours
An image can be drawn on an oscilloscope by going through each of its contours and writing the x coordinate to first audio channel and the y coordinate to the second channel.

It turns out that the human ear interprets virtually anything periodic as a pitch. To play a note with frequency $`f`$, it is therefore sufficient to create drawings of our image with period $`\frac{1}{f}`$. In other words, if the sample rate of our output audio file is $`r`$, we take a total of $`\frac{r}{f}`$ equally spaced points along the image contours and write them to the audio file as before.

`oscilloscope.py` contains an `OscilloscopeDrawer` class which implements these methods.

#### 3. Playing a Chord
It would be nice to be able to play at least 2 notes simultaneously, especially when our frequencies are estimated from raw audio data. We also, however, want to preserve the relative shape of the audio so that it still draws an image.

A simple way to add a second tone without distorting our image is to play it using a simple square wave. A square wave merely jumps between 1 and -1 on both channels, and thus, when added the oscilloscope drawing, only changes its the midpoint. The results in the image being duplicated in the top left and bottom right corners of the oscilloscope (though the corners can be changed by altering the phase of the square waves on both channels). It is noteable that if the frequencies of the image and square wave happen to match, only complementary parts of the image may be drawn in each of the corners--this however only happens rarely.

The `OscilloscopeDrawer` class in `oscilloscope.py` contains the function `play_square_wave` for creating a simple square wave.

Another theoretical approach to playing two tones might be by modulating the amplitude by chosing which contours to play and omit based on their average amplitude. The contours, however, are not good estimations of sinusoidal waves, so using this method with the approximation in the [appendix](#appendix-weighted-sum-of-sines) does not work. Perhaps ordering the contours in a more sophisticated way can be used to address this in the future.

## Appendix: Weighted Sum of Sines
It can be shown geometrically that
```math
a\sin(\theta)+b\sin(\phi) = c\sin(\theta+\chi)
```
where $`c^2 = a^2 + b^2 + 2ab\cos(\alpha)`$, $`\sin(\chi) = \frac{b}{c}\sin(\alpha)`$, and $`\alpha = \phi-\theta`$.

If $`\theta`$ and $`\phi`$, are the first and second most prominent frequencies given by the Fourier transform, we can often than note assume that b<<a, meaning b<<c. This assumption is merely based on qualitative observations.

That b is much smaller than c implies that $`\chi`$ is small, more specifically that, on average, $`\chi<<\theta`$. Thus, we can approximate the weighted sum of sines as a signal with the most prominent frequency with amplitude modulated by c, that is $`c\sin(\theta)`$.

If we assume $`a^2 + b^2 >> 2ab`$, by the first order Taylor approximation we have
```math
c \approx \sqrt{a^2+b^2}\left( 1+\frac{ab}{a^2+b^2}\cos(\alpha) \right)
```

Thus, when two tones have frequencies $`f_1`$ and $`f_2`$, where $`\theta(t)=2 \pi f_1 t`$ and $`\phi(t)=2 \pi f_2 t`$, their combined chord can be represented as signal of frequency $`f_1`$ with the amplitude oscillating at a frequency of $`f_2-f_1`$ around the value $`\sqrt{a^2+b^2}`$.

This approximation seems to qualitatively hold rather nicely. Though it is not currently used by the project, it might be of use in the future.