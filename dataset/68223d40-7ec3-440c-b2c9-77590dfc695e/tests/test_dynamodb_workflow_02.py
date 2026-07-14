from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_bad_keyschema_validation(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfBadKey1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"missing","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    assert "WfBadKey1" not in ddb_client.list_tables()["TableNames"]
