from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multi_table_puts_isolated_delete(cli, ddb_client, tmp_path):
    for t in ("Wf70a", "Wf70b"):
        result = cli("dynamodb", "create-table", "--table-name", t,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
        result = cli("dynamodb", "put-item", "--table-name", t, "--item", '{"pk":{"S":"shared"}}')
        assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf70a", "--key", '{"pk":{"S":"shared"}}')
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf70a", Key={"pk": {"S": "shared"}})
    assert "Item" in ddb_client.get_item(TableName="Wf70b", Key={"pk": {"S": "shared"}})
