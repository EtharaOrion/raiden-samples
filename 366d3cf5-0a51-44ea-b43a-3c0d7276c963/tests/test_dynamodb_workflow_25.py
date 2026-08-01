from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_value_put_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf26",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf26",
                 "--item", '{"pk":{"S":"c"},"st":{"S":"A"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf26",
                 "--item", '{"pk":{"S":"c"},"st":{"S":"B"}}',
                 "--condition-expression", "st = :want",
                 "--expression-attribute-values", '{":want":{"S":"Z"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf26", Key={"pk": {"S": "c"}})
    assert from_item(resp["Item"]) == {"pk": "c", "st": "A"}
