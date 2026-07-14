from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_conditional_fails_unchanged(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfCond1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "WfCond1",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"first"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "WfCond1",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"second"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="WfCond1", Key={"pk": {"S": "c1"}})
    assert from_item(resp["Item"])["v"] == "first"
