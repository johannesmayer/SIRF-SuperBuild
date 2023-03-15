import sys
from pathlib import Path
from sirf_recon import main_cine_recon as main

### looped reconstruction over files in input path
path_in  = Path(sys.argv[1])
path_out = Path(sys.argv[2])

if __name__ == __main__:
    success = main(path_in, path_out)
    sys.exit(success)

