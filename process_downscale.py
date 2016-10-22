# Import Python libraries
from PIL import Image
import numpy as np

from scipy import optimize

from skimage import data, io
from skimage.measure import regionprops
import downscale as down
from skimage.color import label2rgb
from skimage.measure import label

import os.path as path

import multiprocessing as mp
import ctypes

def df(delta, x, x1, x2):
    # Function to map pixel intensity to pore width
    #
    # Input:
    #
    # float delta - free parameter
    # float x     - pixel intensity
    # float x1    - intensity of the solid phase
    # float x2    - intensity of the void phase
    #
    # Output
    #
    # float df - pore width
    #
    if x >= x1:
        return (delta / (x2 - x1)) * (x - x1)
    else:
        return 0.0

def porosity(image, mask, x1, x2):
    # Function to map pixel intensity to porosity
    #
    # Input:
    #
    # float   [:,:] image - original image as 2D array
    # integer [:,:] mask  - image mask
    # float         x1    - intensity of the solid phase
    # float         x2    - intensity of the void phase
    #
    # Output:
    # float porosity - porosity of the image
    #
    fi = (image - x1) / (x2- x1)
    fiflat = fi.flatten()
    maskflat = mask.flatten()
    return np.mean(np.ma.masked_where(maskflat==0, fiflat))

def downscale_image(delta, image, mask, x1, x2, fi, scale, rf):
    # Function to downscale image and return difference
    # between porosity of the original and  downscaled images
    #
    # Input:
    #
    # float          delta  - sub-pixel pore half width
    #                         to be defined by the root
    #                         finding procedure
    # float [:,:]    image  - original image as 2D array
    # integer [:,:]  mask   - image mask
    # float          x1     - intensity of the solid phase
    # float          x2     - intensity of the void phase
    # float          fi     - porosity of the original image
    # integer        scale  - resolution of downscaled
    #                         image with respect to the
    #                         original image
    # boolen         rf     - output flag
    #                          
    # Output:
    # 
    # rf == True
    # float downscale_image - difference between porosity of
    #                         the downscaled image and porosity
    #                         of the original image
    # rf == False
    # (float, integer [:,:]) \
    # downscale_image - (difference between porosity of
    #                   the downscaled image and porosity
    #                   of the original image, downscaled
    #                   image as 2D array)
    #

    # Read image dimensions
    nRow, nCol = image.shape
    # Fill the array of pore width and
    porewidth = np.zeros((nRow, nCol))
    for i in range(nRow):
        for j in range(nCol):
            porewidth[i, j] = df(delta, image[i, j], x1, x2)

    # Find the downscaled image as 
    # binary array
    maskdown = np.ones((nRow * scale, nCol * scale), dtype = np.int32)
    imagedown = np.zeros((nRow * scale, nCol * scale), dtype = np.int32)

    # Call parallel function to perform the downscaling
    down.downscale(porewidth, mask, 3, imagedown, maskdown)

    # Calculate the porosity of the downscaled image
    imagedownflat = imagedown.flatten()
    maskdownflat = maskdown.flatten()
    imagedownflatmask = np.ma.masked_where(maskdownflat==0, imagedownflat)

    # Return results
    if rf == True:
        return np.mean(imagedownflatmask) - fi
    else:
        return (np.mean(imagedownflatmask) - fi, imagedown)


def downscale(image, mask, scale, x1, x2):

    # Estimate image porosity
    fi = porosity(image, mask, x1, x2)

    # Find parameter "delta" in order to match
    # the porosity of the original and downscaled images
    root = optimize.brentq(downscale_image, 0.2, 1.0, \
           args = (image, mask, x1, x2, fi, scale, True), rtol = 0.00001)
 
    residual, imagedown = downscale_image(root, image, mask, x1, x2, fi, scale, False)

    # Perform connected-components labeling
    label_down = label(imagedown, connectivity = 1)
    # Region properties
    regprop = regionprops(label_down)
    nreg = np.size(regprop)

    # Set the output with some useful information
    logstr = 'Image: ' + fname + ', delta: ' + \
             str(root) + ' porosity: ' + str(fi) + \
             ', residual ' + str(residual) + \
             ', number of extracted regions: ' + str(nreg)
    
    # Return downscaled image, properties of extracted
    # regions, porosity of the original image, output string
    return (imagedown, regprop, fi, logstr)


ii16 = float(np.iinfo(np.uint16).max)
# Define resolution of downscaled
# image with respect to the original image
scale = 20
# Load images
images = io.imread_collection('Images/*.tif')

# Main loop over all images
n = len(images)
for ii in range(0, 1):
    # Get the image file name
    fname = path.splitext(path.basename(images.files[ii]))[0]

    # Read intensity data of the solid and void phases
    x1, x2 = np.loadtxt(path.join('x1x2', fname + '.txt'))
    # Read mask of the image
    mask = io.imread(path.join('Mask', fname + '.tif')) * 1
    mask = mask.astype(np.int32, copy = False)

    # Inver image color and scale the intensity,
    # where the max intensity is 1 and
    # the intensity of the solid phase is less then
    # the intensity of the void phase
    imagei = np.invert(images[ii]) / ii16
    
    # Call the downscaling function
    imagedown, regprop, fi, logstr = downscale(imagei, mask, scale, x1, x2)

    print(logstr)

    print(fname + ' measure regions area...')

    # Initialize shared array for the parallel
    # region measurements
    nreg = np.size(regprop)
    area_arr_base = mp.Array(ctypes.c_double, nreg)
    area_arr = np.ctypeslib.as_array(area_arr_base.get_obj())

    # Measure the area of connected components
    # in parallel
    def measure_area(i, def_param = area_arr):
        area_arr[i] = regprop[i].area / np.float(scale * scale)

    pool = mp.Pool()
    pool.map(measure_area, range(nreg))
    pool.close()
    pool.join()

    print('Average region area is ' +  str(np.average(area_arr)))

    # Output the downscaled image as TIFF file
    tifdown = Image.fromarray(imagedown.astype('uint8') * 255)
    tifdown = tifdown.convert('1')
    tifdown.save(path.join('Downscale', fname + '.tif'))   

    # Output the area of connected components to the text file,
    # where the area is measured in pixels of the original image
    np.savetxt(path.join('Regions', fname + '.txt'), area_arr)
    print(fname + " done.")
    print('-----------------------')
