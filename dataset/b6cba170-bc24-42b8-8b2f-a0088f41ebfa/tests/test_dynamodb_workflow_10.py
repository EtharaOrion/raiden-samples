from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_nonkey_attribute_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WFQueryNonKey",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "WFQueryNonKey",
                 "--item", '{"pk":{"S":"q1"},"other":{"S":"foo"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "query", "--table-name", "WFQueryNonKey",
                 "--key-condition-expression", "other = :v",
                 "--expression-attribute-values", '{":v":{"S":"foo"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
