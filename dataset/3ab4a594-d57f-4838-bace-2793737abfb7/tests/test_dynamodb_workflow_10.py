from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_nonkey_validation(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf11Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "Wf11Tbl",
                 "--item", '{"pk":{"S":"p1"},"other":{"S":"z"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "query", "--table-name", "Wf11Tbl",
                 "--key-condition-expression", "other = :v",
                 "--expression-attribute-values", '{":v":{"S":"z"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
