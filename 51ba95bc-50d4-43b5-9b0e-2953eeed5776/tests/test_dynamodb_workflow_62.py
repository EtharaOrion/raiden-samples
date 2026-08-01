from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_leaves_other_items_intact(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_clo1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_clo1",
                 "--item", '{"pk":{"S":"keep"},"v":{"S":"safe"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_clo1",
                 "--item", '{"pk":{"S":"keep"},"v":{"S":"changed"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Tbl_clo1", Key={"pk": {"S": "keep"}})
    assert from_item(resp["Item"]) == {"pk": "keep", "v": "safe"}
