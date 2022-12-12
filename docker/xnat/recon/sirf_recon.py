import os
import shutil

from pathlib import Path
import sirf_preprocessing

from gadgetron_xml_parsing import get_gadget_property_from_xml

import sirf.Gadgetron as pMR

path_recon_execution = Path('/')
path_temp_files = Path('/home/')
fname_config="/recon/gtpipelines/Generic_Cartesian_Grappa.xml"

def main(path_in, fpath_output_prefix):

    print(f"Reading from {path_in}, writing into {fpath_output_prefix}")
    assert os.access(path_in, os.R_OK), f"You don't have write permission in {path_in}"
    assert os.access(fpath_output_prefix, os.W_OK), f"You don't have write permission in {fpath_output_prefix}"

    list_rawdata = sorted(path_in.glob("*.h5"))

    for fname_raw in list_rawdata:
        fname_preprocessed, kspace_dims = preprocess_rawdata(fname_raw, path_temp_files)
#        recon(fname_preprocessed, fname_config)
        recon_complete_with_sirf(fname_preprocessed, fpath_output_prefix)
#        clean_up_reconfiles(path_recon_execution)

#        num_recon_slices = kspace_dims['slice']
#        postprocess_dcm(path_recon_execution, fpath_output_prefix,num_recon_slices)

    print('python finished')

    return 0

def preprocess_rawdata(fname_rawdata, fpath_output):
    prefix_string = "temp_preprocessed"
    fname_processed_output = fpath_output / f"{prefix_string}_{fname_rawdata.name}"
    kspace_dims = sirf_preprocessing.preprocess(str(fname_rawdata), str(fname_processed_output))

    if kspace_dims:
        return fname_processed_output, kspace_dims
    else:
        raise AssertionError("The preprocessing step failed. Aborting reconstructions.")

def recon_complete_with_sirf(fname_raw, fprefix_out):

    # acq_data = AcquisitionData(str(fname_raw))

    acq_data = preprocess(str(fname_raw), "/media/sf_CCPPETMR/tmp.h5")
    print(type(acq_data))
    # Pre-process this input data.
    # (Currently this is a Python script that just sets up a 3 chain gadget.
    # In the future it will be independent of the MR recon engine.)
    print('---\n pre-processing acquisition data...')
    preprocessed_data = preprocess_acquisition_data(acq_data)

    # Perform reconstruction of the preprocessed data.
    # 1. set the reconstruction to be for Cartesian GRAPPA data.
    recon_gadgets = ['AcquisitionAccumulateTriggerGadget',
            'B2B:BucketToBufferGadget', 
            'GenericReconCartesianReferencePrepGadget', 
            'GenericReconEigenChannelGadget',
            'GRAPPA:GenericReconCartesianGrappaGadget', 
            'GenericReconPartialFourierHandlingFilterGadget',
            'GenericReconKSpaceFilteringGadget',
            'GenericReconFieldOfViewAdjustmentGadget', 
            'GenericReconImageArrayScalingGadget', 
            'ImageArraySplitGadget',
            'PhysioInterpolationGadget(phases=30, mode=0, first_beat_on_trigger=true, interp_method=BSpline)',
            # 'ComplexToFloatGadget',
            # 'FloatToUShortGadget'
            ]

    recon = Reconstructor(recon_gadgets)

    recon.set_gadget_property("B2B", "N_dimension", "phase")
    recon.set_gadget_property("B2B", "S_dimension", "set")
    recon.set_gadget_property('GRAPPA', 'send_out_gfactor', True)

    # 2. set the reconstruction input to be the data we just preprocessed.
    recon.set_input(preprocessed_data)

    # 3. run (i.e. 'process') the reconstruction.
    print('---\n reconstructing...\n')
    recon.process()

    # retrieve reconstruced image and G-factor data
    image_data = recon.get_output('Image PhysioInterp')
    # image_data = recon.get_output('image')
    print(f"We have {image_data.number()} images to write.")
    image_data = image_data.abs()
    image_data.write(str(fprefix_out / "sirfrecon.dcm"))

    return None

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
    # first gadgetron writes all reconstructed images, then all that are the output of the PhysioInterpolation gadget
    offset = int(num_recon_slices * num_acq_phases)
    relevant_numbers = [ int(i) for i in range(offset,int((num_acq_phases+num_interpol_phases)*num_recon_slices))]

    return int(number) in relevant_numbers

