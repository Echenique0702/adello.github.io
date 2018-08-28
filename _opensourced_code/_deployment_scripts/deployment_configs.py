import os

DATACENTERS = ["DC1", "DC2", "DC3", "DC4", "DC5"]
TESTDC = "DC_TEST"

OOZIE_SERVERS = {"DC1": "http://oozie.dc1.server:PORT/oozie",
                 "DC2": "http://oozie.dc2.server:PORT/oozie",
                 "DC3": "http://oozie.dc2.server:PORT/oozie",
                 "DC4": "http://oozie.dc2.server:PORT/oozie",
                 "DC5": "http://oozie.dc2.server:PORT/oozie"}

HADOOP_CONFIGS = {"DC1": "/etc/hadoop/conf.yarndc1",
                  "DC2": "/etc/hadoop/conf.yarndc2",
                  "DC3": "/etc/hadoop/conf.yarndc3",
                  "DC4": "/etc/hadoop/conf.yarndc4",
                  "DC5": "/etc/hadoop/conf.yarndc5"}

HIVE_SERVERS = {"DC1": "DC1-hive.server",
                "DC4": "DC4-hive.server",
                "DC5": "DC5-hive.server"}

NAMENODES = {"DC1": "hdfs://DC1-nameservice",
             "DC2": "hdfs://DC2-nameservice",
             "DC3": "hdfs://DC3-nameservice",
             "DC4": "hdfs://DC4-nameservice",
             "DC5": "hdfs://DC5-nameservice"}

HADOOP_MANAGERS = {"DC1": "dc1-hadoopmgr.adello.com",
                   "DC2": "dc2-hadoopmgr.adello.com",
                   "DC3": "dc3-hadoopmgr.adello.com",
                   "DC4": "dc4-hadoopmgr.adello.com",
                   "DC5": "dc5-hadoopmgr.adello.com"}

# oozie service names; they are different, although they belong to different clusters, since they live under the rule
# of the same manager
OOZIE_SERVICE_NAMES = {"DC3": "oozie",
                       "DC1": "oozie2",
                       "DC2": "oozie3",
                       "DC4": "oozie",
                       "DC5": "oozie"}

HIVE_PORT = 10000
DEFAULT_CDH_PATH = "/opt/cloudera/parcels/CDH"
HADOOPCOMMAND = os.path.join(DEFAULT_CDH_PATH, "bin", "hadoop")
