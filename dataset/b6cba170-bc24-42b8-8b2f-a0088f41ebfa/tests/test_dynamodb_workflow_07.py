from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_conditional_fails_leaves_item(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WFPutCond",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "WFPutCond",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"first"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "WFPutCond",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"second"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    resp = ddb_client.get_item(TableName="WFPutCond", Key={"pk": {"S": "c1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["v"] == "first"
