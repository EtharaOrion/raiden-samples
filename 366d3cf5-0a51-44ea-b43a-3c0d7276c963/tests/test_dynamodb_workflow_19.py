from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deleteitem_condition_success(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf20",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf20", "--item", '{"pk":{"S":"z"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf20",
                 "--key", '{"pk":{"S":"z"}}',
                 "--condition-expression", "attribute_exists(pk)")
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf20", Key={"pk": {"S": "z"}})
