from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_idempotent_on_missing_key(cli, ddb_client):
    table = "IdempDelTable"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    # Seed an unrelated item to ensure the table has content that must remain untouched.
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "existing"}, "val": {"N": "1"}},
    )

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table,
        "--key", '{"id":{"S":"never-existed"}}',
    )
    assert result.returncode == 0

    # The missing key delete is idempotent: no such item exists afterward.
    missing = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "never-existed"}},
    )
    assert missing.get("Item") is None

    # The unrelated existing item must still be present.
    still = ddb_client.get_item(
        TableName=table,
        Key={"id": {"S": "existing"}},
    )
    assert still.get("Item") is not None
    assert still["Item"]["val"]["N"] == "1"