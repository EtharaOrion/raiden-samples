from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_deleteitem_then_reput(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf24",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf24", "--item", '{"pk":{"S":"r"},"v":{"S":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf24", "--key", '{"pk":{"S":"r"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf24", "--item", '{"pk":{"S":"r"},"v":{"S":"2"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf24", Key={"pk": {"S": "r"}})
    assert from_item(resp["Item"]) == {"pk": "r", "v": "2"}
