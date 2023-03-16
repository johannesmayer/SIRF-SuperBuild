#!/bin/bash --login

exec gadgetron &
exec python /recon/mr_cine_recon.py /input /output
exec kill $(pidof gadgetron)