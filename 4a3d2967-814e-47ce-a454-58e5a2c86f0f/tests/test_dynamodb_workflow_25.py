from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_filter_no_match(cli, ddb_client, tmp_path):
    t = "wf_filternomatch_26"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}, "n": {"N": "5"}})
    r1 = cli("dynamodb", "scan", "--table-name", t,
             "--filter-expression", "n = :v",
             "--expression-attribute-values", '{":v":{"N":"99"}}')
    assert r1.returncode == 0
    assert json.loads(r1.stdout).get("Items", []) == []
    r2 = cli("dynamodb", "scan", "--table-name", t)
    assert r2.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r2.stdout)["Items"]} == {"a"}
