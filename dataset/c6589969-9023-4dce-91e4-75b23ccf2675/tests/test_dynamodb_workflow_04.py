from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_table_then_list(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfDelTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert "WfDelTbl" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", "WfDelTbl")
    assert result.returncode == 0
    assert "WfDelTbl" not in ddb_client.list_tables()["TableNames"]
