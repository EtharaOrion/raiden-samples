from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_table_removes_table(cli, ddb_client):
    ddb_client.create_table(
        TableName="ToDelete",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert "ToDelete" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "delete-table", "--table-name", "ToDelete")
    assert result.returncode == 0

    assert "ToDelete" not in ddb_client.list_tables()["TableNames"]