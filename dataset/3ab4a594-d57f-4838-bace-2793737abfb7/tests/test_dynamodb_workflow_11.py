from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_nonexistent_idempotent(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf12Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "Wf12Tbl",
                 "--item", '{"pk":{"S":"present"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "delete-item", "--table-name", "Wf12Tbl",
                 "--key", '{"pk":{"S":"absent"}}')
    assert result.returncode == 0

    assert "Item" in ddb_client.get_item(TableName="Wf12Tbl", Key={"pk": {"S": "present"}})
    assert "Item" not in ddb_client.get_item(TableName="Wf12Tbl", Key={"pk": {"S": "absent"}})
