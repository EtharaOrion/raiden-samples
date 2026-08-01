from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_count_attr(cli, ddb_client, tmp_path):
    t = "wf_scancount_19"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    for k in ["a", "b", "c", "d"]:
        ddb_client.put_item(TableName=t, Item={"pk": {"S": k}})
    r1 = cli("dynamodb", "scan", "--table-name", t, "--select", "COUNT")
    assert r1.returncode == 0
    out = json.loads(r1.stdout)
    assert out["Count"] == 4
    r2 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"a"}}')
    assert r2.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r2.stdout)["Items"]} == {"a"}
