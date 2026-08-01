from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_missing_table_before_create(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "get-item", "--table-name", "Wf22Tbl",
                 "--key", '{"pk":{"S":"y"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    result = cli("dynamodb", "create-table", "--table-name", "Wf22Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "Wf22Tbl" in ddb_client.list_tables()["TableNames"]
