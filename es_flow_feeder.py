import boto3 as boto3
import flowdock
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import os

# Primary application module
# This module that will feed an es cluster with flowdock messages
# Assumes es index exists and fixed
# Input of a flow channel
# Look up last msesage in es for that flow
# Get next message in the flow:
#   If the same end as last message in es report successful no new message
#   If newer message returned add message 
#   in lambda handler invoke lambda again to repeat 


def aws_auth_role(region, service, role=None):
    # generate AWS auth object
    # address complexity of assume role or current creds have permission

    # This function uses existing aws credentials,
    # assumes a desired role if not None, and returns an aws auth version4 signature

    if role is not None:
        # Use existing credentials to create an sts token
        # needed to authorize against assume operation
        sts_client = boto3.client('sts')

        # assume the target role in an aws account
        assumed_role_object = sts_client.assume_role(
            RoleArn=role,
            RoleSessionName="AssumeRoleSession1"
        )

        # populate the assumde role's temporary credentials
        credentials = assumed_role_object['Credentials']

        # Generate the auth v4 signature so it can be returned
        auth = AWS4Auth(
            credentials['AccessKeyId'],
            credentials['SecretAccessKey'],
            region,
            service,
            session_token=credentials['SessionToken']
            )

        return auth

    else:
        # Get current session
        session = boto3.Session()

        # Load and freeze session credentials
        credentials = session.get_credentials()
        credentials = credentials.get_frozen_credentials()

        # Generate the auth v4 signature so it can be returned
        auth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            region,
            service,
            )

        return auth


def get_es_message_id(flow_id, index, es):
    # Create request body for es to look up largest id
    # in this use case es max size will always exceed number of results
    # eliminating the need to page through results in es

    body = {
       "from": 0,
       "size": 0,
       "query": {
           "match": {
               "flow": flow_id
                }
            },
       "aggregations": {
            "id": {
                "max": {
                    "field": "id"
                    }
                }
            },
        }

    # envoke es
    try:
        result = es.search(index=index, body=body)

        return result

    except:
        print("error in es")
        return None


def get_next_message_id(flow_id, index, es):
    # Convert flow into request body for es search
    # Returns next message_id

    # envoke es get max id function
    try:
        res = get_es_message_id(flow_id, index, es)

    except:
        print("flowdock_run_failures")
        return None

    # parse results to get id
    # if there are no results the id is zero
    if res['hits']['total']['value'] == 0:
        message_id = 0

    # else if there are results set id to es result
    else:
        message_id = int(res['aggregations']['id']['value'])

    return message_id


def enrich_message(messages, flow_name):
    # add, remove, or change any data as needed

    # pull first record and define it as the message
    message = messages[0]
    message["flow_name"] = flow_name

    # drop the undesired key value pairs for easier parsing
    try:
        del message["thread"]
    except KeyError:
        print("Key 'thread' not found")

    try:
        del message["emojiReactions"]
    except KeyError:
        print("Key 'emojiReactions' not found")

    try:
        del message["tags"]
    except KeyError:
        print("Key 'tags' not found")

    try:
        del message["attachments"]
    except KeyError:
        print("Key 'attachments' not found")

    # some flow messages have non-string content that complicates keyword uses
    # this content can be recreated from other parameters and is set to null
    if type(message["content"]) != str:
        message["content"] = None

    return message


def load_new_messages(
        flow_id,
        flow_name,
        index,
        org,
        userkey,
        host,
        region,
        service,
        role):

    # Primary function that is called by the lambda handler
    
    # innitialize es
    es = Elasticsearch(
        hosts=host,
        http_auth=aws_auth_role(region, service, role),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
        )
    print("es loaded host:"+host+" Index:"+index)
    
    # Look up last message in elastic search
    message_id = get_next_message_id(flow_id, index, es)
    print("es message look up result message_id:"+str(message_id))

    # Look up next message in flowdock
    fd = flowdock.fd(org, flow_name, userkey)
    messages = fd.get_flow_message(message_id)
    print("flowdock next message result length:"+str(len(messages)))

    # For flowdock result with a message add to es
    if len(messages) > 0:

        # Do Enrich/transform
        message = enrich_message(messages, flow_name)

        # Load into Elasticsearch
        result = es.index(index=index, body=message)
        print("es message put body['id']:"+str(message['id']))
        print("es message put result:"+result['result'])
        print(message)
        return message['id']

    # result when no new message returned
    else:
        print('no messages returned from flowdock')
        return "no new messages"


if __name__ == "__main__":
    # AWS Role that can be assumed to access elastic search
    role = None # redacted containers aws account number and role arn

    # For example, my-test-domain.us-east-1.es.amazonaws.com
    host = None # redacted dev aws elasticsearch cluster
    
    # Primary debugging test channel in flowdock
    # flow_id = "4f26ad39-195e-4cd9-a75c-7077692f4b2c"
    # flow_name = "cc_flowdocktesting"

    # Internal team channel with largest amounts of data for extensive debugging
    # flow_id = "682ed953-6c38-4269-aa89-3e943fe0727a"
    # flow_name = "cc-leads"

    # Channel dedicated to testing
    flow_id = "95f07574-4fc4-4450-a7f0-36d5d96ccc7e"
    flow_name = "cc_bi_unittests"

    region = 'us-east-1'  # e.g. us-west-1
    service = 'es'
    index = 'test5'
    org = "uhg"
    userkey = os.environ['flowdock_key']

    # Execute the primary function

    load_new_messages(
        flow_id,
        flow_name,
        index,
        org,
        userkey,
        host,
        region,
        service,
        role
        )
