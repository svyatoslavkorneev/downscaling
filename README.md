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

The complete user's manual is located in the file Manual.pdf
