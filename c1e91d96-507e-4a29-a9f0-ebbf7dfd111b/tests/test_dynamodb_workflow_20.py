from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_binary_attribute(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfBin1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfBin1",
                 "--item", '{"pk":{"S":"bin"},"b":{"B":"aGVsbG8="}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfBin1", Key={"pk": {"S": "bin"}})
    assert "b" in resp["Item"]
