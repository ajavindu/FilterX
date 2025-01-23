#!/usr/bin/env python
# coding: utf-8

# Import necessary libraries
import os
import numpy as np
import subprocess  # To run shell commands
import nibabel as nib  # To handle neuroimaging data formats
import matplotlib.pyplot as plt  # For plotting
from matplotlib.backends.backend_pdf import PdfPages  # For generating PDF reports

# Function to run tckedit, which edits or filters streamlines in a tractography file (.tck)
def run_tckedit(tract_path, roi_paths, output_tract_path, inverse=False):
    """
    Runs the MRtrix3 command tckedit to edit or filter streamlines in a .tck file.

    Parameters:
    - tract_path: Path to the input .tck file.
    - roi_paths: List of paths to ROI files used for filtering the streamlines.
    - output_tract_path: Path where the output .tck file will be saved.
    - inverse: If True, apply the inverse of the ROI-based filtering.

    Returns:
    - None
    """
    # Initialize the command with tckedit and the input/output paths
    cmd = ["tckedit", tract_path, output_tract_path]
    
    # Add the ROI inclusion criteria to the command
    for roi in roi_paths:
        cmd += ["-include", roi]
    
    # If inverse is True, append the inverse flag
    if inverse:
        cmd.append("-inverse")
    
    # Execute the command and handle errors
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running tckedit: {e}")

# Function to run tckresample, which resamples streamlines in a tractography file (.tck)
def run_tckresample(tract_path, output_tract_path):
    """
    Runs the MRtrix3 command tckresample to resample streamlines in a .tck file.

    Parameters:
    - tract_path: Path to the input .tck file.
    - output_tract_path: Path where the resampled .tck file will be saved.

    Returns:
    - None
    """
    try:
        subprocess.run(["tckresample", tract_path, output_tract_path, "-endpoints"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running tckresample: {e}")

# Function to count the number of fibers in a .tck file
def count_fibers(tck_path):
    """
    Counts the number of streamlines (fibers) in a .tck file.

    Parameters:
    - tck_path: Path to the .tck file.

    Returns:
    - The number of streamlines (int) or None if an error occurs.
    """
    try:
        tck = nib.streamlines.load(tck_path)  # Load the .tck file
        return len(tck.streamlines)  # Return the number of streamlines
    except Exception as e:
        print(f"Error reading {tck_path}: {e}")
        return None

# Function to process a single tract file with its associated ROIs
def process_tract_file(tract_file, roi_files, directory):
    """
    Processes a single tract file with its associated ROIs.

    Parameters:
    - tract_file: Name of the tract file to be processed.
    - roi_files: Dictionary mapping tract files to their respective ROIs.
    - directory: The directory containing the tract and ROI files.

    Returns:
    - A dictionary containing the fiber counts and endpoint file paths.
    """
    tract_path = os.path.join(directory, tract_file)
    roi_paths = [os.path.join(directory, roi) for roi in roi_files[tract_file]]
    output_path = os.path.join(directory, tract_file.replace('.tck', '_ICPED.tck'))
    output_inv_path = os.path.join(directory, tract_file.replace('.tck', '_ICPED_inv.tck'))

    # Run tckedit for both standard and inverse cases
    run_tckedit(tract_path, roi_paths, output_path)
    run_tckedit(tract_path, roi_paths, output_inv_path, inverse=True)

    # Generate resampled endpoint files
    output_ep_path = output_path.replace('.tck', '_ep.tck')
    output_inv_ep_path = output_inv_path.replace('.tck', '_ep.tck')
    run_tckresample(output_path, output_ep_path)
    run_tckresample(output_inv_path, output_inv_ep_path)

    # Return fiber counts and endpoint file paths
    return {
        "original": count_fibers(tract_path),
        "processed": count_fibers(output_path),
        "inverse_processed": count_fibers(output_inv_path),
        "endpoint_files": [output_ep_path, output_inv_ep_path]
    }

# Main function to orchestrate the processing
def main(directory):
    """
    Main function to orchestrate the processing of tract files.

    Parameters:
    - directory: The directory containing the tract and ROI files.

    Returns:
    - None
    """
    import pandas as pd

    # Initialize a list to store fiber count results
    fiber_count_results = []

    # Define the tractography and ROI files to be processed
    tract_files = ['CST_L.tck', 'CST_R.tck']
    roi_files = {
        'CST_L.tck': ['LPIC_binary.nii.gz', 'LCP_binary.nii.gz'],
        'CST_R.tck': ['RPIC_binary.nii.gz', 'RCP_binary.nii.gz']
    }

    # Process each tract file
    for tract_file in tract_files:
        result = process_tract_file(tract_file, roi_files, directory)
        fiber_count_results.append({
            'TCK File': tract_file,
            'Fiber Count': result["original"]
        })
        fiber_count_results.append({
            'TCK File': tract_file.replace('.tck', '_ICPED.tck'),
            'Fiber Count': result["processed"]
        })
        fiber_count_results.append({
            'TCK File': tract_file.replace('.tck', '_ICPED_inv.tck'),
            'Fiber Count': result["inverse_processed"]
        })

        # Print or save endpoint file information
        for endpoint_file in result["endpoint_files"]:
            print(f"Endpoint file: {endpoint_file}")

    # Convert the list of fiber counts to a DataFrame
    fiber_counts_df = pd.DataFrame(fiber_count_results)

    # Generate a PDF report with the fiber counts
    pdf_path = os.path.join(directory, 'fiber_counts.pdf')
    with PdfPages(pdf_path) as pdf:
        fig, ax = plt.subplots(figsize=(8, 4))  # Adjust the size as needed
        ax.axis('off')  # Hide the axes
        ax.table(cellText=fiber_counts_df.values, colLabels=fiber_counts_df.columns, loc='center')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

    print(f"PDF report generated: {pdf_path}")

# Entry point for the script
if __name__ == "__main__":
    directory = ''  # Specify the directory where files are located
    main(directory)
