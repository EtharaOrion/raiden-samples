from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_idempotent_on_absent_key(cli, ddb_client):
    table_name = "IdempotentDeleteTbl"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    result = cli(
        "dynamodb",
        "delete-item",
        "--table-name",
        table_name,
        "--key",
        '{"id":{"S":"never-existed"}}',
    )
    assert result.returncode == 0

    resp = ddb_client.get_item(
        TableName=table_name,
        Key={"id": {"S": "never-existed"}},
    )
    assert resp.get("Item") is None