from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_get_item_missing_key_returns_no_item(cli, ddb_client):
    table = "GetMissTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "present"}, "val": {"N": "1"}},
    )

    result = cli(
        "dynamodb",
        "get-item",
        "--table-name",
        table,
        "--key",
        '{"id":{"S":"does-not-exist"}}',
    )
    assert result.returncode == 0

    if result.stdout.strip():
        payload = json.loads(result.stdout)
        assert "Item" not in payload or not payload.get("Item")

    resp = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "does-not-exist"}},
    )
    assert resp.get("Item") is None

    present = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "present"}},
    )
    assert present.get("Item") is not None
    assert present["Item"]["val"]["N"] == "1"