from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_delete_table_gone(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "GoneTbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "GoneTbl" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "delete-table", "--table-name", "GoneTbl")
    assert result.returncode == 0
    assert "GoneTbl" not in ddb_client.list_tables()["TableNames"]
