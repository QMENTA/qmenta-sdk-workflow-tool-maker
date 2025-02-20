# qmenta-sdk-workflow-tool-maker
Example showing how you can create a workflow using a tool you have developed and already available QMENTA tools

## Setup

Clone this repository into your local environment.


### Install requirements

You will need a python environment with version 3.8 or higher.

Install the python packages required: 

```bash
pip install -r requirements.txt
```
### Enable Docker

Install docker: https://docs.docker.com/engine/install/ubuntu/

Start the docker daemon: 

```bash
systemctl start docker
```

## Local test

To run this, FreeSurfer 7.4.1 must be installed
in your computer. You can download it here and follow the instructions:
[Download and install Freesurfer 7.4.1](https://surfer.nmr.mgh.harvard.edu/fswiki/rel7downloads).

Then, run using pytest the local testing, make sure the data is found inside the `local/test/sample_data` folder and that in the
file `local/test/test_tool.py` the path to the file is properly set. 
```bash
pytest local_tools/recon_all_clinical/local/test/test_tool.py::TestTool::test_basic_call
```