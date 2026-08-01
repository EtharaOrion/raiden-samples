from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_binary_attr_put_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf33Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf33Tbl",
                 "--item", '{"pk":{"S":"bin"},"data":{"B":"aGVsbG8="}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf33Tbl", Key={"pk": {"S": "bin"}})
    assert "data" in resp["Item"]
