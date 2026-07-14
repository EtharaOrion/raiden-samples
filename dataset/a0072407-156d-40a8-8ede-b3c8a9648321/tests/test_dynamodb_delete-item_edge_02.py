from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_idempotent_missing_key(cli, ddb_client):
    ddb_client.create_table(
        TableName="IdempTbl",
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "IdempTbl",
        "--key", '{"id":{"S":"never-existed"}}',
    )
    assert result.returncode == 0

    resp = ddb_client.get_item(
        TableName="IdempTbl",
        Key={"id": {"S": "never-existed"}},
    )
    assert resp.get("Item") is None

    assert "IdempTbl" in ddb_client.list_tables()["TableNames"]