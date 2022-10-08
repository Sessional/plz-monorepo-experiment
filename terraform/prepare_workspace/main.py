import argparse
import shutil
from pathlib import Path
import sys
import logging
import os

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

log.info("preparing root with args: " + " ".join(sys.argv))

parser = argparse.ArgumentParser(description='Prepare a please terraform workspace')
parser.add_argument('--pkg',type=str)
parser.add_argument('--name', type=str)
parser.add_argument('--os', type=str)
parser.add_argument('--arch', type=str)
parser.add_argument('--out', type=str)
parser.add_argument('--pkg-dir', type=str)
parser.add_argument('--srcs', type=str)
parser.add_argument('--var-files', type=str)
parser.add_argument('--modules', type=str, nargs='+')
args = parser.parse_args()

pkg = args.pkg
name = args.name
os_arg = args.os
arch = args.arch
out = args.out
pkg_dir = args.pkg_dir
srcs = args.srcs
var_files = args.var_files
modules = args.modules

sources_as_list = srcs[1:-1].split(" ")

Path(out).mkdir(parents=True, exist_ok=True)

for src in sources_as_list:
    file_path = Path(src)
    file_path = os.path.dirname(file_path)
    destination = out
    if file_path:
        # support a module containing module references relative
        # to the current path that have not been set up as a
        # please terraform_module
        log.debug(f"File has path {file_path}")
        destination =  out + "/" + file_path
        Path(destination).mkdir(parents=True, exist_ok=True)

    log.debug(f"Copying {src} to {destination}")
    shutil.copy(f"{pkg_dir}/{src}", destination)

log.debug(modules)
for module in modules:
    # this is a side effect of having the `/terraform` out directory
    # ideally there would be a better way to figure this out, but
    # I don't know what that would look like...
    # if the terraform_module is NOT set up using the terraform
    # label we won't find it :(
    new_path = module.rstrip("/" + os.environ.get("TERRAFORM_TARGET"))
    shutil.copytree(module, f"{out}/{new_path}")
