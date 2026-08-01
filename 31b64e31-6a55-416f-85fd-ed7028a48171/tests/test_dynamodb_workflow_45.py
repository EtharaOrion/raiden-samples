from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seq_create_put_get_delete_like(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf46Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf46Tbl",
                 "--item", '{"pk":{"S":"a"},"v":{"S":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Wf46Tbl",
                 "--key", '{"pk":{"S":"a"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf46Tbl", Key={"pk": {"S": "a"}})
    assert from_item(resp["Item"]) == {"pk": "a", "v": "1"}
