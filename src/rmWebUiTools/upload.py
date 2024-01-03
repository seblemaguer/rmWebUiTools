#!/usr/bin/env python3
"""
Upload - Upload either PDFs or ePubs to your remarkable.
"""


import argparse
import os
import logging
from sys import stderr
from . import api


LOGGER = logging.getLogger()


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    ap.add_argument(
        "-t",
        "--target-folder",
        default="/",
        help="Folder on your remarkable to put the uploaded files in ('/' corresponds to the root directory)"
    )
    ap.add_argument("file", type=argparse.FileType("rb"), nargs="+")

    args = ap.parse_args()

    try:
        api.changeDirectory(args.target_folder)
        for file in args.file:
            file_name, file_extension = os.path.splitext(file.name)
            if file_extension.lower() not in [".pdf", ".epub"]:
                print(f"Only PDFs and ePubs are supported. Skipping {file.name}")
                continue
            LOGGER.info(f"Uploading {file.name} to {args.target_folder}")
            api.upload(file)
            LOGGER.info(f"Successfully uploaded {file.name} to {args.target_folder}")
        LOGGER.info("Done!")
    except KeyboardInterrupt:
        LOGGER.info("Cancelled.")
        exit(0)
    except Exception as ex:
        LOGGER.error(f"ERROR: {ex}")
        LOGGER.error(
            'Please make sure your reMarkable is connected to this PC and you have enabled the USB Webinterface in "Settings -> Storage".'
        )
        exit(1)
    finally:
        for file in args.file:
            file.close()


if __name__ == "__main__":
    main()
