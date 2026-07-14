from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_conditional_missing_key_fails(cli, ddb_client):
    table = "GuardedDeleteTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    # Seed an unrelated item so we can confirm table state is untouched.
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "existing"}, "val": {"S": "keepme"}},
    )

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table,
        "--key", '{"id":{"S":"never-existed"}}',
        "--condition-expression", "attribute_exists(id)",
    )

    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    # State unchanged: the missing key stays missing, the other item survives.
    resp_missing = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "never-existed"}},
    )
    assert resp_missing.get("Item") is None

    resp_existing = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "existing"}},
    )
    assert resp_existing.get("Item") is not None
    assert resp_existing["Item"]["val"]["S"] == "keepme"