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
parser.add_argument("--qa_pipeline_name", help="Pipeline Name for QA Environment")
parser.add_argument("--qa_sch_url", help="Control Hub URL for QA Environment")
parser.add_argument("--qa_sch_user", help="Control Hub User for QA Environment")
parser.add_argument("--qa_sch_password", help="Control Hub Password for QA Environment")


args = parser.parse_args()


qa_control_hub = ControlHub(server_url=args.qa_sch_url,username=args.qa_sch_user,password=args.qa_sch_password)
exported_json = args.qa_pipeline_name + '.json'
with open(exported_json, 'r') as input_file:
    pipeline_json = json.load(input_file)

pipeline = qa_control_hub.import_pipeline(pipeline=pipeline_json,
                               commit_message='Promoted pipeline from Dev',
                               name=args.qa_pipeline_name)
