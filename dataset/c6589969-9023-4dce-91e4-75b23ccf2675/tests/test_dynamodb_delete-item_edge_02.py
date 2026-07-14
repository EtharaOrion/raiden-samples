from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_idempotent_on_missing_key(cli, ddb_client):
    table = "IdempotentDeleteTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    # Seed a different item to ensure the table has content but not the target key.
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "existing"}, "v": {"N": "1"}},
    )

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table,
        "--key", '{"id":{"S":"never-existed"}}',
    )
    assert result.returncode == 0

    # The never-existing key is still absent (idempotent delete, no error).
    resp = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "never-existed"}},
    )
    assert resp.get("Item") is None

    # The unrelated seeded item is untouched.
    other = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "existing"}},
    )
    assert other.get("Item") is not None
    assert other["Item"]["v"]["N"] == "1"