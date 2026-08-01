from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_attr_exists_fail_new_key(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf48Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf48Tbl",
                 "--item", '{"pk":{"S":"new"},"v":{"S":"x"}}',
                 "--condition-expression", "attribute_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    assert "Item" not in ddb_client.get_item(TableName="Wf48Tbl", Key={"pk": {"S": "new"}})
