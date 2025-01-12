# Building SyneRBI_VM via Vagrant

## Installation of prerequisites

- Install VirtualBox
- Install [Vagrant](https://www.vagrantup.com)
- Install the vbguest plugin. This makes sure the VirtualBox Guest additions will be up-to-date w.r.t.
the VirtualBox version you have.
```
vagrant plugin install vagrant-vbguest
```

## VM creation

Make sure there is no other SIRF VM running (as it will mean vagrant aborts due to a port forwarding conflict)

### Set environment variables used in the Vagrantfile
We currently have the following:
- `VB_CPUS` (defaults to 4): number of virtual CPUs used by the VM
- `VB_RAM` (defaults to 6096): system RAM to be used by the VM
- `VB_NAME` (defaults to "SIRF 3.4.0")
- `UPDATE_ARGS` (defaults to "-j `nproc`"): any arguments to be passed to the `UPDATE.sh` script.

For example in Windows Powershell:
```ps
$Env:UPDATE_ARGS="-t origin/master -j 4"
```
will make sure we use current `master` (as opposed to the latest release), with a parallel build of max 4 processes.

### Start the machine

```
cd vagrant
vagrant up
```
This will take a substantial amount of time.

### Final configuration
Log into the VM, open a terminal and type
```sh
~/devel/SIRF-SuperBuild/VirtualBox/scripts/first_run.sh
```
1. changes some settings of the gnome desktop environment
2. configures Jupyter
```
If you want to export the VM, we recommend running
```sh
~/devel/SIRF-SuperBuild/VirtualBox/scripts/clean_before_VM_export.sh
```

See the [scripts/README.md](../scripts/README.md) for more information.

## Other useful vagrant commands
The following can be done via the VirtualBox interface, but you can use `vagrant` as well.

- Pause the machine

```
vagrant suspend
```

- Shutdown the machine

```
vagrant halt
```

- Remove the machine (to start from scratch)

```
vagrant destroy
```

## Documentation

- [https://www.vagrantup.com/docs/](https://www.vagrantup.com/docs/)
- [https://www.packer.io/intro/](https://www.packer.io/intro/)
