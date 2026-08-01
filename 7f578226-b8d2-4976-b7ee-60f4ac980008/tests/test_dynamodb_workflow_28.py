from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_ss_item_readback(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl26",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl26",
                 "--item", '{"pk":{"S":"ss1"},"tags":{"SS":["x","y"]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl26", Key={"pk": {"S": "ss1"}})
    assert set(resp["Item"]["tags"]["SS"]) == {"x", "y"}
