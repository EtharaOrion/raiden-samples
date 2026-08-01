from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_exists_missing_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfCem1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfCem1",
                 "--item", '{"pk":{"S":"ghost"},"v":{"S":"x"}}',
                 "--condition-expression", "attribute_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfCem1", Key={"pk": {"S": "ghost"}})
    assert "Item" not in resp
