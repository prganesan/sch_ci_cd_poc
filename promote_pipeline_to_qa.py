import sys
import argparse
import time
from streamsets.sdk import ControlHub
#ControlHub.VERIFY_SSL_CERTIFICATES = False

parser = argparse.ArgumentParser()
parser.add_argument("--pipeline_id", help="Pipeline to be exported from Dev Environment")
parser.add_argument("--dev_sch_url", help="Control Hub URL for Dev Environment")
parser.add_argument("--dev_sch_user", help="Control Hub User for Dev Environment")
parser.add_argument("--dev_sch_password", help="Control Hub Password for Dev Environment")
parser.add_argument("--qa_pipeline_name", help="Pipeline Name for QA Environment")
parser.add_argument("--qa_sch_url", help="Control Hub URL for QA Environment")
parser.add_argument("--qa_sch_user", help="Control Hub User for QA Environment")
parser.add_argument("--qa_sch_password", help="Control Hub Password for QA Environment")


args = parser.parse_args()

dev_control_hub = ControlHub(server_url=args.dev_sch_url,username=args.dev_sch_user,password=args.dev_sch_password)
pipeline_list = dev_control_hub.pipelines.get_all(pipeline_id=args.pipeline_id)
pipeline_export_data = dev_control_hub.export_pipelines(pipelines=pipeline_list)
pipeline_export_data
with open ('./sch_pipeline_exports.zip', 'wb') as output_file:
    output_file.write(pipeline_export_data)
qa_control_hub = ControlHub(server_url=args.qa_sch_url,username=args.qa_sch_user,password=args.qa_sch_password)
with open('./sch_pipeline_exports.zip', 'rb') as input_file:
    pipelines_zip_data = input_file.read()
pipelines = qa_control_hub.import_pipelines_from_archive(archive=pipelines_zip_data,
                                              commit_message='Exported as zip from sdc')
