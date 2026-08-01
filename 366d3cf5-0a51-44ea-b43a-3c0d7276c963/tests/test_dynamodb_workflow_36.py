from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_missing_table_after_valid(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf37",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "delete-table", "--table-name", "Wf37Ghost")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "Wf37" in ddb_client.list_tables()["TableNames"]
