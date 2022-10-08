import sys
import argparse
import shutil
import logging
import os

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

log.info("preparing module with args: " + " ".join(sys.argv))

parser = argparse.ArgumentParser(description='Prepare a terraform module')
parser.add_argument('--pkg', type=str)
parser.add_argument('--name', type=str)
parser.add_argument('--module-dir', type=str)
parser.add_argument('--out', type=str)
parser.add_argument('--out-dirs', type=str)
parser.add_argument('--strip', type=str)
parser.add_argument('--deps', type=str)
parser.add_argument('--modules', type=str, nargs='+')

args = parser.parse_args()
print(args)

shutil.move(args.module_dir, args.out)

modules = args.modules

for module in args.modules:
    if module is '':
        # if modules is left blank, the way it is passed results in a list with an empty string
        # maybe just pretend like that doesn't happen and continue on with our day
        continue
    module_path = module.rstrip("/" + os.environ.get("TERRAFORM_TARGET"))
    log.info(f"Moving {module} to {args.out}/{module_path}")
    shutil.copytree(module, args.out + "/" + module_path)