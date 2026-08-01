from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_three_tables_partial_puts(cli, ddb_client, tmp_path):
    for name in ("Wf69A", "Wf69B", "Wf69C"):
        result = cli("dynamodb", "create-table", "--table-name", name,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf69B",
                 "--item", '{"pk":{"S":"only"},"v":{"S":"here"}}')
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf69A", Key={"pk": {"S": "only"}})
    assert from_item(ddb_client.get_item(TableName="Wf69B", Key={"pk": {"S": "only"}})["Item"]) == {"pk": "only", "v": "here"}
    assert "Item" not in ddb_client.get_item(TableName="Wf69C", Key={"pk": {"S": "only"}})
