import numpy as np
import matplotlib.pyplot as plt

contour_lookup = {
    (True, True, True, True): [],
    (True, True, False, True): [[(0,1), (1,0)]],
    (True, True, True, False): [[(1,0), (2,1)]],
    (True, True, False, False): [[(0,1), (2,1)]],
    (True, False, True, True): [[(1,2), (2,1)]],
    (True, False, False, True): [[(0,1), (1,2)], [(1,0), (2,1)]],
    (True, False, True, False): [[(1, 0), (1,2)]],
    (True, False, False, False): [[(0,1), (1,2)]],
    (False, True, True, True): [[(0,1), (1,2)]],
    (False, True, False, True): [[(1,0), (1,2)]],
    (False, True, True, False): [[(0,1), (1,0)], [(1,2), (2,1)]],
    (False, True, False, False): [[(1,2), (2,1)]],
    (False, False, True, True): [[(0,1), (2,1)]],
    (False, False, False, True): [[(1,0), (2,1)]],
    (False, False, True, False): [[(0,1), (1,0)]],
    (False, False, False, False): []
}

def marching_squares(img_data, threshold = 255):
    Y, X = img_data.shape
    bin_array = img_data < threshold
    
    def coord(contour, x, y):
        return (x+contour[0]*0.5 - X/2, -y+contour[1]*0.5 + Y/2)
    
    contours = []
    
    # March through each 2x2 pixel square
    for x in range(0, X-1):
        for y in range(0, Y-1):
            # Identify countour coordinates on the square
            gridpoints = tuple(bin_array[y:y+2, x:x+2].flatten())
            
            for contour_seg in contour_lookup[gridpoints]:
                coord0 = coord(contour_seg[0], x, y)
                coord1 = coord(contour_seg[1], x, y)
                
                # Add contour segment to the correct contour
                added = False
                
                for contour in contours:
                    # Bad icky else if ladder for combining contour segments
                    if contour[0] == coord0:
                        contour.insert(0, coord1)
                        added = True
                        break
                    elif contour[0] == coord1:
                        contour.insert(0, coord0)
                        added = True
                        break
                    elif contour[-1] == coord0:
                        contour.append(coord1)
                        added = True
                        break
                    elif contour[-1] == coord1:
                        contour.append(coord0)
                        added = True
                        break
                
                if not added:
                    contours.append([coord0, coord1])
    
    return contours

# Combine contours that join at endpoints
def combine_contours(contours):
    contours_combined = []
    
    # Go through each contour
    for i in range(len(contours)):
        standalone = True
        
        # Check if this contour connects to any of the other contours
        contour = contours[i]
        for j in range(i+1, len(contours)):
            parent_contour = contours[j]
            
            # If so, connect it to the other contour (using another icky else if ladder of course)
            if contour[0] == parent_contour[0]:
                contours[j] = contour[:0:-1] + parent_contour
                standalone = False
                break
            elif contour[-1] == parent_contour[0]:
                contours[j] = contour[:-1] + parent_contour
                standalone = False
                break
            elif contour[0] == parent_contour[-1]:
                contours[j] = parent_contour + contour[1:]
                standalone = False
                break
            elif contour[-1] == parent_contour[-1]:
                contours[j] = parent_contour + contour[-2::-1]
                standalone = False
                break
        
        # If the contour does not connect to any other contours, add it to the list of full contours
        if standalone:
            contours_combined.append(contour)
    
    return contours_combined

def get_contours(img_data, threshold = 255):
    contours = marching_squares(img_data, threshold)
    return combine_contours(contours)

def sort_contours(contours):
    # Get average amplitude
    avg_amps = []
    for contour in contours:
        avg_amp = sum([c[0]**2 + c[1]**2 for c in contour]) / len(contour)
        avg_amps.append(avg_amp)
    
    # Sort average amplitudes
    sorted_indices = np.argsort(avg_amps)
    avg_amps = np.array(avg_amps)[sorted_indices]
    
    # Reposition contours accordingly
    contours_sorted = []
    for i in sorted_indices:
        contours_sorted.append(contours[i])
    
    return contours_sorted, avg_amps

# Converts a contour to a piecewise complex function with period 1
def contour_to_f(contour):
    N = len(contour)
    
    def f(t):
        k = np.floor(N*t)
        
        z1 = contour[int(k%N)][0] + 1j*contour[int(k%N)][1]
        z2 = contour[int((k+1)%N)][0] + 1j*contour[int((k+1)%N)][1]
        
        return z1 + (z2-z1)*t/N
    
    return np.vectorize(f)

def show_contours(contours, legend=False):
    for i, contour in enumerate(contours):
        plt.plot([c[0] for c in contour], [c[1] for c in contour], label=i)
    if legend:
        plt.legend()
    
    return plt.gcf(), plt.gca()