from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_conditional_missing_key_fails(cli, ddb_client):
    table = "GuardedDelete"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    # Seed an unrelated item to prove state is untouched.
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

    # State unchanged: the seeded item remains, the missing key still absent.
    resp = ddb_client.get_item(TableName=table, Key={"id": {"S": "exists"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["v"]["N"] == "1"

    missing = ddb_client.get_item(TableName=table, Key={"id": {"S": "never-existed"}})
    assert missing.get("Item") is None