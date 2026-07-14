from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_conditional_fails_no_mutation(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WFUpdCond",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "WFUpdCond",
                 "--item", '{"pk":{"S":"u1"},"status":{"S":"keep"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "update-item", "--table-name", "WFUpdCond",
                 "--key", '{"pk":{"S":"u1"}}',
                 "--update-expression", "SET #s = :v",
                 "--expression-attribute-names", '{"#s":"status"}',
                 "--expression-attribute-values", '{":v":{"S":"changed"},":e":{"S":"nomatch"}}',
                 "--condition-expression", "#s = :e")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    resp = ddb_client.get_item(TableName="WFUpdCond", Key={"pk": {"S": "u1"}})
    assert from_item(resp["Item"])["status"] == "keep"
