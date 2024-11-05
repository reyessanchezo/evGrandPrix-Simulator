<!-- TODO: Add instructions to activate venv in Windows -->
<!-- TODO: Update requirements.txt so pip install . sets up everything. -->

# evGrandPrix-Simulator

This repository will contain documentation and files supporting the R. B. Annis evGrandPrix Simulator project. This project aims to build a dynamometer to simulate the stress of racing a gokart around a track and develop a simulator that can determine the optimal racing line given various kart parameters.

# Installation Instructions

Due to some issues with the PyVESC package structure and potential configuration changes, we'll be using the files directly from the PyVESC repository. Fortunately, the current project already includes the PyVESC package, as it is lightweight.

Follow these steps to set up your environment:

1. Clone the GitHub repository:

   ```bash
   git clone https://github.com/reyessanchezo/evGrandPrix-Simulator.git
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:

   - On Linux/Mac:

     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

(OPTIONAL)

If using conda:

2. Create new conda environment
```bash
conda env create -f environment.yml
```

3. Activate conda environment
```bash
conda activate pyvesc
```
