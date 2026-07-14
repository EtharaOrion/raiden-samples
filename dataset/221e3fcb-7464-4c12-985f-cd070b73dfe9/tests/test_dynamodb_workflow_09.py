from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_idempotent(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf_Idem",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "Wf_Idem",
                 "--item", '{"pk":{"S":"present"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "delete-item", "--table-name", "Wf_Idem",
                 "--key", '{"pk":{"S":"absent_key"}}')
    assert result.returncode == 0

    assert "Item" in ddb_client.get_item(TableName="Wf_Idem", Key={"pk": {"S": "present"}})
    assert "Item" not in ddb_client.get_item(TableName="Wf_Idem", Key={"pk": {"S": "absent_key"}})
