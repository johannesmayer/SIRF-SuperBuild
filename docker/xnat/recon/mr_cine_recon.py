import sys, os
import shutil

from pathlib import Path

import sirf_preprocessing

def extract_dcm_number_from_gt_recon(fname_dcm):
    num_digits = 6
    num_slots_suffix=4
    return fname_dcm.parts[-1][-(num_digits+num_slots_suffix):-num_slots_suffix]

def postprocess_dcm(input_dir, output_dir):
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

current_directory = Path(__file__).parent.resolve()

def main(path_in, fpath_output_prefix):

    print(f"Reading from {path_in}, writing into {fpath_output_prefix}")
    assert os.access(path_in, os.R_OK), f"You don't have write permission in {path_in}"
    assert os.access(fpath_output_prefix, os.W_OK), f"You don't have write permission in {fpath_output_prefix}"

    temp_path_output = Path('/home/')

    list_of_files = sorted(path_in.glob("*.h5"))

    for mrfile in list_of_files:
        fname_processed_output = temp_path_output / f"temp_preprocessed_{mrfile.name}"
        prep_success = sirf_preprocessing.preprocess(str(mrfile), str(fname_processed_output))

        if prep_success:
            cmd_recon = f"/bin/bash /recon/gt_grappa.sh {fname_processed_output} {fpath_output_prefix}"
            print(f"Running command: {cmd_recon}")
            sys_return = os.system(cmd_recon)
            os.remove(str(fname_processed_output))
            if sys_return != 0:
                raise AssertionError("The reconstruction step failed. Aborting reconstructions.")
        else:
            raise AssertionError("The preprocessing step failed. Aborting reconstructions.")

        import pathlib
        
        postprocess_dcm

    print('python finished')

    return 0

### looped reconstruction over files in input path
path_in  = Path(sys.argv[1])
path_out = Path(sys.argv[2])

main(path_in, path_out)

