from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_pay_per_request_default_read(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_ppr1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_ppr1",
                 "--item", '{"pk":{"S":"pr1"},"data":{"S":"payload"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Tbl_ppr1",
                 "--key", '{"pk":{"S":"pr1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_ppr1", Key={"pk": {"S": "pr1"}})
    assert from_item(resp["Item"]) == {"pk": "pr1", "data": "payload"}
