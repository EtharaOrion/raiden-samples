from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_conditional_missing_key_fails(cli, ddb_client):
    table = "GuardedDelete"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    # Seed an unrelated item so we can verify the table is otherwise intact.
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "exists"}, "v": {"N": "1"}},
    )

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table,
        "--key", '{"id":{"S":"never-existed"}}',
        "--condition-expression", "attribute_exists(id)",
    )

    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    # The missing key remains absent (no phantom write/delete).
    resp_missing = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "never-existed"}},
    )
    assert resp_missing.get("Item") is None

    # The pre-existing item is untouched.
    resp_exists = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "exists"}},
    )
    assert resp_exists.get("Item") is not None
    assert resp_exists["Item"]["v"]["N"] == "1"