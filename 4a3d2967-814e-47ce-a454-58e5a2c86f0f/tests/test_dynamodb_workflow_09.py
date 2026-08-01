from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_filter_verify_state(cli, ddb_client, tmp_path):
    t = "wf_scanfilter_10"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}, "st": {"S": "on"}})
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "b"}, "st": {"S": "off"}})
    r1 = cli("dynamodb", "scan", "--table-name", t,
             "--filter-expression", "st = :v",
             "--expression-attribute-values", '{":v":{"S":"on"}}')
    assert r1.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r1.stdout)["Items"]} == {"a"}
    r2 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"b"}}')
    assert r2.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r2.stdout)["Items"]} == {"b"}
