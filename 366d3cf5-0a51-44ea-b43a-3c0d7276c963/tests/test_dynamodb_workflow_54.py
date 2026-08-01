from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_condition_wrong_val_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf55",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf55",
                 "--item", '{"pk":{"S":"d"},"v":{"N":"5"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf55",
                 "--key", '{"pk":{"S":"d"}}',
                 "--condition-expression", "v = :n",
                 "--expression-attribute-values", '{":n":{"N":"9"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    assert "Item" in ddb_client.get_item(TableName="Wf55", Key={"pk": {"S": "d"}})
