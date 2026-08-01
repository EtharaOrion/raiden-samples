from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_condition_delete_after(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf54",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf54",
                 "--item", '{"pk":{"S":"d"},"v":{"N":"5"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf54",
                 "--key", '{"pk":{"S":"d"}}',
                 "--condition-expression", "v = :n",
                 "--expression-attribute-values", '{":n":{"N":"5"}}')
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf54", Key={"pk": {"S": "d"}})
