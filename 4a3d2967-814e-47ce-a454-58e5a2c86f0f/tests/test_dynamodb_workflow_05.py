from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_empty_then_seed_query(cli, ddb_client, tmp_path):
    t = "wf_scan_empty_6"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "scan", "--table-name", t)
    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert out.get("Items", []) == []
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "z"}})
    r2 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"z"}}')
    assert r2.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r2.stdout)["Items"]} == {"z"}
