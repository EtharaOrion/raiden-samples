from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_recreate_table_inuse(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf7Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "Wf7Tbl" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "create-table", "--table-name", "Wf7Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode != 0
    assert "ResourceInUseException" in result.stderr
