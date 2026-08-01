from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_tables_isolated(cli, ddb_client, tmp_path):
    for t in ("Wf22a", "Wf22b"):
        result = cli("dynamodb", "create-table", "--table-name", t,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf22a", "--item", '{"pk":{"S":"k"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="Wf22a", Key={"pk": {"S": "k"}})
    assert "Item" not in ddb_client.get_item(TableName="Wf22b", Key={"pk": {"S": "k"}})
