import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Welcome to the Zero shell')
    parser.add_argument('-C', '--connection')
    args = parser.parse_args()
