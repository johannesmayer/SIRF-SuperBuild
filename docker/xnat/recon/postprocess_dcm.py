'''
Author: Johannes Mayer
'''
import argparse
from pathlib import Path
import shutil, os

parser = argparse.ArgumentParser(description="Postprocess Gadgetron DICOMs.")
parser.add_argument('-i', '--input', help='Directory of where the gadgetron_ismrmrd_client was called.')
parser.add_argument('-o', '--output', help='Name of the directory in which the Dicoms should be stored.')

args = parser.parse_args()

dir_in = Path(args.input)
dir_out = Path(args.output)

assert dir_out.is_dir(), "You gave an output directory that does not exists. The program is stopped."

def extract_dcm_number_from_gt_recon(fname_dcm):
    num_digits = 6
    num_slots_suffix=4
    return fname_dcm.parts[-1][-(num_digits+num_slots_suffix):-num_slots_suffix]

def main(input_dir, output_dir):
    print(f"--- Postprocessing gadgetron reconstruction: Searching for dicoms in {input_dir} and moving them to {output_dir}")

    flist_dcm=sorted(input_dir.glob("*.dcm"))

    num_recon_phases = 30
    all_imgs = len(flist_dcm)
    first_img_num = all_imgs - num_recon_phases 
    for fdcm in flist_dcm:

        recon_number = extract_dcm_number_from_gt_recon(fdcm)
        target = Path(fdcm.parent / f"gt_recon_{recon_number}.dcm")

        if int(recon_number) >= first_img_num:
            fdcm.rename(target)
            shutil.move(str(target), str(output_dir))
        else:
            os.remove(str(fdcm))

main(dir_in, dir_out)