from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_condition_no_mutation(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfUC1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "WfUC1",
                 "--item", '{"pk":{"S":"u1"},"n":{"N":"10"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "update-item", "--table-name", "WfUC1",
                 "--key", '{"pk":{"S":"u1"}}',
                 "--update-expression", "SET n = :new",
                 "--expression-attribute-values", '{":new":{"N":"20"},":exp":{"N":"999"}}',
                 "--condition-expression", "n = :exp")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="WfUC1", Key={"pk": {"S": "u1"}})
    assert from_item(resp["Item"])["n"] == 10
