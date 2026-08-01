from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_nested_map_readback(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf71",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf71",
                 "--item", '{"pk":{"S":"n"},"data":{"M":{"inner":{"M":{"k":{"N":"3"}}}}}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf71", Key={"pk": {"S": "n"}})
    assert from_item(resp["Item"]) == {"pk": "n", "data": {"inner": {"k": 3}}}
