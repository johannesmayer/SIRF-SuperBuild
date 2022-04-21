import numpy as np
import nibabel as nib
import sys, re, os
import glob

path_in = sys.argv[1]
path_out = sys.argv[2]

print(path_in)
print(os.stat(path_in).st_uid)
print(os.access(path_in, os.R_OK))
print(os.access(path_in, os.W_OK))

print(path_out)
print(os.stat(path_out).st_uid)
print(os.access(path_out, os.R_OK))
print(os.access(path_out, os.W_OK))

list_of_files = []

for file in os.listdir(path_in):
        list_of_files.append(os.path.join(path_in,file))
for name in list_of_files:
    print('in ', name)
    
# Get all h5 files
data = [os.path.basename(x) for x in glob.glob(path_in + '/*.h5')]

for name in data:
    print('h5 ', name)
    
file_in = data[0]


print('python started again')


import sirf.Gadgetron as pMR
import sirf.Reg as pReg

rawdata = pMR.AcquisitionData(path_in + '/' + file_in)
rawdata = pMR.preprocess_acquisition_data(rawdata)
rawdata.sort()

recon = pMR.FullySampledReconstructor()
recon.set_input(rawdata)
recon.process()
img_data = recon.get_output()

img_data = img_data.abs()
img_data /= img_data.as_array().max()
img_data *= 2^16
file_out = file_in.replace('.h5', '.dcm')
img_data.write(path_out + '/' + file_out)

#file_out = file_in.replace('.h5', '.nii')
#img_data.write(path_out + '/' + file_out)

#nii_img = pReg.NiftiImageData(img_data)
#file_out = file_in.replace('.h5', '_reg.nii')
#nii_img.write(path_out + '/' + file_out)



print('python finished')
