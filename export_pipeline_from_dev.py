import sys
import argparse
import time
from streamsets.sdk import ControlHub
from zipfile import ZipFile
#ControlHub.VERIFY_SSL_CERTIFICATES = False

parser = argparse.ArgumentParser()
parser.add_argument("--pipeline_id", help="Pipeline to be exported from Dev Environment")
parser.add_argument("--dev_sch_url", help="Control Hub URL for Dev Environment")
parser.add_argument("--dev_sch_user", help="Control Hub User for Dev Environment")
parser.add_argument("--dev_sch_password", help="Control Hub Password for Dev Environment")



args = parser.parse_args()

dev_control_hub = ControlHub(server_url=args.dev_sch_url,username=args.dev_sch_user,password=args.dev_sch_password)
pipeline_list = dev_control_hub.pipelines.get_all(pipeline_id=args.pipeline_id)
pipeline_export_data = dev_control_hub.export_pipelines(pipelines=pipeline_list)
pipeline_export_data
with open ('./sch_pipeline_exports.zip', 'wb') as output_file:
    output_file.write(pipeline_export_data)
with ZipFile('./sch_pipeline_exports.zip', 'r') as zipObj:
   # Extract all the contents of zip file in current directory
   zipObj.extractall()


