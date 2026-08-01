from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_then_query_verify_get(cli, ddb_client, tmp_path):
    t = "wf_verifyget_28"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}, "v": {"S": "hello"}})
    r1 = cli("dynamodb", "scan", "--table-name", t)
    assert r1.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r1.stdout)["Items"]} == {"a"}
    r2 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"a"}}')
    assert r2.returncode == 0
    assert json.loads(r2.stdout)["Items"][0]["v"]["S"] == "hello"
    assert ddb_client.get_item(TableName=t, Key={"pk": {"S": "a"}})["Item"]["v"]["S"] == "hello"
