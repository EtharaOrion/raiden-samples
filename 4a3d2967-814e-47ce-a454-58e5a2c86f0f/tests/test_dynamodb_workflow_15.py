from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_binary_number_set(cli, ddb_client, tmp_path):
    t = "wf_numset_16"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={"pk": {"S": "a"}, "ns": {"NS": ["1", "2", "3"]}})
    r1 = cli("dynamodb", "query", "--table-name", t,
             "--key-condition-expression", "pk = :v",
             "--expression-attribute-values", '{":v":{"S":"a"}}')
    assert r1.returncode == 0
    items = json.loads(r1.stdout)["Items"]
    assert set(items[0]["ns"]["NS"]) == {"1", "2", "3"}
    stored = ddb_client.get_item(TableName=t, Key={"pk": {"S": "a"}})["Item"]
    assert set(stored["ns"]["NS"]) == {"1", "2", "3"}
