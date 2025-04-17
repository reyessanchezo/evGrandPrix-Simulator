# Dyno Directory

This directory contains all files related to the dyno, including the scripts and programs used to control and monitor the motor controller.

## Contents

- **Python Scripts**  
  Python files used for data collection, analysis, and communication with the motor controller.

- **Lisp Script**  
  The primary program (`vesc.lisp`) that runs continuously on the motor controller.

## Requirements

### Python

To run the Python scripts, install the following libraries:

- `matplotlib`
- `pyserial`
- `python-can`
- `pyusb`

You can install them using `pip`:

```bash
pip install matplotlib pyserial pyusb python-can
```

### Lisp

To run the Lisp code, you will need to install a Lisp interpreter.  
For Mac users, follow this guide: [How to install Lisp on macOS](https://www.geeksforgeeks.org/how-to-install-lisp-on-macos/).
