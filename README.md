# Scribd Image Downloader

Sometimes, you really want to download a file off of Scribd, but you find the download fails repeatedly or the download completes but results in a corrupt file.

If all the files in the Scribd document are images, more specifically .jpg files, this script will help you download all the images and convert them to a pdf.

This script uses **multiprocessing** to speed up the downloading process. However, it doesn't account for any rate limits that might exist while downloading.

# Dependencies

This script requires the modules **requests** and **img2pdf**.

These can be downloaded from Pypi by using the following commands through the command line interface.

    pip install requests
    pip install img2pdf

# Usage

This module doesn't check for correctness of the Scribd link, or the existence of the `img_folder` and `output_folder` directories.

This script is to be run at the command line by running

    python scribd_downloader1.py

from the folder the script resides in.

Enter the scribd link, pdf file name, path of the directory to which the images will be downloaded, path of the directory where the pdf will be created separated by spaces

Enter the number of processes that will be running.

You can change the `DEBUG` variable inside the script to True, to see a list of images that have downloaded (updated realtime).