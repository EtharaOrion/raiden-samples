from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_ddb_cli_get_readback(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf38",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf38",
                 "--item", '{"pk":{"S":"p"},"payload":{"S":"hello world"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf38", Key={"pk": {"S": "p"}})
    assert from_item(resp["Item"])["payload"] == "hello world"
