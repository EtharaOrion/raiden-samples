from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_absent_after_seed_other_key(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf74Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    ddb_client.put_item(TableName="Wf74Tbl", Item={"pk": {"S": "present"}, "v": {"S": "y"}})
    result = cli("dynamodb", "get-item", "--table-name", "Wf74Tbl",
                 "--key", '{"pk":{"S":"absent"}}')
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf74Tbl", Key={"pk": {"S": "absent"}})
    assert "Item" in ddb_client.get_item(TableName="Wf74Tbl", Key={"pk": {"S": "present"}})
