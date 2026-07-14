from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_conditional_missing_key_fails(cli, ddb_client):
    table_name = "GuardedDeleteTbl"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    # Seed an unrelated item to make sure state is observable and untouched.
    ddb_client.put_item(
        TableName=table_name,
        Item={"id": {"S": "existing"}, "v": {"N": "1"}},
    )

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table_name,
        "--key", '{"id":{"S":"never-existed"}}',
        "--condition-expression", "attribute_exists(id)",
    )

    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    # State unchanged: the missing key is still absent, the seed still present.
    missing = ddb_client.get_item(
        TableName=table_name,
        Key={"id": {"S": "never-existed"}},
    )
    assert missing.get("Item") is None

    present = ddb_client.get_item(
        TableName=table_name,
        Key={"id": {"S": "existing"}},
    )
    assert present.get("Item") is not None
    assert present["Item"]["v"]["N"] == "1"