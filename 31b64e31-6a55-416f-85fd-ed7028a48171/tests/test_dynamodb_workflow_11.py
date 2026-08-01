from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_tables_isolation(cli, ddb_client, tmp_path):
    for name in ("Wf12A", "Wf12B"):
        result = cli("dynamodb", "create-table", "--table-name", name,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf12A",
                 "--item", '{"pk":{"S":"shared"},"src":{"S":"A"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf12B", Key={"pk": {"S": "shared"}})
    assert "Item" not in resp
    resp = ddb_client.get_item(TableName="Wf12A", Key={"pk": {"S": "shared"}})
    assert from_item(resp["Item"]) == {"pk": "shared", "src": "A"}
