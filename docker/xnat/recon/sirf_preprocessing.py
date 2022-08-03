import numpy as np
import os

from collections import Counter
import sirf.Gadgetron as pMR


def main(path_in, path_out):

    print(f"Reading from {path_in}, writing into {path_out}")
    assert os.access(path_in, os.R_OK), f"You don't have write permission in {path_in}"
    assert os.access(path_out, os.W_OK), f"You don't have write permission in {path_out}"

    list_of_files = sorted(path_in.glob("*.h5"))

    for mrfile in list_of_files:

        cname_out = path_out / f"preprocessed_{mrfile.name}"
        preprocess(str(mrfile),str(cname_out))

    print('preprocessing finished')

    return 0

def preprocess(fname_in,fname_out):
    
    rd = pMR.AcquisitionData(fname_in)
    rd_preprocessed = rd.copy()
    
    # get the undersampled and last fully sampled phase
    undersampled_phases, fsp = get_undersampled_phases(rd)

    # get phase encoding for last fully sampled phase
    pe_fs = get_phasencoding_for_phase(rd,fsp)

    fullysampled_data = get_phase_subset(rd, fsp)

    print(f"We have found undersampled phases: {undersampled_phases}.")
    print(f"Fully sampled reference phase: {fsp}.")
    for usp in undersampled_phases:
        cphaseenc = get_phasencoding_for_phase(rd,usp)

        missing_points = list(set(pe_fs) - set(cphaseenc))
        rd_missing = get_missing_pe_points(fullysampled_data, missing_points)

        max_time_stamp = get_maximum_physio_timestamp_for_phase(rd, usp)
        print(f"Setting the time stamp of {max_time_stamp} to hope for better distribution.")
        print(f"adding {rd_missing.number()} phase encoding points to phase {usp}")
        for i in range(rd_missing.number()):
            acq = rd_missing.acquisition(i)
            acq.set_phase(usp)
            acq.set_physiology_time_stamp(max_time_stamp,0)
            rd_preprocessed.append_acquisition(acq)

    rd_preprocessed.write(fname_out)
    
    return True

def get_maximum_physio_timestamp_for_phase(rawdata, phase):

    rd = get_phase_subset(rawdata, phase)
    return np.max(rd.get_ISMRMRD_info('physiology_time_stamp'))

def get_undersampled_phases(rawdata):
    cardiac_phase = rawdata.get_ISMRMRD_info('phase')
    cpc = Counter(cardiac_phase)
    pe_pts_per_phase = [cpc[key] for key in cpc]

    # TODO: check for that if all have same number of readouts as median

    median_num_ro_per_phase = np.median(sorted(pe_pts_per_phase))
    undersampled_phases = np.where(pe_pts_per_phase < median_num_ro_per_phase)
    last_fullysampled_phase = np.min(undersampled_phases[0]) - 1
    
    return undersampled_phases[0], last_fullysampled_phase

def get_phasencoding_for_phase(rawdata, phase_number):

    rawdata = get_phase_subset(rawdata,phase_number)
    return rawdata.get_ISMRMRD_info('kspace_encode_step_1')

def get_phase_subset(rawdata,phase_number):

    cardiac_phase = rawdata.get_ISMRMRD_info('phase')
    idx_all = np.arange(rawdata.number())
    idx_phase_number = idx_all[cardiac_phase == phase_number]

    return rawdata.get_subset(idx_phase_number)


def get_missing_pe_points(rawdata,missing_points):
    
    pe_points = rawdata.get_ISMRMRD_info('kspace_encode_step_1')

    overlap = np.isin(pe_points, missing_points)
    idx_all = np.arange(rawdata.number())
    idx_missing = idx_all[overlap]
    
    return rawdata.get_subset(idx_missing)

