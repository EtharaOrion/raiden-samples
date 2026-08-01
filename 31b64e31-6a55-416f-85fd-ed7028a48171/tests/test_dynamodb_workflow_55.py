from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_wrong_type_key_validation(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf56Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf56Tbl",
                 "--item", '{"pk":{"S":"good"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Wf56Tbl",
                 "--key", '{"pk":{"N":"5"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
