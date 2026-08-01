from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_projection_expr(cli, ddb_client, tmp_path):
    t = "wf_scanproj_31"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}, "keep": {"S": "1"}, "drop": {"S": "2"}})
    r1 = cli("dynamodb", "scan", "--table-name", t,
             "--projection-expression", "keep")
    assert r1.returncode == 0
    items = json.loads(r1.stdout)["Items"]
    assert "drop" not in items[0]
    assert ddb_client.get_item(TableName=t, Key={"pk": {"S": "a"}})["Item"]["drop"]["S"] == "2"
