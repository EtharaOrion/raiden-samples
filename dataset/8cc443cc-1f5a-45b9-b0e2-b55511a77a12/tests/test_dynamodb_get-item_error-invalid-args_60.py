from _ddb_http import to_item, from_item, to_av, from_av


def test_get_item_nonexistent_table_returns_resource_not_found(cli, ddb_client):
    table_name = "PresentTable"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert table_name in ddb_client.list_tables()["TableNames"]

    missing_table = "AbsentTable123"
    assert missing_table not in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "get-item",
        "--table-name", missing_table,
        "--key", '{"pk":{"S":"abc"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr