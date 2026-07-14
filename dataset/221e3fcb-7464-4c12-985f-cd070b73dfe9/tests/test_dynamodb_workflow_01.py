from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_delete_item(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf_DelItem",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "Wf_DelItem",
                 "--item", '{"pk":{"S":"gone"},"v":{"S":"x"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="Wf_DelItem", Key={"pk": {"S": "gone"}})

    result = cli("dynamodb", "delete-item", "--table-name", "Wf_DelItem",
                 "--key", '{"pk":{"S":"gone"}}')
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName="Wf_DelItem", Key={"pk": {"S": "gone"}})
    assert "Item" not in resp
