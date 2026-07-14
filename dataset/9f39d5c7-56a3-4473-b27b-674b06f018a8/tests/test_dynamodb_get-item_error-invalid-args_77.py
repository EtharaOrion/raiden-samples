from _ddb_http import to_item, from_item, to_av, from_av


def test_get_item_missing_required_key(cli, ddb_client):
    table_name = "TblGetItemErr"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "get-item",
        "--table-name", "NonExistentTableXYZ",
        "--key", '{"pk":{"S":"abc"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr