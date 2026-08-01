from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_then_query(cli, ddb_client, tmp_path):
    t = "wf_scan_query_1"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}, "n": {"N": "1"}})
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "b"}, "n": {"N": "2"}})
    result = cli("dynamodb", "scan", "--table-name", t)
    assert result.returncode == 0
    out = json.loads(result.stdout)
    pks = {i["pk"]["S"] for i in out["Items"]}
    assert pks == {"a", "b"}
    result2 = cli("dynamodb", "query", "--table-name", t,
                  "--key-condition-expression", "pk = :v",
                  "--expression-attribute-values", '{":v":{"S":"a"}}')
    assert result2.returncode == 0
    out2 = json.loads(result2.stdout)
    qpks = {i["pk"]["S"] for i in out2["Items"]}
    assert qpks == {"a"}
    assert ddb_client.get_item(TableName=t, Key={"pk": {"S": "a"}})["Item"]["n"]["N"] == "1"
