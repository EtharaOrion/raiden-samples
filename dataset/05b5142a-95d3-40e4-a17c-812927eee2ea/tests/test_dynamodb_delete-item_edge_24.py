from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_conditional_missing_key_fails(cli, ddb_client):
    table = "GuardedDeleteTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    # Seed a different item so the table is non-empty but the target key is absent.
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "exists"}, "data": {"S": "keepme"}},
    )

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table,
        "--key", '{"id":{"S":"never-existed"}}',
        "--condition-expression", "attribute_exists(id)",
    )

    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    # State unchanged: the target key still absent, the seeded item still present.
    missing = ddb_client.get_item(
        TableName=table, Key={"id": {"S": "never-existed"}}
    )
    assert missing.get("Item") is None

    kept = ddb_client.get_item(
        TableName=table, Key={"id": {"S": "exists"}}
    )
    assert kept.get("Item") is not None
    assert kept["Item"]["data"]["S"] == "keepme"