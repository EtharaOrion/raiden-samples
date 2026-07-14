from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_idempotent_missing_key(cli, ddb_client):
    table = "IdempotentDeleteTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    # Seed an unrelated item so the table is non-empty.
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "exists"}, "v": {"S": "keep"}},
    )

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table,
        "--key", '{"id":{"S":"never-existed"}}',
    )
    assert result.returncode == 0

    # The missing key remains absent (delete on missing key is a no-op).
    resp_missing = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "never-existed"}},
    )
    assert resp_missing.get("Item") is None

    # The unrelated seeded item is untouched.
    resp_existing = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "exists"}},
    )
    assert resp_existing.get("Item") is not None
    assert resp_existing["Item"]["v"]["S"] == "keep"