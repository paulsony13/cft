import boto3
import json
from tabulate import tabulate

REGION = 'us-east-1'
CHANGE_SET_NAME = 'deploy-commit'
STACK_NAME =  'IAM-Stack'

client = boto3.client('cloudformation', region_name=REGION)

response = client.describe_change_set(
    ChangeSetName=CHANGE_SET_NAME,
    StackName=STACK_NAME
)
#print(json.dumps(response['Changes'], indent=4))

changes_list = response['Changes']

#print(len(changes_list))

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

# print(sl)
# print(action)
# print(ResourceId)
# print(replacement)
# print(logicid)



def genetate_table_format(index):
    n = []
    n.append(sl[index])
    n.append(action[index])
    n.append(ResourceId[index])
    n.append(logicid[index])
    n.append(replacement[index])

    return n


data = []
for i in range(0, len(sl)):
    data.append(genetate_table_format(0))



print (tabulate(data, headers=["SL", "ACTION", "RecourseID", "LogicID", "Replacement"]))
