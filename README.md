# downscaling
The downscaling code allows to enhance X-ray computed tomography (XCT)
images of heterogeneous porous sample and extract pore space geometry without
performing a preliminary noise filtering. The code is accurate when the porous
sample is chemically effectively homogeneous across the solid phase and the
void phase and the uncertainties of the imaging experiment originate only from
the photon shot-noise and the unresolved micro-porosity or from the partial
volume effect. Due to the noise, the intensity value of the output data varies
even though the sample is chemically homogeneous. The noise can be described
by a Poisson probability density function (PDF), which can be approximated
by a Gaussian distribution. We assume that the signal-to-noise ratio is high
enough to allow identification of the solid and void phases as maximums on
the data intensity histogram. The geometrical features of the unresolved micro-
porosity are uncertain, but information about the porosity is still preserved
in the image intensity. We define the unresolved micro-porosity as a porous
phase. The main idea of the downscaling code is to map the low-
resolution gray-scale image into a high-resolution binary image, while preserving
the maximum information regarding the unresolved porosity, then extract the
multi-scale pore distribution by segmentation of the void space of the binary
image on interconnected void regions bounded by the solid phase.

The code and the example of the XCT data are available as Amazon AWS
EC2 public image (AMI) or at the GitHub
https://github.com/svyatoslavkorneev/downscaling. Amazon AMI is a fully
pre-configured environment which allows to deploy Amazon EC2 computing
instance and run the code withing a minute. The image also includes operating
system Ubuntu 14.04.5 LTS, all required Python libraries and Anaconda. After
the computing instance is initialized, the downscaling code is ready to run.
Public image name is #downscaling_code_Korneev_Battiato.

Compilation of the parallel Cython library.

Translateto C code
cython downscale.pyx

Compile the C code with OpenMP
and output the compiled sharedlibrary
which can be imported from the Python
gcc −fPIC −fopenmp −shared −o downscale.so downscale.c \
−I /home/ubuntu/anaconda2/include/python2.7/


Example of the output of the program process_downscale.py, where
the string image shows the name of the downscaled image, delta is the half of the
width of the sub-pixel pore at the void phase, porosity is the image porosity,
residual is the accuracy of the root finding, number of extracted regions is
number of pores of the downscaled image and average region area is the average
area of extracted pores in pixels.

Image : C6197_0009 , delta: 0.755033344803 \
porosity : 0.310749161206 , \
residual −9.7293157908 e −07 , \
number of extracted regions : 450582
C6197_0009 measure regionsarea...
Average region area is 0.505825171667
C6197_0009 done.
