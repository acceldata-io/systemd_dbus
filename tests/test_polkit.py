"""Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""
from unittest.mock import patch, MagicMock
import pytest
import sys


def _fake_popen(stdout=b"", stderr=b""):
    proc = MagicMock()
    proc.communicate.return_value = (stdout, stderr)
    return proc

def test_polkit_rule():
    from systemd_dbus import PolkitRule

    expected = \
"""polkit.addRule(function(action, subject) {
  if(action.id === "org.freedesktop.systemd1.manage-units") {
    var permitted_users = ["kudu"];
    if (action.lookup("unit") === "") {
      var verb = action.lookup("verb");
      if (subject.active && permitted_users.indexOf(subject.user) !== -1 && subject.isInGroup("kudu")) {
        if (verb === "start" || verb === "stop" || verb === "restart") {
          polkit.log("User '" + subject.user + "' was permitted to '" + verb + "' unit file ''")
          return polkit.Result.YES;
        }
      } else if (subject.user === "ambari") {
        if (verb === "start" || verb === "stop" || verb === "restart" || verb === "enable" || verb === "disable") {
          polkit.log("User '" + subject.user + "' was permitted to '" + verb + "' unit file ''")
          return polkit.Result.YES;
        }
      } else {
        return polkit.Result.NO;
      }
    }
  }
});""".strip()

    polkit_rule = str(PolkitRule("kudu", users=["kudu"], group="kudu", ambari_user="ambari")).strip()
    assert(polkit_rule == expected)

def test_manual_polkit_rule():
    from systemd_dbus import PolkitRule

    value = "abcdefg"
    expected="hello, abcdefg"
    test_input = "hello, {{value}}"

    polkit_rule = str(PolkitRule("hdfs", users=["hdfs"], group="hadoop", manual_rules=test_input, value=value))
    assert(polkit_rule == expected)

@pytest.mark.parametrize("bad_version", [None, 105])
def test_write_rule_systemd_version_invalid(tmp_path, bad_version):
    from systemd_dbus import PolkitRule
    rule = PolkitRule("test", users=["some_user", "hdfs"], ambari_user="ambari")
    rule_file = tmp_path / rule.name
    with patch.object(PolkitRule, "version", return_value=bad_version):
        assert rule.write(tmp_path) is False
    assert not rule_file.exists()

def test_write_rule_success(tmp_path):
    from systemd_dbus import PolkitRule
    rule = PolkitRule("test", users=["some_user", "hdfs"], ambari_user="ambari")
    rule_file = tmp_path / rule.name
    with patch.object(PolkitRule, "version", return_value=110):
        assert rule.write(tmp_path) is True
    assert rule_file.exists()

def test_write_rule_using_open_not_sudo(tmp_path):
    from systemd_dbus import PolkitRule

    rule = PolkitRule("test", users=["some_user", "hdfs"], ambari_user="ambari")

    with patch.object(PolkitRule, "version", return_value=110), \
        patch.dict(sys.modules, {"resource_management.core": None}):

        assert rule.write(tmp_path) is True

    assert (tmp_path / rule.name).exists()

def test_write_rule_using_sudo_return(tmp_path):
    from systemd_dbus import PolkitRule
    rule = PolkitRule("test", users=["some_user", "hdfs"], ambari_user="ambari")

    fake_sudo = MagicMock()
    fake_core = MagicMock(sudo=fake_sudo)
    with patch.object(PolkitRule, "version", return_value=110), \
         patch.dict(sys.modules, {
             "resource_management": MagicMock(),
             "resource_management.core": fake_core,
         }):
        assert rule.write(str(tmp_path)) is True

    fake_sudo.create_file.assert_called_once()

def test_version_parses_number():
    from systemd_dbus import PolkitRule

    target = "{}.Popen".format(PolkitRule.__module__)
    rule = PolkitRule("test", users=["test"])
    with patch(target, return_value=_fake_popen(stdout=b"pkaction version 0.117")):
        assert rule.version() == 117

def test_version_with_stderr():
    from systemd_dbus import PolkitRule

    target = "{}.Popen".format(PolkitRule.__module__)
    rule = PolkitRule("test", users=["test"])
    with patch(target, return_value=_fake_popen(stdout=b"pkaction version 0.117", stderr=b"command not found")):
        assert rule.version() is None

def test_version_no_match():
    from systemd_dbus import PolkitRule

    target = "{}.Popen".format(PolkitRule.__module__)
    rule = PolkitRule("test", users=["test"])
    with patch(target, return_value=_fake_popen(stdout=b"some output here")):
        assert rule.version() is None
