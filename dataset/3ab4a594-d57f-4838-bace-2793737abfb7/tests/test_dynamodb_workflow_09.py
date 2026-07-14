from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_conditional_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf10Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "Wf10Tbl",
                 "--item", '{"pk":{"S":"x1"},"v":{"S":"keep"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "delete-item", "--table-name", "Wf10Tbl",
                 "--key", '{"pk":{"S":"x1"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="Wf10Tbl", Key={"pk": {"S": "x1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["v"] == "keep"
