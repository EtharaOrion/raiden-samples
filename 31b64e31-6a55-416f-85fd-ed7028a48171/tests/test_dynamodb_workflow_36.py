from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_two_get_missing_key_each(cli, ddb_client, tmp_path):
    for name in ("Wf37A", "Wf37B"):
        result = cli("dynamodb", "create-table", "--table-name", name,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Wf37A",
                 "--key", '{"pk":{"S":"z"}}')
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf37A", Key={"pk": {"S": "z"}})
    assert "Item" not in ddb_client.get_item(TableName="Wf37B", Key={"pk": {"S": "z"}})
