from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_conditional_unchanged(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf8Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "Wf8Tbl",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"orig"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "Wf8Tbl",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"changed"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="Wf8Tbl", Key={"pk": {"S": "c1"}})
    assert from_item(resp["Item"])["v"] == "orig"
