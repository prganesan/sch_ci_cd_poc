import logging
import string
import time
import json
import pytest
from subprocess import Popen, PIPE

from kafka.admin import KafkaAdminClient
from streamsets.testframework.utils import get_random_string

logger = logging.getLogger(__name__)
#Generate a Random Topic Name and Job Name
job_name = get_random_string()

SAMPLE_DATA = [dict(FirstName='MAURICE', LastName='GARIN',EmployeeId='1'),
               dict(FirstName='LUCIEN', LastName='POTHIER',EmployeeId='2'),
               dict(FirstName='FERNAND', LastName='AUGEREAU', EmployeeId='3')]

        
def test_complete(elasticsearch_data):
    """Test that first name and last name are split as expected."""
    EXPECTED_NAMES = [dict(FirstName='Maurice', LastName='Garin' , EmployeeId='1'),
                      dict(FirstName='Lucien', LastName='Pothier',EmployeeId='2'),
                      dict(FirstName='Fernand', LastName='Augereau',EmployeeId='3')]
    assert EXPECTED_NAMES == [{key: record[key] for key in ['FirstName', 'LastName', 'EmployeeId']}
                              for record in elasticsearch_data]


@pytest.fixture(scope='module')
def elasticsearch_data(sch, pipeline, cluster,elasticsearch):
    
    """Send basic messages to Kafka"""
    producer = cluster.kafka.producer()
    producer.send(job_name, SAMPLE_DATA)
    #logger.info('broker_configs %s ...',broker_configs)
    runtime_params = {'Topic_Name': job_name,'Index_Name': job_name}
    #admin_client = KafkaAdminClient(bootstrap_servers="node-1.cluster:9092", client_id='test',security_protocol='SASL_PLAINTEXT',sasl_mechanism='GSSAPI',sasl_kerberos_service_name='kafka')
    admin_client = KafkaAdminClient(bootstrap_servers="172.28.0.4:9092", client_id='test',security_protocol="PLAINTEXT")

    try:
        logger.info('Creating test job ...')
        job_builder = sch.get_job_builder()
        logger.info('Creating test job ...')
        #pipeline.parameters.update(runtime_params)
        job_builder = sch.get_job_builder()
        job = job_builder.build(job_name,
                                pipeline=pipeline,
                                runtime_parameters=runtime_params)
        job.description = 'CI/CD test job'
        job.data_collector_labels = ['prasanna-azure']
        sch.add_job(job)
        sch.start_job(job)
        #Wait for records to be written.
        time.sleep(5)

        data_in_elasticsearch = [hit['_source'] for hit in elasticsearch.client.search(index=index)]
        yield data_in_elasticsearch
    finally:
        #Stop Job
        sch.stop_job(job)
        #Delete Job
        sch.delete_job(job)
        logger.info('Deleting dummy data from %s ... ', job_name)
        admin_client.delete_topics([job_name],1000)
        
        logger.info('Deleting Elasticsearch index %s ...', index)
        elasticsearch.client.delete_index(index)
