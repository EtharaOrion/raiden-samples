from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_numeric_key_type(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfNk1",
                 "--attribute-definitions", '[{"AttributeName":"id","AttributeType":"N"}]',
                 "--key-schema", '[{"AttributeName":"id","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfNk1",
                 "--item", '{"id":{"N":"100"},"name":{"S":"hundred"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfNk1", Key={"id": {"N": "100"}})
    assert from_item(resp["Item"]) == {"id": 100, "name": "hundred"}
