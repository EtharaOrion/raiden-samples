from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_get_via_ddb_delete_via_cli(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf65",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf65", "--item", '{"pk":{"S":"g"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="Wf65", Key={"pk": {"S": "g"}})
    result = cli("dynamodb", "delete-item", "--table-name", "Wf65", "--key", '{"pk":{"S":"g"}}')
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf65", Key={"pk": {"S": "g"}})
