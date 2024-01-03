#!/usr/bin/env python3
"""
Export - Exports all files of the remarkable onto your PC as pdfs.

Info: If a file is already exported, it will get skipped by default.
"""


from . import api

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
from os import makedirs, utime
from os.path import exists, getmtime
from sys import stderr
from time import time
import logging

# ------------------------------
# Config:
DEBUG = False
LOGGER = logging.getLogger()
# ------------------------------


def local_time_offset():
    now_timestamp = time()
    return (
        datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    ).total_seconds()


def exportTo(
    files,
    targetFolderPath,
    onlyNotebooks,
    onlyBookmarked,
    updateFiles,
    onlyPathPrefix=None
):
    # Preprocessing filterPath:
    if onlyPathPrefix is not None:
        if onlyPathPrefix.startswith("/"):
            onlyPathPrefix = onlyPathPrefix[1:]
        onlyPathPrefix = onlyPathPrefix.lower()
        if onlyPathPrefix == "":
            onlyPathPrefix = None

    exportableFiles = list(
        filter(lambda rmFile: rmFile.isFolder is False, api.iterateAll(files))
    )

    # Apply filter:
    if onlyPathPrefix is not None:
        exportableFiles = list(
            filter(
                lambda rmFile: rmFile.path().lower().startswith(onlyPathPrefix),
                exportableFiles,
            )
        )

    # Filter for only notebooks if requested:
    if onlyNotebooks:
        exportableFiles = list(
            filter(lambda rmFile: rmFile.isNotebook, exportableFiles)
        )

    # Filter for only bookmared if requested:
    if onlyBookmarked:
        exportableFiles = list(
            filter(lambda rmFile: rmFile.isBookmarked, exportableFiles)
        )

    totalExportableFiles = len(exportableFiles)

    lastDirectory = None
    for i, exportableFile in enumerate(exportableFiles):
        # Announce directory change:
        directory = exportableFile.parentFolderPath()
        if directory != lastDirectory:
            str_directory = ("<reMarkable Document Root>" if not directory else directory)
            LOGGER.info(
                f"Current folder: {str_directory}"
            )
            lastDirectory = directory

        # Get full path:
        path = exportableFile.path(targetFolderPath)
        if not path.endswith(".pdf"):
            path += ".pdf"

        # Create necessary directories:
        parentDir = exportableFile.parentFolderPath(targetFolderPath)
        if parentDir:  # May be None in the root
            try:
                makedirs(parentDir, exist_ok=True)
            except Exception as ex:
                LOGGER.error('Failed to create directories: "%s"' % parentDir)
                raise ex

        # Check if file needs to be downloaded and output appropriate messages:
        skipFile = False
        if exists(path):
            # Existing exported file:
            if updateFiles:
                if int(getmtime(path)) < int(
                    exportableFile.modifiedTimestamp + local_time_offset()
                ):
                    # Update outdated export:
                    LOGGER.info(
                        "[%d/%d] Updating file '%s'..."
                        % (i + 1, totalExportableFiles, exportableFile.name)
                    )
                else:
                    # Skip file that is up-to-date:
                    skipFile = True
                    LOGGER.warn(
                        "[%d/%d] Skipping unchanged file '%s'..."
                        % (i + 1, totalExportableFiles, exportableFile.name)
                    )
            else:
                # Don't override files. Regardless of date:
                skipFile = True
                LOGGER.info(
                    "[%d/%d] Skipping file '%s' (already exists in your target folder)..."
                    % (i + 1, totalExportableFiles, exportableFile.name)
                )

        if not exists(path):
            LOGGER.info(
                "[%d/%d] Exporting '%s'..."
                % (i + 1, totalExportableFiles, exportableFile.name)
            )

        # Export file if necessary:
        if not skipFile:
            try:
                exportableFile.exportPdf(path)
            except Exception as ex:
                LOGGER.error(
                    'Failed to export "%s" to "%s"' % (exportableFile.name, path)
                )
                raise ex
            try:
                local_mod_time = exportableFile.modifiedTimestamp + local_time_offset()
                utime(
                    path, (local_mod_time, local_mod_time)
                )  # Use timestamp from the reMarkable device
            except Exception as ex:
                LOGGER.error('Failed to change timestamp for exported file "%s"' % path)
                raise ex


def entry_point(args):

    targetFolder, onlyNotebooks, onlyBookmarked, updateFiles, onlyPathPrefix = (
        args.target_folder,
        args.only_notebooks,
        args.only_bookmarked,
        args.update,
        args.only_path_prefix,
    )

    # Print info regarding arguments:
    if updateFiles:
        LOGGER.info(
            "Updating files that have been changed recently. (Does not delete old files.)"
        )
    if onlyNotebooks:
        LOGGER.info("Export only notebooks.")
    if onlyBookmarked:
        LOGGER.info("Export only bookmarked files.")
    if onlyPathPrefix:
        LOGGER.info(
            "Only exporting files whose path begins with given filter (case insensitive)."
        )

        # Actual process:
        LOGGER.info("Fetching file structure...")
        files = api.fetchFileStructure()
        exportTo(
            files,
            targetFolder,
            onlyNotebooks,
            onlyBookmarked,
            updateFiles,
            onlyPathPrefix
        )
        LOGGER.info("Done!")

def main():

    # Disclaimer:
    LOGGER.warn(
        "DISCLAIMER: Please be aware that this puts the STRAIN of creating exported pdf files on YOUR REMARKABLE DEVICE rather than this computer.\n"
        "This can lead to UNEXPECTED BEHAVIOUR when many and/or big files are being exported.\n"
        "I WON'T TAKE ANY RESPONSIBILITY for potential damage this may induce!\n"
    )

    # Argument parsing:
    ap = ArgumentParser(
        description=__doc__, formatter_class=RawDescriptionHelpFormatter
    )

    ap.add_argument("target_folder", help="Base folder to put the exported files in")

    ap.add_argument(
        "-n",
        "--only-notebooks",
        action="store_true",
        default=False,
        help="Skips all files except notebooks",
    )

    ap.add_argument(
        "-b",
        "--only-bookmarked",
        action="store_true",
        default=False,
        help="Skips all files except bookmarked",
    )

    ap.add_argument(
        "-f",
        "--only-path-prefix",
        metavar="path",
        default="",
        help="Skips all files that DON'T starts with the given path (case-insensitive)",
    )

    ap.add_argument(
        "-u",
        "--update",
        action="store_true",
        default=False,
        help="Overrides/Updates all updated files. Does not remove deleted files!",
    )

    args = ap.parse_args()

    try:
        entry_point(args)
    except KeyboardInterrupt:
        LOGGER.debug("Cancelled.")
        exit(0)
    except Exception as ex:
        # Error handling:
        if DEBUG:
            raise ex
            exit(1)
        else:
            LOGGER.error("%s" % ex)
            LOGGER.error(
                'Please make sure your reMarkable is connected to this PC and you have enabled the USB Webinterface in "Settings -> Storage".'
            )
            exit(1)


if __name__ == "__main__":
    main()
