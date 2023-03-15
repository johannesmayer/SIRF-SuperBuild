#!/bin/bash --login

set +euo pipefail
conda activate base
set -euo pipefail

exec python /recon/mr_cine_recon.py /input /output