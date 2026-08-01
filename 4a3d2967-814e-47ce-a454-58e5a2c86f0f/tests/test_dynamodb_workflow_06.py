from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_count_matches_scan(cli, ddb_client, tmp_path):
    t = "wf_count_7"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    for k in ["a", "b", "c"]:
        ddb_client.put_item(TableName=t, Item={"pk": {"S": k}})
    r1 = cli("dynamodb", "scan", "--table-name", t)
    assert r1.returncode == 0
    scan_pks = {i["pk"]["S"] for i in json.loads(r1.stdout)["Items"]}
    assert scan_pks == {"a", "b", "c"}
    r2 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"b"}}')
    assert r2.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r2.stdout)["Items"]} == {"b"}
