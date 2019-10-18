# es_bi_py

elasticsearch business intelligence python app

## Objectives

My product team runs an enterprise central logging platform and I want to centralize all of our cloud adoption business intelligence in elasticsearch as PoC so I can more intelligently speak on the topic to our engineering partners as well as be an primary user of our tech stack (I am a firm believer in the product manager using his own product daily)

I am experimenting with lambda and es and would appreciate engineering feedback on how I am building out my python code.  

elasticsearch is not the best database tool but I wanted to develop experience with it for this project

Some follow up features include running all messages through aws comprehend, adding another index with user meta data from LDAP.  I would like to use this as a pattern for a seperate python lambda that would parse/load LDAP data

All of the infrastructure is deployed with terraform.

## TODO

I need to add logging and determine a better way to handle configurations

There are better ways to feed es (such as kinesis firehose) but the record volumes are very low and this seems to reduce complexity

I need to incorporate logging (I am looking basic python logging and aws x-ray)

## Gaps/areas of focus

What would I need to do to make this a project you would be willing to work on?

I would like to have continous integration testing but am struggling with how to seperate out integration tests from unit tests - give the abstraction of the functions I am not sure how to proceed.

I don't know how to properly use decorators - I am curious if they are a little less valuable in this example