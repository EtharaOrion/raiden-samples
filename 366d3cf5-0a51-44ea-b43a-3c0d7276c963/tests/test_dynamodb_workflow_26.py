from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_value_put_success(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf27",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf27",
                 "--item", '{"pk":{"S":"c"},"st":{"S":"A"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf27",
                 "--item", '{"pk":{"S":"c"},"st":{"S":"B"}}',
                 "--condition-expression", "st = :want",
                 "--expression-attribute-values", '{":want":{"S":"A"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf27", Key={"pk": {"S": "c"}})
    assert from_item(resp["Item"]) == {"pk": "c", "st": "B"}
