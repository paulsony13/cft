import boto3
import json
from tabulate import tabulate
import sys
import botocore
import time
import os




REGION = os.environ['REGION']
CHANGE_SET_NAME = 'deploy-commit-'
STACK_NAME = os.environ['STACK_NAME']
SNS_TOPIC = 'arn:aws:sns:us-east-1:631145538984:SendCINotification'
PARAMS_FILE = os.environ['PARAMS_FILE']
TEMPLATE_BODY_FILE = os.environ['TEMPLATE_FILE']
COMMIT =  os.environ['CODEBUILD_RESOLVED_SOURCE_VERSION']
COMMIT_ID = COMMIT[:5]




client = boto3.client('cloudformation', region_name=REGION)

def get_change_set():

    time.sleep(10)

    response = client.describe_change_set(
        ChangeSetName=CHANGE_SET_NAME+COMMIT_ID,
        StackName=STACK_NAME
    )

    changes_list = response['Changes']
    if not changes_list:
        print("No Changes found in Template/Parameter, Stack is Up-to-Date")
        return None, None, None, None, None
    else:
        action = []
        ResourceId = []
        replacement = []
        logicid = []
        sl = []
        for i in range(0, len(changes_list)):
            sl.append(int(i) + 1)
            action.append(changes_list[i]['ResourceChange']['Action'])
            ResourceId.append(changes_list[i]['ResourceChange']['PhysicalResourceId'])
            replacement.append(changes_list[i]['ResourceChange']['Replacement'])
            logicid.append(changes_list[i]['ResourceChange']['LogicalResourceId'])

        return sl, action, ResourceId, replacement, logicid


def genetate_table_format(index, sl, action, ResourceId , logicid, replacement):
    n = []
    n.append(sl[index])
    n.append(action[index])
    n.append(ResourceId[index])
    n.append(logicid[index])
    n.append(replacement[index])

    return n


def send_sns(msg):
    client = boto3.client('sns', region_name=REGION)
    response = client.publish(
        TargetArn=SNS_TOPIC,
        Message=msg,
    )

    print(response)


def read_parameters_json(PARAMS_FILE):
    file = open(PARAMS_FILE)
    parameter = json.load(file)

    parameter = parameter['Parameters']
    params_list = []
    param = {}

    for key, value in parameter.items():
        param['ParameterKey'] = key
        param['ParameterValue'] = value

        params_list.append(param.copy())

    return params_list


def create_stack(params):
    cf_template = open(TEMPLATE_BODY_FILE).read()
    try:
        response = client.create_stack(
            StackName=STACK_NAME,
            TemplateBody=cf_template,
            Parameters=params,
            Capabilities=['CAPABILITY_IAM','CAPABILITY_NAMED_IAM','CAPABILITY_AUTO_EXPAND']
        )
        print("Provisioning new Stack.....")

        return response
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']

        stack_exists = "Stack ["+STACK_NAME+"] already exists"
        if error_message == stack_exists:
            return 'stack-exists'


def validate_change_set():
    sl, action, ResourceId, replacement, logicid = get_change_set()
    data = []
    if not sl:
        return "no-changes"
    else:
        for i in range(0, len(sl)):
            data.append(genetate_table_format(i, sl, action, ResourceId, replacement, logicid))
        d = tabulate(data, headers=["SL", "ACTION", "RID", "LogicID", "Replacement"])
        #send_sns(d)
        print(d)


def create_change_set(params):
    cf_template = open(TEMPLATE_BODY_FILE).read()
    try:
        response = client.create_change_set(
            StackName=STACK_NAME,
            ChangeSetName=CHANGE_SET_NAME+COMMIT_ID,
            IncludeNestedStacks=True,
            TemplateBody=cf_template,
            Parameters=params,
            Capabilities=['CAPABILITY_IAM','CAPABILITY_NAMED_IAM','CAPABILITY_AUTO_EXPAND']
        )

        return "change-set-created"
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        return error_message

if sys.argv[1] == "update":
    parameters = read_parameters_json(PARAMS_FILE)
    response = create_stack(parameters)
    if response == "stack-exists":
        print("Stack ["+STACK_NAME+"] already exists")
        print("Discovering new Changes")
        change_set_response = create_change_set(parameters)
        if change_set_response == "change-set-created":
            validate_change_set_response =  validate_change_set()
            if validate_change_set_response == "no-changes":
                exit(0)


elif sys.argv[1] == "execute":
    print("Executing Change Set")
    response = client.execute_change_set(
        ChangeSetName=CHANGE_SET_NAME+COMMIT_ID,
        StackName=STACK_NAME
    )

    print(response)





















