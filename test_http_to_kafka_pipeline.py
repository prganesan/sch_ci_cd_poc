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

def test_1(sch):
    assert 1 == 1

def test_complete(kafka_data):
    """Smoke test for the http_to_kafka pipeline."""
    # Expected Data in Kafka
    EXPECTED_RECORDS = [{'price': '50274.11', 'coin': 'BTC'}]
    for record in kafka_data:
        assert [record] == EXPECTED_RECORDS


def setup():
    rm_krb5_args = [ '/bin/rm','/etc/sdc/krb5.conf' ]
    subp1 = Popen(rm_krb5_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    subp1.wait()
    cp_krb5_args = [ '/bin/cp','/etc/testframework/krb5.conf', '/etc/' ]
    subp2 = Popen(cp_krb5_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    subp2.wait()
    kinit_args = [ '/usr/bin/kinit', '-kt', '/etc/testframework/sdc.keytab', 'sdctest@CLUSTER' ]
    subp3 = Popen(kinit_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    subp3.wait()


@pytest.fixture(scope='module')
def kafka_data(sch, pipeline, cluster):
    setup()
    configs = cluster.kafka._get_consumer_producer_params()
    #broker_configs = cluster.kafka._handle_kafka_broker_configs(None)
    logger.info('Is Kafka Kerberized %s ...',cluster.kafka.is_kerberized)
    logger.info('sdc_stage_configurations %s ...',cluster.sdc_stage_configurations)
    logger.info('_get_consumer_producer_params %s ...',cluster.kafka._get_consumer_producer_params())
    #logger.info('broker_configs %s ...',broker_configs)
    runtime_params = {'OriginURL':'http://mockserver:8080/castlemock/mock/rest/project/pk7Aiv/application/uRvAzU/ticker','Topic_Name': job_name}
    #admin_client = KafkaAdminClient(bootstrap_servers="node-1.cluster:9092", client_id='test',security_protocol='SASL_PLAINTEXT',sasl_mechanism='GSSAPI',sasl_kerberos_service_name='kafka')
    admin_client = KafkaAdminClient(bootstrap_servers=configs.get('bootstrap_servers'), client_id='test',security_protocol=cluster.kafka.security_protocol,sasl_mechanism=configs.get('sasl_mechanism'),sasl_kerberos_service_name='kafka')

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
        job.data_collector_labels = ['cicd']
        sch.add_job(job)
        sch.start_job(job)
        #Wait for records to be written.
        time.sleep(5)

        consumer = cluster.kafka.consumer(consumer_timeout_ms=1000, auto_offset_reset='earliest')
        consumer.subscribe([job_name])

        #Read Back data from Kafka Topic
        data_in_kafka = [json.loads(msg.value.decode('latin1')) for msg in consumer]
        logger.info('Kafka data %s = ',data_in_kafka)
        #print(data_in_kafka)
        yield data_in_kafka
    finally:
        #Stop Job
        sch.stop_job(job)
        #Delete Job
        sch.delete_job(job)
        logger.info('Deleting dummy data from %s ... ', job_name)
        admin_client.delete_topics([job_name],1000)
