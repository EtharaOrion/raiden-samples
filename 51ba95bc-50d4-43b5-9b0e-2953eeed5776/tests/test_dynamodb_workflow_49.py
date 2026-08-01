from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_with_expr_values(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_cev1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cev1",
                 "--item", '{"pk":{"S":"cv1"},"status":{"S":"active"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cev1",
                 "--item", '{"pk":{"S":"cv1"},"status":{"S":"closed"}}',
                 "--condition-expression", "#s = :v",
                 "--expression-attribute-names", '{"#s":"status"}',
                 "--expression-attribute-values", '{":v":{"S":"inactive"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Tbl_cev1", Key={"pk": {"S": "cv1"}})
    assert from_item(resp["Item"]) == {"pk": "cv1", "status": "active"}
