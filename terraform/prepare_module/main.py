import sys
import argparse
import shutil

print("preparing module with args: " + " ".join(sys.argv))

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--pkg', type=str)
parser.add_argument('--name', type=str)
parser.add_argument('--module-dir', type=str)
parser.add_argument('--out', type=str)
parser.add_argument('--out-dirs', type=str)
parser.add_argument('--strip', type=str)
parser.add_argument('--deps', type=str)
args = parser.parse_args()

shutil.move(args.module_dir, args.out)
