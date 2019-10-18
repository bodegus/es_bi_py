import requests as requests
import os

# Module for flowdock handling
# A class that aggregates flowdock curl commands/logic


class fd:
    # set up a flowdock class that will make flowdock calls
    # define core urls at init to curl later
    # define a function to get flow messages
    # define a function to get users

    def __init__(self, org, flow, userkey):
        # define url used by the remaining functions
        # https:// + apikey + ":dummy@api.flowdock.com/flows/" + org + flow

        # set a common root of the string used in subsequent definitions
        url = "https://" + userkey + ":dummy@api.flowdock.com/flows/"

        # set the url that will be used for org level calls
        self.org_url = url + org + "/"

        # set the url that will be used for flow level calls
        self.flow_url = url + org + "/" + flow + "/"

    def get_flow_message(self, message_id=0):
        # Set the url that will be used to make the request

        # Set the static elements of the url
        url = self.flow_url + "messages?limit=1&sort=asc&since_id="

        # Add last message id to url
        url = url + str(message_id)

        # Make the curl request to flowdock for messages
        r = requests.get(url)

        # return the request result
        return r.json()

    def get_flow_messages(self, message_id=0, limit=100):
        # Set the url that will be used to make the request

        # Set limit var type to str so it can be added to url
        limit = str(limit)

        # Set the static elements of the url
        url = self.flow_url + "messages?limit="+limit+"&sort=asc&since_id="

        # Add last message id to url
        url = url + str(message_id)

        # Make the curl request to flowdock for messages
        r = requests.get(url)

        # return the request result
        return r.json()

    def send_flow_message(self, message):
        # Post a message to flowdown

        # set post url
        posturl = self.flow_url + "messages"

        # Build message body
        body = {
            "event": "message",
            "content": message,
            }

        r = requests.post(url=posturl, data=body)

        print(r)

        return r

    def get_user_email(self, user_id):
        # Look up a user in the flowdock org

        # Set the static elements of the url

        # Add user id to url

        # Make the curl request to flowdock for messages

        # Extract the email field as a single string
        email = None

        # Return Result
        return email


if __name__ == "__main__":
    # Load Variables for debugging
    org = "uhg"
    flow = "pe-iac-aws"
    userkey = os.environ['flowdock_key']

    # Generate Class
    fd = fd(org, flow, userkey)

    # Call method for Flow messages and printoutputs
    data = fd.get_flow_message(0)

    print(data)
    print(len(data[0]))
    print(data[0])

    data = fd.get_flow_messages(0, 10)
    print(type(data))
    print(len(data[0]))
    print(data[0])
