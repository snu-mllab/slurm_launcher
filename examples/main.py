import argparse
import os
parser = argparse.ArgumentParser()
parser.add_argument('--seed', type=int)
args = parser.parse_args()

if __name__ == '__main__':
    print("Hello, world! on seed {} from".format(args.seed), flush=True)

