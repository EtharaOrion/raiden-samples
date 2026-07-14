from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deletetable_then_listtables(ddb_client, cli, tmp_path):
    ddb_client.create_table(
        TableName="WfDropTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert "WfDropTbl" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", "WfDropTbl")
    assert result.returncode == 0
    assert "WfDropTbl" not in ddb_client.list_tables()["TableNames"]
