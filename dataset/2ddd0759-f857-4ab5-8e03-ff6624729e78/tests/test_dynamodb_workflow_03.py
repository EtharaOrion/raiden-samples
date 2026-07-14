from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_table_gone_from_list(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfDelTbl1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert "WfDelTbl1" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", "WfDelTbl1")
    assert result.returncode == 0
    assert "WfDelTbl1" not in ddb_client.list_tables()["TableNames"]
