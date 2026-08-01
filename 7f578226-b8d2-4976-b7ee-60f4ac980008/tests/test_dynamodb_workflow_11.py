from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_composite_missing_rangekey_def_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl9",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    assert "WfTbl9" not in ddb_client.list_tables()["TableNames"]
