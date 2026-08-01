from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_missing_key_in_defs_no_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf49",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    assert "Wf49" not in ddb_client.list_tables()["TableNames"]
