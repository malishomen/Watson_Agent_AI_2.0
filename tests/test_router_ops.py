# -*- coding: utf-8 -*-
from utils.router_core import plan_and_route

def test_ops_smoke_slash_command():
    r = plan_and_route("/smoke host=staging.example.com")
    assert r["intent"] == "ops_smoke"
    assert r["args"]["host"] == "staging.example.com"

def test_ops_smoke_natural_phrase():
    r = plan_and_route("staging-smoke: verify /health and /metrics host=staging.local")
    assert r["intent"] == "ops_smoke"
    assert r["args"]["host"] == "staging.local"

def test_ops_deploy_slash():
    r = plan_and_route("/deploy host=staging.example.com ref=main")
    assert r["intent"] == "ops_deploy"
    assert r["args"]["host"] == "staging.example.com"
    assert r["args"]["ref"] == "main"

def test_ops_promote_slash():
    r = plan_and_route("/promote host=staging.example.com tag=abc1234")
    assert r["intent"] == "ops_promote"
    assert r["args"]["tag"] == "abc1234"

def test_ops_rollback_slash():
    r = plan_and_route("/rollback host=staging.example.com to=prev")
    assert r["intent"] == "ops_rollback"
    assert r["args"]["to"] == "prev"


