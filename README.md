# Tractography Processing Pipeline

## Overview

This repository contains a Python script for processing tractography data using MRtrix3 commands. The script processes `.tck` files by filtering and resampling streamlines based on specific regions of interest (ROIs), counts the fibers, and generates a PDF report. Additionally, the script makes use of ANTs (Advanced Normalization Tools) for preprocessing and registration of the neuroimaging data.

## Prerequisites

### Software Dependencies
- Python 3.x: The script is written in Python and requires Python 3.x.
- MRtrix3: This software suite is used for processing tractography data. (https://www.mrtrix.org)
- ANTs (Advanced Normalization Tools)**: Used for preprocessing and registration of the neuroimaging data. Ensure that ANTs is installed and accessible in your system's PATH.(https://github.com/ANTsX/ANTs.git)
- nibabel: For handling neuroimaging data formats.
- matplotlib: For generating the PDF report with fiber counts.

### Python Packages
You can install the necessary Python packages using pip:

```bash
pip install nibabel matplotlib pandas
