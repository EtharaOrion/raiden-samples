from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_scan_consistency(cli, ddb_client, tmp_path):
    t = "wf_consist_40"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}})
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "b"}})
    r1 = cli("dynamodb", "scan", "--table-name", t)
    assert r1.returncode == 0
    scan_set = {i["pk"]["S"] for i in json.loads(r1.stdout)["Items"]}
    assert scan_set == {"a", "b"}
    query_union = set()
    for k in scan_set:
        r2 = cli("dynamodb", "query", "--table-name", t,
                 "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"' + k + '"}}')
        assert r2.returncode == 0
        query_union |= {i["pk"]["S"] for i in json.loads(r2.stdout)["Items"]}
    assert query_union == scan_set
