from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_names_put_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf39",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf39", "--item", '{"pk":{"S":"n"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf39",
                 "--item", '{"pk":{"S":"n"},"x":{"S":"y"}}',
                 "--condition-expression", "attribute_not_exists(#p)",
                 "--expression-attribute-names", '{"#p":"pk"}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
