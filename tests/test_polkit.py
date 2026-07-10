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
