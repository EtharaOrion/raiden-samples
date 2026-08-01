from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_attribute_exists_fails_new(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_aexfail1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_aexfail1",
                 "--item", '{"pk":{"S":"nope"},"v":{"S":"x"}}',
                 "--condition-expression", "attribute_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Tbl_aexfail1", Key={"pk": {"S": "nope"}})
    assert "Item" not in resp
