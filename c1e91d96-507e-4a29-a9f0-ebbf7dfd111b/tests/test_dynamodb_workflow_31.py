from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_expr_attr_names_condition(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfEan1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfEan1",
                 "--item", '{"pk":{"S":"n1"},"status":{"S":"a"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfEan1",
                 "--item", '{"pk":{"S":"n1"},"status":{"S":"b"}}',
                 "--condition-expression", "attribute_not_exists(#s)",
                 "--expression-attribute-names", '{"#s":"pk"}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfEan1", Key={"pk": {"S": "n1"}})
    assert from_item(resp["Item"]) == {"pk": "n1", "status": "a"}
