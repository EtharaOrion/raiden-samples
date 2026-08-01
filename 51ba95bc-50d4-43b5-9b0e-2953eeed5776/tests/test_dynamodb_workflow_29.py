from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_same_key_thrice_last_wins(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_thrice1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    for v in ("one", "two", "three"):
        result = cli("dynamodb", "put-item", "--table-name", "Tbl_thrice1",
                     "--item", '{"pk":{"S":"t1"},"v":{"S":"%s"}}' % v)
        assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_thrice1", Key={"pk": {"S": "t1"}})
    assert from_item(resp["Item"]) == {"pk": "t1", "v": "three"}
