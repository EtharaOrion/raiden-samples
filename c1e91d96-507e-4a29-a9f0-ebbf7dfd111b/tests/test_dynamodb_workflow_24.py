from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_client_seed_cli_read(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfCsr1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfCsr1",
                 "--item", '{"pk":{"S":"c"},"v":{"N":"11"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "WfCsr1",
                 "--key", '{"pk":{"S":"c"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfCsr1", Key={"pk": {"S": "c"}})
    assert from_item(resp["Item"]) == {"pk": "c", "v": 11}
