from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_get_composite_delete(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf77",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"N"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf77", "--item", '{"pk":{"S":"p"},"sk":{"N":"1"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="Wf77", Key={"pk": {"S": "p"}, "sk": {"N": "1"}})
    result = cli("dynamodb", "delete-item", "--table-name", "Wf77", "--key", '{"pk":{"S":"p"},"sk":{"N":"1"}}')
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf77", Key={"pk": {"S": "p"}, "sk": {"N": "1"}})
