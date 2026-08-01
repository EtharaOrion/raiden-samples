from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_item_consistent_read_flag(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_cr1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cr1",
                 "--item", '{"pk":{"S":"cr1"},"v":{"S":"strong"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Tbl_cr1",
                 "--key", '{"pk":{"S":"cr1"}}', "--consistent-read")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_cr1", Key={"pk": {"S": "cr1"}},
                               ConsistentRead=True)
    assert from_item(resp["Item"]) == {"pk": "cr1", "v": "strong"}
