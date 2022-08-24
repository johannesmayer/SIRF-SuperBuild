import sys, os
import shutil

from pathlib import Path
import sirf_preprocessing

import ismrmrd

from gadgetron_xml_parsing import get_gadget_property_from_xml

path_recon_execution = Path('/')
path_temp_files = Path('/home/')
fname_config="/recon/gtpipelines/Generic_Cartesian_Grappa.xml"

def main(path_in, fpath_output_prefix):

    print(f"Reading from {path_in}, writing into {fpath_output_prefix}")
    assert os.access(path_in, os.R_OK), f"You don't have write permission in {path_in}"
    assert os.access(fpath_output_prefix, os.W_OK), f"You don't have write permission in {fpath_output_prefix}"

    list_rawdata = sorted(path_in.glob("*.h5"))

    for fname_raw in list_rawdata:
        fname_preprocessed = preprocess_rawdata(fname_raw, path_temp_files)
        recon(fname_preprocessed, fname_config)
        clean_up_reconfiles(path_recon_execution)

        num_recon_slices = determine_num_slices(fname_raw)
        postprocess_dcm(path_recon_execution, fpath_output_prefix,num_recon_slices)

    print('python finished')

    return 0

def preprocess_rawdata(fname_rawdata, fpath_output):
    prefix_string = "temp_preprocessed"
    fname_processed_output = fpath_output / f"{prefix_string}_{fname_rawdata.name}"
    prep_success = sirf_preprocessing.preprocess(str(fname_rawdata), str(fname_processed_output))

    if prep_success:
        return fname_processed_output
    else:
        raise AssertionError("The preprocessing step failed. Aborting reconstructions.")

def recon(fname_rawdata, fname_config):
    cmd_recon = f"gadgetron_ismrmrd_client --filename={fname_rawdata} --outfile=' ' --config-local={fname_config}"

    print(f"Running command: {cmd_recon}")
    sys_return = os.system(cmd_recon)
    os.remove(str(fname_rawdata))

    if sys_return != 0:
        raise AssertionError("The reconstruction step failed. Aborting reconstructions.")

def clean_up_reconfiles(recon_path):
    flist_garbage=sorted(recon_path.glob("*_attrib.xml"))
    for f in flist_garbage:
        os.remove(f)


def determine_num_slices(fpath_raw):
    dset = ismrmrd.Dataset(fpath_raw, 'dataset', create_if_needed=False)
    header = ismrmrd.xsd.CreateFromDocument(dset.read_xml_header())

    num_slices = 1 + header.encoding[0].encodingLimits.slice.maximum - header.encoding[0].encodingLimits.slice.minimum
    return num_slices

def postprocess_dcm(input_dir, output_dir,num_recon_slices):
    print(f"--- Postprocessing gadgetron reconstruction: Searching for dicoms in {input_dir} and moving them to {output_dir}")

    flist_dcm=sorted(input_dir.glob("*.dcm"))

    num_recon_phases = determine_num_interpolated_phases(fname_config)
    num_tot_imgs = len(flist_dcm)
    num_acq_phases = num_tot_imgs/num_recon_slices - num_recon_phases

    for fdcm in flist_dcm:

        recon_number = extract_dcm_number_from_gt_recon(fdcm)
        target = Path(fdcm.parent / f"gt_recon_{recon_number}.dcm")
        
        if is_recon_number_relevant(recon_number, num_acq_phases, num_recon_phases, num_recon_slices):
            fdcm.rename(target)
            shutil.move(str(target), str(output_dir))
        else:
            os.remove(str(fdcm))

def determine_num_interpolated_phases(fpath_gt_pipeline_xml):
    return int(get_gadget_property_from_xml(fpath_gt_pipeline_xml, 'PhysioInterpolation', 'phases'))

def extract_dcm_number_from_gt_recon(fname_dcm):
    num_digits = 6
    num_slots_suffix=4
    return int(fname_dcm.parts[-1][-(num_digits+num_slots_suffix):-num_slots_suffix])

def is_recon_number_relevant(number, num_acq_phases, num_interpol_phases , num_recon_slices):
    from itertools import product
    offsets = [nslc * (num_interpol_phases + num_acq_phases) for nslc in range(num_recon_slices)]
    interpol_range = [i for i in range(num_acq_phases, num_acq_phases+num_interpol_phases)]

    relevant_numbers = [ i+o for i,o in product(offsets,interpol_range)]

    return number in relevant_numbers


### looped reconstruction over files in input path
path_in  = Path(sys.argv[1])
path_out = Path(sys.argv[2])

main(path_in, path_out)

