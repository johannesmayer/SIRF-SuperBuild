import numpy as np
import sys, os


from pathlib import Path

import sirf_preprocessing

def main(path_in, fpath_output_prefix):

    print(f"Reading from {path_in}, writing into {fpath_output_prefix}")
    assert os.access(path_in, os.R_OK), f"You don't have write permission in {path_in}"
    assert os.access(fpath_output_prefix, os.W_OK), f"You don't have write permission in {fpath_output_prefix}"

    list_of_files = sorted(path_in.glob("*.h5"))

    for mrfile in list_of_files:

        fname_processed_output = fpath_output_prefix / f"temp_preprocessed_{mrfile.name}"
        prep_success = sirf_preprocessing.preprocess(str(mrfile), str(fname_processed_output))

        recon_path_out = fpath_output_prefix / str(fname_processed_output.stem).replace('temp_preprocessed_', 'recon_')

        if prep_success:
            cmd_recon = f"/bin/bash /recon/gt_grappa.sh {fname_processed_output} {recon_path_out}"
            print(f"Running command: {cmd_recon}")
            sys_return = os.system(cmd_recon)
            os.remove(str(fname_processed_output))
            if sys_return != 0:
                raise AssertionError("The reconstruction step failed. Aborting reconstructions.")
        else:
            raise AssertionError("The preprocessing step failed. Aborting reconstructions.")

    print('python finished')

    return 0

### looped reconstruction over files in input path
path_in  = Path(sys.argv[1])
path_out = Path(sys.argv[2])

try:
    main(path_in, path_out)
except Exception as e:
    print(f"Program failed because of {str(e)}")
