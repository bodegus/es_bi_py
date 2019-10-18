import es_flow_feeder
from datetime import datetime
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
import os
import flowdock

# AWS Role that can be assumed to access elastic search
role = "placeholder value"
region = 'us-east-1'  # e.g. us-west-1
service = 'es'
flow_id = "4f26ad39-195e-4cd9-a75c-7077692f4b2c"
flow_name = "cc_flowdocktesting"
index = 'test5'
host = "placeholder value" 
org = "uhg"
userkey = os.environ['flowdock_key']

# Innitialize es
es = Elasticsearch(
    hosts=host,
    http_auth=es_flow_feeder.aws_auth_role(region, service, role),
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
    )


def test_aws_auth_role():
    # Expected Results
    now = datetime.now().strftime("%Y%m%d")

    # Generate Auth object
    auth = es_flow_feeder.aws_auth_role(region, service, role)

    # Asseter success by checking date provided
    assert auth.signing_key.date == now

def test_aws_auth_role_direct():
    # AWS Role that can be assumed to access elastic search
    role = None

    # Expected Results
    now = datetime.now().strftime("%Y%m%d")

    # Generate Auth object
    auth = es_flow_feeder.aws_auth_role(region, service, role)

    # Asseter success by checking date provided
    assert auth.signing_key.date == now

def test_es_next_message_id():

    # Generate Auth object
    res = es_flow_feeder.get_es_message_id(flow_id, index, es)

    # Asseter success by checking date provided
    assert type(res['hits']['total']['value']) == int


def test_get_next_message_id():

    # Generate Auth object
    message_id = es_flow_feeder.get_next_message_id(flow_id, index, es)

    # Asseter success by checking date provided
    assert type(message_id) == int
    assert message_id >= 0

def test_get_next_message_id_none():
    # set a different flow id with known result
    flow_id = "this flow does not exist"

    # Generate Auth object
    message_id = es_flow_feeder.get_next_message_id(flow_id, index, es)

    # Asseter success by checking date provided
    assert type(message_id) == int
    assert message_id == 0

def test_enrich_message():
    messages = [{'user': '189821', 'content': {'type': 'add_people', 'message': ['Charlie', 'Matthew', 'Emroz', 'Ashutosh', 'Santi']}, 'event': 'action', 'edited': None, 'emojiReactions': {}, 'tags': [], 'id': 9, 'sent': 1499354138298, 'attachments': [], 'thread_id': 'TGsO5wiHQQpvVYBSZ4Af8cQ4DcQ', 'app': 'chat', 'thread': {'id': 'TGsO5wiHQQpvVYBSZ4Af8cQ4DcQ', 'title': 'Added Charlie, Matthew, Emroz, Ashutosh, Santi to the flow.', 'body': '', 'external_url': None, 'status': None, 'actions': [], 'fields': [], 'source': None, 'activities': 0, 'internal_comments': 0, 'external_comments': 0, 'updated_at': '2017-07-06T15:15:38.298Z', 'created_at': '2017-07-06T15:15:38.000Z', 'initial_message': 9}, 'flow': '61f75e0e-edee-48f6-9c9a-156640d32409', 'created_at': '2017-07-06T15:15:38.298Z', 'edited_at': None}] # noqa
    result_message = {'user': '189821', 'content': None, 'event': 'action', 'edited': None, 'id': 9, 'sent': 1499354138298, 'thread_id': 'TGsO5wiHQQpvVYBSZ4Af8cQ4DcQ', 'app': 'chat', 'flow': '61f75e0e-edee-48f6-9c9a-156640d32409', 'created_at': '2017-07-06T15:15:38.298Z', 'edited_at': None, 'flow_name': flow_name} # noqa
    
    # Generate test result
    message = es_flow_feeder.enrich_message(messages, flow_name)

    # Asseter success by checking date provided
    assert type(message) == dict
    assert message['flow_name'] == flow_name
    assert message == result_message


def test_load_new_messages_none():

    result = es_flow_feeder.load_new_messages(flow_id, flow_name, index, org, userkey, host, region, service, role)


    if type(result) == str:
        assert result == "no new messages"

    elif type(result) == int:
        assert result >= 0

def test_load_new_messages_generate():
    org = "uhg"
    flow_id = "95f07574-4fc4-4450-a7f0-36d5d96ccc7e"
    flow_name = "cc_bi_unittests"
    userkey = os.environ['flowdock_key']

    # post new message
    message = "hello from test_load_new_messages_generate(): at " + str(datetime.now())
    r = flowdock.fd(org, flow_name, userkey).send_flow_message(message)
    r = r.json()

    # get next message
    result = es_flow_feeder.load_new_messages(
        flow_id, flow_name, index, org, userkey, host, region, service, role)

    assert result == r['id']

def test_load_new_messages_none_exist():
    org = "uhg"
    flow_id = "95f07574-4fc4-4450-a7f0-36d5d96ccc7e"
    flow_name = "cc_bi_unittests"
    userkey = os.environ['flowdock_key']

    # get next message
    result = es_flow_feeder.load_new_messages(
        flow_id, flow_name, index, org, userkey, host, region, service, role)

    assert result == "no new messages"