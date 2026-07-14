from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_keyschema_mismatch(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "BadKeyTbl",
                 "--attribute-definitions", '[{"AttributeName":"other","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    assert "BadKeyTbl" not in ddb_client.list_tables()["TableNames"]
