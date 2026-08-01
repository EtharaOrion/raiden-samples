from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_repeated_gets_consistent(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf52Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf52Tbl",
                 "--item", '{"pk":{"S":"c"},"v":{"S":"stable"}}')
    assert result.returncode == 0
    for _ in range(3):
        result = cli("dynamodb", "get-item", "--table-name", "Wf52Tbl",
                     "--key", '{"pk":{"S":"c"}}')
        assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf52Tbl", Key={"pk": {"S": "c"}})
    assert from_item(resp["Item"]) == {"pk": "c", "v": "stable"}
