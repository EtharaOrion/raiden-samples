from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_after_two_puts_different_keys(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_twk1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_twk1",
                 "--item", '{"pk":{"S":"kA"},"v":{"S":"A"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_twk1",
                 "--item", '{"pk":{"S":"kB"},"v":{"S":"B"}}')
    assert result.returncode == 0
    respA = ddb_client.get_item(TableName="Tbl_twk1", Key={"pk": {"S": "kA"}})
    respB = ddb_client.get_item(TableName="Tbl_twk1", Key={"pk": {"S": "kB"}})
    assert from_item(respA["Item"]) == {"pk": "kA", "v": "A"}
    assert from_item(respB["Item"]) == {"pk": "kB", "v": "B"}
