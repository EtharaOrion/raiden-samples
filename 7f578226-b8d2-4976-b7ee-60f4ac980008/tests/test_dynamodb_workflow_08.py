from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_conditional_put_fails_existing(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl6",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl6",
                 "--item", '{"pk":{"S":"e1"},"v":{"S":"orig"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl6",
                 "--item", '{"pk":{"S":"e1"},"v":{"S":"new"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfTbl6", Key={"pk": {"S": "e1"}})
    assert resp["Item"]["v"]["S"] == "orig"
