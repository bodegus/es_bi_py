import flowdock
import os
from datetime import datetime


def test_flowdock_init():
    org = "uhg"
    flow = "CC_Flowdocktesting"
    userkey = os.environ['flowdock_key']
    url_buffer = 38
    org_buffer = 1
    flow_buffer = 2

    # Expected Results
    org_len = url_buffer + org_buffer + len(org) + len(userkey)
    flow_len = url_buffer + flow_buffer + len(org) + len(userkey) + len(flow)

    assert len(flowdock.fd(org, flow, userkey).org_url) == org_len
    assert len(flowdock.fd(org, flow, userkey).flow_url) == flow_len


def test_flowdock_get_message():
    org = "uhg"
    flow = "cc_flowdocktesting"
    userkey = os.environ['flowdock_key']
    message_id = 0

    message = flowdock.fd(org, flow, userkey).get_flow_message(message_id)

    assert message[0]['created_at'] is not None
    assert message[0]['flow'] is not None
    assert message[0]['id'] is not None

def test_flowdock_get_messages():
    org = "uhg"
    flow = "cc_flowdocktesting"
    userkey = os.environ['flowdock_key']
    message_id = 0
    length = 10

    message = flowdock.fd(org, flow, userkey).get_flow_messages(message_id, length)

    assert message[0]['created_at'] is not None
    assert message[0]['flow'] is not None
    assert message[0]['id'] is not None
    assert len(message) == length


def test_flowdock_get_message():
    org = "uhg"
    flow = "cc_flowdocktesting"
    userkey = os.environ['flowdock_key']

    message = "hello from pytest at " + str(datetime.now())

    r = flowdock.fd(org, flow, userkey).send_flow_message(message)
    r = r.json()

    assert r['id'] >= 0

