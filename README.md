# Impact of Import instructions on code complexity

## Project Structure

- **`/cam`** — this directory contains scripts that are used to scrape, filter and calculate complexity metrics over a given dataset. This directory is a  fork of the [cam-0.9.3](https://github.com/yegor256/cam) repository, optimized and enhanced with features, specific for study impact of import instructions on code complexity
- **`/cam/dataset/data`** — Directory that contains results with calculated complexity metrics over each Java repository from dataset
- **`main.ipynb`** — A IPYNB notebook used for data analysis.

## Steps to Reproduce the Results

0. **[Optional] Regenerate the Dataset**:

    Download dataset [data.zip](https://github.com/yegor256/cam/releases/download/0.1.1/cam-2021-07-08.zip) unzip `w/dataset/github` directory into `cam/datatset/github` to store initial raw data
    
    Go into the script directory and follow the steps in its README.md to metrics dataset. As calculation finished, `cam/dataset/data` would contain required metrics.

2. **Set Up Python Environment**:  
   Install Python version 3.10 or above and create a virtual environment called `.venv`:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Required Packages**:  
   Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Jupyter Notebook**:  
   Launch Jupyter Notebook and open `main.ipynb` to begin the analysis.
