from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_composite_seed_get_multiple_sk(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf32Tbl",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"S"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    for s in ("s1", "s2", "s3"):
        result = cli("dynamodb", "put-item", "--table-name", "Wf32Tbl",
                     "--item", '{"pk":{"S":"P"},"sk":{"S":"%s"},"v":{"S":"%s"}}' % (s, s))
        assert result.returncode == 0
    for s in ("s1", "s2", "s3"):
        resp = ddb_client.get_item(TableName="Wf32Tbl",
                                   Key={"pk": {"S": "P"}, "sk": {"S": s}})
        assert from_item(resp["Item"]) == {"pk": "P", "sk": s, "v": s}
