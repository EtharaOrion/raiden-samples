from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_get_item_missing_key_returns_no_item(cli, ddb_client):
    table = "GetItemMissingTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    # Seed an unrelated item so the table is non-empty.
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "exists"}, "n": {"N": "1"}},
    )

    result = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", '{"id":{"S":"does-not-exist"}}',
    )
    assert result.returncode == 0

    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    assert "Item" not in payload or not payload.get("Item")

    # Independent verification: the key was never written.
    resp = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "does-not-exist"}},
    )
    assert resp.get("Item") is None

    # Sanity: the existing item is still retrievable.
    resp2 = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "exists"}},
    )
    assert resp2.get("Item") is not None