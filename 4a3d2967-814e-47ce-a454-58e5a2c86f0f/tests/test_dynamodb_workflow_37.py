from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_then_scan_large(cli, ddb_client, tmp_path):
    t = "wf_large_38"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "N"},
        ],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    for i in range(10):
        ddb_client.put_item(TableName=t, Item={"pk": {"S": "p"}, "sk": {"N": str(i)}})
    r1 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"p"}}')
    assert r1.returncode == 0
    assert {i["sk"]["N"] for i in json.loads(r1.stdout)["Items"]} == {str(x) for x in range(10)}
    r2 = cli("dynamodb", "scan", "--table-name", t)
    assert r2.returncode == 0
    assert {i["sk"]["N"] for i in json.loads(r2.stdout)["Items"]} == {str(x) for x in range(10)}
