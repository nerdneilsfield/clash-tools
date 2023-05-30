import argparse
import logging

import coloredlogs

from clash_tools import Subscribers, Rules 

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description="update scribers")

    argparser.add_argument("-f", "--file", help="subscribers file", default="subscribers.yml", required=True)
    argparser.add_argument("-o", "--output", help="output file", default="out_subscribers.yml", required=True)
    argparser.add_argument("-r", "--rules", help="rules file", default="rules.yml", required=True)
    argparser.add_argument("-v", "--verbose", help="verbose", action="store_true")

    args = argparser.parse_args()

    coloredlogs.install()

    if args.verbose:
        logging.info(f"verbose mode")
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.info(f"update subscribers from {args.file}")

    subscribers = Subscribers(args.file)

    rules = Rules(output_path=args.output)

    rules.append_with_path(args.rules)

    rules.set_subscribers(subscribers)

    rules.generate_configs()



