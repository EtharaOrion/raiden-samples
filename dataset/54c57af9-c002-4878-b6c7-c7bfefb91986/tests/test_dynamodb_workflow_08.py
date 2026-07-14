from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_condition_leaves_item(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfPC1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "WfPC1",
                 "--item", '{"pk":{"S":"c1"},"v":{"N":"1"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "WfPC1",
                 "--item", '{"pk":{"S":"c1"},"v":{"N":"999"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="WfPC1", Key={"pk": {"S": "c1"}})
    assert from_item(resp["Item"])["v"] == 1
