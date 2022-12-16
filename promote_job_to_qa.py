import logging
import sys
import argparse
import time
from streamsets.sdk import ControlHub
from zipfile import ZipFile
import json
import os

#ControlHub.VERIFY_SSL_CERTIFICATES = False

logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser()
parser.add_argument("--pipeline_id", help="Pipeline ID for QA Environment")
parser.add_argument("--pipeline_name", help="Pipeline Name for QA Environment")
parser.add_argument("--sch_url", help="Control Hub URL for QA Environment")
parser.add_argument("--sch_user", help="Control Hub User for QA Environment")
parser.add_argument("--sch_password", help="Control Hub Password for QA Environment")
parser.add_argument("--topic_name", help="Kafka Topic for QA Environment")
parser.add_argument("--index_name", help="Elastic Search Index for QA Environment")
parser.add_argument("--consumer_group_name", help="Kafka Consumer Group Name for QA Environment")
args = parser.parse_args()
pipeline_id = args.pipeline_id
pipeline_name = args.pipeline_name
topic_name = args.topic_name
index_name = args.index_name
consumer_group_name = args.consumer_group_name
job_name = "QA Job For " + pipeline_name
lib_list=""

runtime_params = {'Topic_Name': topic_name,'Index_Name': index_name, 'Consumer_Group_Name': consumer_group_name}

qa_control_hub = ControlHub(server_url=args.sch_url,username=args.sch_user,password=args.sch_password)

pipeline_ = qa_control_hub.pipelines.get(pipeline_id=pipeline_id)



#jobs_to_upgrade = [job for job in qa_control_hub.jobs.get_all(pipeline_id=pipeline_id)
#                               if (job.pipeline_commit_label != f'v{pipeline_.version}' and job.data_collector_labels == ['prasanna-azure-qa'] )]
jobs_to_upgrade = [job for job in qa_control_hub.jobs.get_all(pipeline_id=pipeline_id)
                               if (job.data_collector_labels == ['prasanna_adda_qa'] )]

if jobs_to_upgrade:
   logger.info('Upgrading QA jobs: %s ...', ', '.join(str(job) for job in jobs_to_upgrade))
   qa_control_hub.upgrade_job(*jobs_to_upgrade)
else:
    logger.info('Creating Job in QA environment')
    job_builder = qa_control_hub.get_job_builder()
    job = job_builder.build(job_name,
                        pipeline=pipeline_,
                        runtime_parameters=runtime_params)
    job.data_collector_labels=['prasanna_adda_qa']
        
    qa_control_hub.add_job(job)
#qa_control_hub.start_job(job)

#Compile list of required stage libraries for the pipeline
#for stage in pipeline_.stages:
#  lib_list = lib_list + stage.library + ","

#lib_list = lib_list[:-1]
#print ('##vso[task.setvariable variable=lib_list]'+lib_list)
