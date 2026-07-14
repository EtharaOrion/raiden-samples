from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_get_item_missing_key_returns_no_item(cli, ddb_client):
    table = "GetItemMissing"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    # Seed a different item so the table is non-empty but the queried key is absent.
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
    assert payload.get("Item") is None

    # Independent verification: the key truly does not exist in the table.
    resp = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "does-not-exist"}},
    )
    assert resp.get("Item") is None

    # And the seeded item is still present, confirming the table is intact.
    present = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "exists"}},
    )
    assert present.get("Item") is not None