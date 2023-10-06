# rmWebUiTools

[![Mentioned in Awesome reMarkable](https://awesome.re/mentioned-badge.svg)](https://github.com/reHackable/awesome-reMarkable)

This is a collection of scripts that utilize the reMarkable USB webinterface to export files.


## DISCLAIMER

Using the export functionality, the script will prompt your device to **export every single file** onto your pc.
This will - as of now - lead to freezes and other problems, as the software is not specifically suited for this usecase.

I (and reMarkable AS too) **WON'T take any responsibility** for potential damage done to your device using this software.


## Installation

Run the following command:

```sh
pip install git+pip install git+https://github.com/seblemaguer/rmWebUiTools.git@executables
```

## Usage

The repository provides the following commands:

  - `rm_export` to copy the files from the remarkable to a local folder to specify
  - `rm_import` to copy a local PDF/EPUB file to a given target folder on the remarkbable
  - `rm_tree` which lists the filetree of the remarkable
  - `rm_stats` which provides some statistics about the content of the remarkable

## Possibilities

Right now, you can export/mirror all your files into a specified folder, export only changed files or view general information using on of the various scripts available.

You can also make your own scripts using the `api.py` and give you access to all metadata provided by the reMarkable USB webinterface. An example of such information can be found in the file `.exampleRootMetadata.json`.

There is certainly a lot more possible than currently provided.
If you want a certain feature, you can create an issue (= feature request) or contribute it yourself.


## Common problem

When exporting a large amount of files, it can happen that your reMarkable **enters sleep mode** during that process or **locks up and restarts** (happens on some huge pdf files).

When this happens, you can just execute the same command again. It should continue where it failed with no data loss.
