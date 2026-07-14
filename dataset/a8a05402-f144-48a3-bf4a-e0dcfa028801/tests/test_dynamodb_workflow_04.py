from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_table_then_list(cli, ddb_client, tmp_path):
    table = "WfDelTable"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert table in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", table)
    assert result.returncode == 0
    assert table not in ddb_client.list_tables()["TableNames"]
