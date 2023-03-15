#!/bin/bash --login

set +euo pipefail
conda activate base
set -euo pipefail

exec gadgetron &
exec python /recon/mr_cine_recon.py /input /output
exec kill $(pidof gadgetron)