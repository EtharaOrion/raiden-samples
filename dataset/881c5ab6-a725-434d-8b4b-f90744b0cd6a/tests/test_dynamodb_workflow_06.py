from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_missing_table_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblG",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    assert "WfTblG" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", "WfTblG_missing")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "WfTblG" in ddb_client.list_tables()["TableNames"]
