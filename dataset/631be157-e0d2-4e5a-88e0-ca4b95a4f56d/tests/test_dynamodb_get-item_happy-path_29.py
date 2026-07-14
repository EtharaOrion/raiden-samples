from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_get_item_returns_stored_item(cli, ddb_client):
    ddb_client.create_table(
        TableName="GetTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName="GetTbl",
        Item={"pk": {"S": "abc"}, "n": {"N": "42"}, "status": {"S": "active"}},
    )

    result = cli(
        "dynamodb", "get-item",
        "--table-name", "GetTbl",
        "--key", '{"pk":{"S":"abc"}}',
    )
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    item = payload["Item"]
    assert item["pk"]["S"] == "abc"
    assert item["n"]["N"] == "42"
    assert item["status"]["S"] == "active"

    resp = ddb_client.get_item(TableName="GetTbl", Key={"pk": {"S": "abc"}})
    stored = resp.get("Item")
    assert stored is not None
    assert stored["n"]["N"] == "42"
    assert stored["status"]["S"] == "active"