#!/usr/bin/env python3
"""
Upload - Upload either PDFs or ePubs to your remarkable.
"""


import argparse
import os

from sys import stderr


from . import api


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    ap.add_argument(
        "-t",
        "--target-folder",
        required=True,
        help="Folder on your remarkable to put the uploaded files in",
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
            print(f"Uploading {file.name} to {args.target_folder}")
            api.upload(file)
            print(f"Successfully uploaded {file.name} to {args.target_folder}")
        print("Done!")
    except KeyboardInterrupt:
        print("Cancelled.")
        exit(0)
    except Exception as ex:
        print("ERROR: %s" % ex, file=stderr)
        print(file=stderr)
        print(
            'Please make sure your reMarkable is connected to this PC and you have enabled the USB Webinterface in "Settings -> Storage".',
            file=stderr,
        )
        exit(1)
    finally:
        for file in args.file:
            file.close()


if __name__ == "__main__":
    main()
