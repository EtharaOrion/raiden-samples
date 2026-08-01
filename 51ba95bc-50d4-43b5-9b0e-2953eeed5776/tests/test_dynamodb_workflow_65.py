from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_two_items_get_only_one(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_p2g1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_p2g1",
                 "--item", '{"pk":{"S":"one"},"v":{"S":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_p2g1",
                 "--item", '{"pk":{"S":"two"},"v":{"S":"2"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_p2g1", Key={"pk": {"S": "two"}})
    assert from_item(resp["Item"]) == {"pk": "two", "v": "2"}
