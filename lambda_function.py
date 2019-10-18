import os
import es_flow_feeder as es_flow_feeder
import boto3
import json

def lambda_handler(event, context):
    # AWS Role that can be assumed to access elastic search
    role = event['role']

    # For example, my-test-domain.us-east-1.es.amazonaws.com
    host = event['host']
    flow_id = event['flow_id']
    flow_name = event['flow_name']
    region = event['region']
    service = event['service']
    index = event['index']
    org = event['org']
    userkey = os.environ['flowdock_key']


    # re-envoke variables
    client2 = boto3.client('lambda')


    # Innitialize the ES object I am going to use
    result = es_flow_feeder.load_new_messages(flow_id, flow_name, index, org, userkey, host, region, service, role)

    if type(result) == int:
        # envoke the lambda again
        print("envoking lambda again function_name:", context.function_name)
        print(context.function_name)
        response = client2.invoke(
            FunctionName=context.function_name,
            InvocationType='Event',
            LogType='Tail',
            Payload=json.dumps(event).encode('utf-8'),
            )
        print("Invoking Lambda", response)
        return "envoked lambda again"
        
    else:
        return result


if __name__ == "__main__":
    event = {
        "role": "placeholder value",
        "host": "placeholder value",
        "flow_id": "682ed953-6c38-4269-aa89-3e943fe0727a",
        "flow_name": "cc-leads",
        "region": 'us-east-1',
        "service": 'es',
        "index": 'test5',
        "org": "uhg"
        }
    context = type('Lambda context', (object,), {})()
    context.function_name = "testeslambda"
    lambda_handler(event, context)
