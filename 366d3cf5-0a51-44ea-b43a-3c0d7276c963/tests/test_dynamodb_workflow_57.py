from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_missing_then_valid(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "delete-table", "--table-name", "Wf58Ghost")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    result = cli("dynamodb", "create-table", "--table-name", "Wf58",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "delete-table", "--table-name", "Wf58")
    assert result.returncode == 0
    assert "Wf58" not in ddb_client.list_tables()["TableNames"]
