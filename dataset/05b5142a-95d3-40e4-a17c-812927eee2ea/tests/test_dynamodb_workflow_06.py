from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_table_removes_from_list(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfDelTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    assert "WfDelTbl" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", "WfDelTbl")
    assert result.returncode == 0
    assert "WfDelTbl" not in ddb_client.list_tables()["TableNames"]
