from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_expr_values_success(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_cevs1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cevs1",
                 "--item", '{"pk":{"S":"cs1"},"status":{"S":"active"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cevs1",
                 "--item", '{"pk":{"S":"cs1"},"status":{"S":"done"}}',
                 "--condition-expression", "#s = :v",
                 "--expression-attribute-names", '{"#s":"status"}',
                 "--expression-attribute-values", '{":v":{"S":"active"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_cevs1", Key={"pk": {"S": "cs1"}})
    assert from_item(resp["Item"]) == {"pk": "cs1", "status": "done"}
