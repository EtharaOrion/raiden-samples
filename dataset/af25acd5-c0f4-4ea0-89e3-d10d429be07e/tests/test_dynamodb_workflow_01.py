from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_recreate_conflict(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "DupTbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "DupTbl" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "create-table", "--table-name", "DupTbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode != 0
    assert "ResourceInUseException" in result.stderr
