import glob
import logging
import os
import shlex
import subprocess

from qmenta.sdk.tool_maker.outputs import (
    Coloring,
    HtmlInject,
    OrientationLayout,
    PapayaViewer,
    Region,
    ResultsConfiguration,
    Split,
    Tab,
)
from qmenta.sdk.tool_maker.modalities import Modality, Tag
from qmenta.sdk.tool_maker.tool_maker import InputFile, Tool, FilterFile


class ReconAllClinical(Tool):
    def tool_inputs(self):
        """
        Define the inputs for the tool. This is used to create the settings.json file.
        More information on the inputs can be found here:
        https://docs.qmenta.com/sdk/guides_docs/settings.html
        """
        # Add the file selection method:
        self.add_input_container(
            title="Input recon-all-clinical",
            info="Required inputs:<br><b>&bull; T1</b>: anatomical 3D image<br>&ensp;Must be labeled as 'T1' modality.<br><b>&bull;",
            anchor=1,
            batch=1,
            container_id="input_data",
            mandatory=1,
            file_list=[
                InputFile(
                    file_filter_condition_name="c_t1",
                    filter_file=FilterFile(
                        modality=Modality.T1,
                    ),
                    mandatory=1,
                    min_files=1,
                    max_files=1,
                ),
            ],
        )


    def run(self, context):
        """
        This is the main function that is called when the tool is run.
        """
        # ================ #
        # GETTING THINGS READY
        logger = logging.getLogger("main")
        logger.info("Tool starting")

        # Downloads all the files and populate the variable self.inputs with the handlers and parameters
        context.set_progress(message="Downloading input data and setting self.inputs object")
        self.prepare_inputs(context, logger)

        t1_input = self.inputs.input_data.c_t1[0].file_path

        subject_dir = os.path.join(os.environ["WORKDIR"], "FS_OUTPUT")
        os.environ["SUBJECTS_DIR"]=subject_dir
        os.makedirs(subject_dir, exist_ok=True)

        crop = f"tcsh $FREESURFER_HOME/bin/recon-all-clinical.sh {t1_input} sub-01 1 {subject_dir}"
        print(crop)
        subprocess.call(shlex.split(crop))

        fs = os.path.join(subject_dir, "FREESURFER")

        for filename in glob.glob(os.path.join(fs, "**"), recursive=True):
            path_file = filename.split("OUTPUT/")[1]
            if os.path.isfile(filename):
                context.upload_file(filename, path_file)

    def tool_outputs(self):
        # Main object to create the results configuration object.
        result_conf = ResultsConfiguration()

        # Add the tools to visualize files using the function add_visualization

        # Online 3D volume viewer: visualize DICOM or NIfTI files.
        papaya_1 = PapayaViewer(title="Tissue segmentation over T1", width="50%", region=Region.center)
        # the first viewer's region is defined as center

        # Add as many layers as you want, they are going to be loaded in the order that you add them.
        papaya_1.add_file(file="mri/brain.mgz", coloring=Coloring.grayscale)  # using the file name
        papaya_1.add_file(file="mri/aseg.mgz", coloring=Coloring.custom)
        # Add the papaya element as a visualization in the results configuration object.
        result_conf.add_visualization(new_element=papaya_1)

        papaya_2 = PapayaViewer(title="Labels segmentation over T1", width="50%", region=Region.right)
        # the second viewer's region is defined as right, this depends on the Split(), which has the element
        # orientation set to vertical. If it is set to horizontal, then you can choose between 'top' or 'bottom'.

        # You can use modality or tag of the output file to select the file to be shown in the viewer.
        papaya_2.add_file(file="mri/brain.mgz", coloring=Coloring.grayscale)  # using the file modality
        papaya_2.add_file(file="mri/aparc+aseg.mgz", coloring=Coloring.custom_random)  # using file tag
        result_conf.add_visualization(new_element=papaya_2)

        # To create a split, specify which ones are the objects to be shown in the split
        split_1 = Split(
            orientation=OrientationLayout.vertical, children=[papaya_1, papaya_2], button_label="Images"
        )

        # Call the function generate_results_configuration_file to create the final object that will be saved in the
        # tool path
        result_conf.generate_results_configuration_file(
            build_screen=split_1, tool_path=self.tool_path, testing_configuration=False
        )

def run(context):
    ReconAllClinical().tool_outputs()  # this can be removed if no results configuration file needs to be generated.
    ReconAllClinical().run(context)