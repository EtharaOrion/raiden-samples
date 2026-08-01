from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_number_and_string_mixed(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl20",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl20",
                 "--item", '{"pk":{"S":"mix1"},"name":{"S":"joe"},"age":{"N":"30"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl20", Key={"pk": {"S": "mix1"}})
    assert resp["Item"]["name"]["S"] == "joe"
    assert resp["Item"]["age"]["N"] == "30"
