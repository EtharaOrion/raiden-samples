from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_overwrite_updates_item(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfOvr1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfOvr1",
                 "--item", '{"pk":{"S":"o1"},"n":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfOvr1",
                 "--item", '{"pk":{"S":"o1"},"n":{"N":"99"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfOvr1", Key={"pk": {"S": "o1"}})
    assert from_item(resp["Item"]) == {"pk": "o1", "n": 99}
