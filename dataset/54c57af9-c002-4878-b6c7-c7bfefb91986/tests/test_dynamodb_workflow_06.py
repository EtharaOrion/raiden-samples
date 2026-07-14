from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_table_removes(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfDT1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "WfDT1" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "delete-table", "--table-name", "WfDT1")
    assert result.returncode == 0
    assert "WfDT1" not in ddb_client.list_tables()["TableNames"]
