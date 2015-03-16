# Scribd Image Downloader

Sometimes, you really want to download a file off of Scribd, but you find the download fails repeatedly or the download completes but results in a corrupt file.

If all the files in the Scribd document are images, more specifically .jpg files, this script will help you download all the images and convert them to a pdf.

# Dependencies

This script requires the modules **requests** and **img2pdf**.

These can be downloaded from Pypi by using the following commands through the command line interface.

    pip install requests
    pip install img2pdf

# Usage

This module doesn't check for correctness of the Scribd link, or the existence of the `img_folder` and `output_folder` directories.

To use this script, you can either:

- change the variable values inside the script
- run it from the command line interface or on your IDE.

To use it on your IDE,

    get_pdf(scribd_url, pdf_file_name, img_directory, output_directory)