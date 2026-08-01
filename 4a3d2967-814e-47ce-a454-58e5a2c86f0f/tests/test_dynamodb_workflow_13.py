from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_then_query_after_more_items(cli, ddb_client, tmp_path):
    t = "wf_addmore_14"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}})
    r1 = cli("dynamodb", "scan", "--table-name", t)
    assert r1.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r1.stdout)["Items"]} == {"a"}
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "b"}})
    r2 = cli("dynamodb", "scan", "--table-name", t)
    assert r2.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r2.stdout)["Items"]} == {"a", "b"}
