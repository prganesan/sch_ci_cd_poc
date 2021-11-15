import logging
import string
import time
import json
import pytest
import sys
import argparse
from subprocess import Popen, PIPE

from kafka.admin import KafkaAdminClient
from streamsets.testframework.utils import get_random_string
from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser()


parser.add_argument("--sch-server-url", help="SCH URL")
parser.add_argument("--sch-username", help="SCH Username")
parser.add_argument("--sch-password", help="SCH Password")
parser.add_argument("--pipeline_id", help="Pipeline Id")
parser.add_argument("--elasticsearch-url", help="Elastic Search URL")
parser.add_argument("--cluster-server", help="Kafka Cluster Broker URL")
parser.add_argument("--kafka-version", help="Kafka Version")
parser.add_argument("--kafka-zookeeper", help="Kafka Zookeeper")
#parser.add_argument("--upgrade-jobs", help="Kafka Version")
#parser.add_argument("--junit-xml", help="Junit")

args = parser.parse_args()


#Generate a Random Topic Name and Job Name
job_name = get_random_string(string.ascii_lowercase)
index_name=job_name
consumer_group_name=job_name
topic_name=job_name
SAMPLE_DATA1 = dict(FirstName='MAURICE', LastName='GARIN',EmpId=1)
SAMPLE_DATA2 = dict(FirstName='LUCIEN', LastName='POTHIER',EmpId=2)
SAMPLE_DATA3 = dict(FirstName='FERNAND', LastName='AUGEREAU', EmpId=3)


def test_complete(elasticsearch_data):
    """Test that first name and last name are split as expected."""
    EXPECTED_NAMES = [dict(FirstName='MAURICE', LastName='GARIN' , EmpId=1),
                      dict(FirstName='LUCIEN', LastName='POTHIER',EmpId=2),
                      dict(FirstName='FERNAND', LastName='AUGEREAU',EmpId=3)]
    assert EXPECTED_NAMES == [{key: record[key] for key in ['FirstName', 'LastName', 'EmpId']}
                              for record in elasticsearch_data]


@pytest.fixture(scope='module')
def elasticsearch_data(sch, pipeline, cluster,elasticsearch):

    """Send basic messages to Kafka"""
    producer = cluster.kafka.producer()
    producer.send(topic_name, json.dumps(SAMPLE_DATA1).encode('utf-8'))
    producer.send(topic_name, json.dumps(SAMPLE_DATA2).encode('utf-8'))
    producer.send(topic_name, json.dumps(SAMPLE_DATA3).encode('utf-8'))
    logger.info('broker_configs %s ...',sys.argv)
    runtime_params = {'Topic_Name': topic_name,'Index_Name': index_name, 'Consumer_Group_Name': consumer_group_name}
    #admin_client = KafkaAdminClient(bootstrap_servers="172.28.0.4:9092", client_id='test',security_protocol="PLAINTEXT")
    admin_client = KafkaAdminClient(bootstrap_servers=args.cluster-server, client_id='test',security_protocol="PLAINTEXT")
    #es1 = Elasticsearch([{"host":"172.28.0.4","port":9200}])
    es1 = Elasticsearch([{"host":args.elasticsearch-url,"port":9200}])

    try:
        mapping = '''
        {
           "mappings": {
              "properties" : {
                 "FirstName": {
                   "type": "text"
                  },
                 "LastName": {
                   "type": "text"
                  },
                "EmpId": {
                   "type": "integer"
                 }
              }

          }
        }'''

        es1.indices.create(index=index_name,body=mapping,ignore=400)
        #time.sleep(5)
        logger.info('Creating test job ...')
        job_builder = sch.get_job_builder()
        logger.info('Creating test job ...')
        #pipeline.parameters.update(runtime_params)
        job_builder = sch.get_job_builder()
        job = job_builder.build(job_name,
                                pipeline=pipeline,
                                runtime_parameters=runtime_params)
        job.description = 'CI/CD test job'
        job.data_collector_labels = ['prasanna-azure-dev']
        sch.add_job(job)
        sch.start_job(job)
        #Wait for records to be written.
        time.sleep(5)

        
        data_in_elasticsearch = [hit['_source'] for hit in elasticsearch.client.search(index=index_name)]
        yield data_in_elasticsearch
    finally:
        #Stop Job
        sch.stop_job(job)
        #Delete Job
        sch.delete_job(job)
        logger.info('Deleting dummy data from %s ... ', job_name)
        admin_client.delete_topics([topic_name],1000)

        logger.info('Deleting Elasticsearch index %s ...', index_name)
        elasticsearch.client.delete_index(index_name)
