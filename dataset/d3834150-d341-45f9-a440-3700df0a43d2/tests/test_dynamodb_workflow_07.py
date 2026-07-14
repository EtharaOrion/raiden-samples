from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deletetable_then_listtables(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="TblToDelete1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert "TblToDelete1" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "delete-table", "--table-name", "TblToDelete1")
    assert result.returncode == 0
    assert "TblToDelete1" not in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
