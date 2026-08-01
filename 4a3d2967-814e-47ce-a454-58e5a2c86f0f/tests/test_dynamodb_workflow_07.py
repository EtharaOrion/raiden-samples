from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_then_query_number_pk(cli, ddb_client, tmp_path):
    t = "wf_numpk_8"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "N"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"id": {"N": "10"}})
    ddb_client.put_item(TableName=t, Item={"id": {"N": "20"}})
    r1 = cli("dynamodb", "scan", "--table-name", t)
    assert r1.returncode == 0
    assert {i["id"]["N"] for i in json.loads(r1.stdout)["Items"]} == {"10", "20"}
    r2 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "id = :v",
             "--expression-attribute-values", '{":v":{"N":"10"}}')
    assert r2.returncode == 0
    assert {i["id"]["N"] for i in json.loads(r2.stdout)["Items"]} == {"10"}
