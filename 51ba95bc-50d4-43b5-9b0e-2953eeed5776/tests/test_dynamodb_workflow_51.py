from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_numeric_range_key_items(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_nrk1",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"N"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    for i in range(3):
        result = cli("dynamodb", "put-item", "--table-name", "Tbl_nrk1",
                     "--item", '{"pk":{"S":"g"},"sk":{"N":"%d"},"v":{"S":"row%d"}}' % (i, i))
        assert result.returncode == 0
    for i in range(3):
        resp = ddb_client.get_item(TableName="Tbl_nrk1",
                                   Key={"pk": {"S": "g"}, "sk": {"N": str(i)}})
        assert from_item(resp["Item"]) == {"pk": "g", "sk": i, "v": "row%d" % i}
