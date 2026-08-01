from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_expr_names_only_fail(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_cen1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cen1",
                 "--item", '{"pk":{"S":"ce1"},"status":{"S":"on"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cen1",
                 "--item", '{"pk":{"S":"ce1"},"status":{"S":"off"}}',
                 "--condition-expression", "attribute_not_exists(#p)",
                 "--expression-attribute-names", '{"#p":"pk"}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Tbl_cen1", Key={"pk": {"S": "ce1"}})
    assert from_item(resp["Item"]) == {"pk": "ce1", "status": "on"}
