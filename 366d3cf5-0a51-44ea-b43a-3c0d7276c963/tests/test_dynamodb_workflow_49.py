from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_deleteitem_wrong_key_keeps(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf50",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"S"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf50",
                 "--item", '{"pk":{"S":"p"},"sk":{"S":"s1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf50",
                 "--key", '{"pk":{"S":"p"},"sk":{"S":"s2"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="Wf50", Key={"pk": {"S": "p"}, "sk": {"S": "s1"}})
