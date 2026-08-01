from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_missing_key_attr_validation(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf55Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf55Tbl",
                 "--item", '{"notpk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
