# evGrandPrix-Simulator

This repository contains documentation and files supporting the R. B. Annis evGrandPrix Simulator project. The team behind this project aims to design, develop, and prototype an platform that emulates the stresses of a gokart racing around a track. This is to be done using only the powertrain for the kart (motor, batteries, controllers, etc) to ensure that the components will endure the race.

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

   - On Windows:

     ```
     venv/Scripts/activate.bat //In CMD
     venv/Scripts/Activate.ps1 //In Powershel
     ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

# File Structure
This repository is divided in 3 sections: `Dyno`, `Kart`, `TorqueSensor`. Each of them include the code controlling that specific subsytem. 
