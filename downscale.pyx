import cython
from cython.parallel import prange, parallel

cdef extern from "math.h":
    int round(double x) nogil

cdef extern from "math.h":
    double sqrt(double x) nogil

@cython.boundscheck(False)
def downscale(double [:, :] porewidth, int [:, :] mask, int zn, int [:, :] imagedown, int[:, :] maskdown):
    #
    # Parallel procedure which takes array of pore
    # half-width and return downscaled image as
    # 2D binary array
    #
    # Input:
    #
    # porewidth - array of pore half-width
    # mask      - image mask
    # zn        - area of the scanning in pixels
    #
    # Output:
    #
    # imagedown - downscaled image as 2D binary array
    # maskdown  - downscaled mask 
    #
    cdef int i, j, ii, jj, l, m
    cdef int nRow, nCol, nRowd, nCold,
    cdef double scaleR, scaleC, deltaij, di, dj

    nRow = porewidth.shape[0]
    nCol = porewidth.shape[1]

    nRowd = imagedown.shape[0]
    nCold = imagedown.shape[1]

    scaleR =  float(nRowd) / float(nRow)
    scaleC =  float(nCold) / float(nCol)
 
    with nogil, parallel():
        for i in prange(nRowd, schedule='dynamic'):
            for j in range(nCold):
                di = i / scaleR
                dj = j / scaleC

                ii = round(di)
                jj = round(dj)

                if zn >= ii or ii >= nRow - zn - 1 or \
                   zn >= jj or jj >= nCol - zn - 1:
                    maskdown[i, j] = 0
                    continue

                if mask[ii, jj] == 0:
                    maskdown[i, j] = 0
                    continue

                for l in range(ii - zn, ii + zn):
                    for m in range(jj - zn, jj + zn):
                        if mask[l, m] == 1: deltaij = porewidth[l, m]
                        else: deltaij = 0.0

                        if l - deltaij < di < l + deltaij and m - deltaij < dj < m + deltaij:
                            imagedown[i, j] = 1
                            break
                    if imagedown[i, j] == 1: break
