from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_conditional_missing_key_fails(cli, ddb_client):
    table = "GuardedDelete"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    # Seed an unrelated item to confirm state is unchanged afterwards.
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "existing"}, "v": {"N": "1"}},
    )

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table,
        "--key", '{"id":{"S":"never-existed"}}',
        "--condition-expression", "attribute_exists(id)",
    )

    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    # The missing key was never created; the guarded delete must not create it.
    resp = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "never-existed"}},
    )
    assert resp.get("Item") is None

    # The unrelated item is untouched.
    existing = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "existing"}},
    )
    assert existing.get("Item") is not None
    assert existing["Item"]["v"]["N"] == "1"