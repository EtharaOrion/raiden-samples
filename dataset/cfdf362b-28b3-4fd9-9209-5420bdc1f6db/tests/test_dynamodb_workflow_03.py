from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deletetable_removes_from_list(cli, ddb_client, tmp_path):
    ddb_client.create_table(TableName="WfTblDel1",
                            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
                            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
                            BillingMode="PAY_PER_REQUEST")
    assert "WfTblDel1" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", "WfTblDel1")
    assert result.returncode == 0
    assert "WfTblDel1" not in ddb_client.list_tables()["TableNames"]
