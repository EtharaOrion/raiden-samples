from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_idempotent_on_missing_key(cli, ddb_client):
    table = "IdempotentDeleteTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    # Seed an unrelated item to ensure the table is non-empty.
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "exists"}, "n": {"N": "1"}},
    )

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table,
        "--key", '{"id":{"S":"never-existed"}}',
    )
    assert result.returncode == 0

    # The never-existent key remains absent (idempotent delete, no error).
    resp = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "never-existed"}},
    )
    assert resp.get("Item") is None

    # The unrelated item is untouched.
    other = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "exists"}},
    )
    assert other.get("Item") is not None
    assert other["Item"]["n"]["N"] == "1"