from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_table_listing(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf7Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert "Wf7Tbl" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", "Wf7Tbl")
    assert result.returncode == 0
    assert "Wf7Tbl" not in ddb_client.list_tables()["TableNames"]
