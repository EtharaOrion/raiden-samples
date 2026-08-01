from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_missing_then_created(cli, ddb_client, tmp_path):
    t = "wf_misscreate_39"
    r0 = cli("dynamodb", "scan", "--table-name", t)
    assert r0.returncode != 0
    assert "ResourceNotFoundException" in r0.stderr
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "now"}})
    r1 = cli("dynamodb", "scan", "--table-name", t)
    assert r1.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r1.stdout)["Items"]} == {"now"}
