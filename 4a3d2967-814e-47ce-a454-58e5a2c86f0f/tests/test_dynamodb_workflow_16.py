from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_begins_with_sort(cli, ddb_client, tmp_path):
    t = "wf_begins_17"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "p"}, "sk": {"S": "user#1"}})
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "p"}, "sk": {"S": "user#2"}})
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "p"}, "sk": {"S": "order#9"}})
    r1 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :p AND begins_with(sk, :s)",
             "--expression-attribute-values", '{":p":{"S":"p"},":s":{"S":"user#"}}')
    assert r1.returncode == 0
    assert {i["sk"]["S"] for i in json.loads(r1.stdout)["Items"]} == {"user#1", "user#2"}
    r2 = cli("dynamodb", "scan", "--table-name", t)
    assert r2.returncode == 0
    assert {i["sk"]["S"] for i in json.loads(r2.stdout)["Items"]} == {"user#1", "user#2", "order#9"}
