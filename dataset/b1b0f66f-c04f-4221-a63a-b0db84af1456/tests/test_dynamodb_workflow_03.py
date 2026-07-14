from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_table_then_list_tables(cli, ddb_client):
    ddb_client.create_table(
        TableName="WFDropTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert "WFDropTbl" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", "WFDropTbl")
    assert result.returncode == 0
    assert "WFDropTbl" not in ddb_client.list_tables()["TableNames"]
