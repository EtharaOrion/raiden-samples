from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_describe(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfPd1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfPd1",
                 "--item", '{"pk":{"S":"pd"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "describe-table", "--table-name", "WfPd1")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfPd1", Key={"pk": {"S": "pd"}})
    assert from_item(resp["Item"]) == {"pk": "pd"}
