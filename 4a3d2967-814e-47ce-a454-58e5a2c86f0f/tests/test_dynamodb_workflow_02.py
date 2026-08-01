from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_missing_table(cli, ddb_client, tmp_path):
    t = "wf_scan_missing_3"
    result = cli("dynamodb", "scan", "--table-name", t)
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
