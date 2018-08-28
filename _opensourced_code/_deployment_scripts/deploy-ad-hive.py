#!/usr/bin/env python
from __future__ import division, print_function

import argparse
import logging
import subprocess

# Function to download specific artifacts from repository
from artifact_download import download_artifact

from deployment_configs import *
from shared_functions import send_deployment_mail
import hdfs_functions as hdfs

# Some config constants
HIVE_SERVER2_AUX_JARS_DIR = "/opt/local/hive/lib"
BEELINE_CMD = os.path.join(DEFAULT_CDH_PATH, "bin", "beeline")
HDFSDIR = "/user/oozie"
PERMANENT_FUNCTIONS_FILE = "permanent_functions.hive"
HIVE_PORT = 10000

DEV_TEAM_EMAIL_ID = "<dev_team_email_address>"


def upload_hive_jar_to_hiveserver(ad_hive_jar, dc, username="user"):
    hive_server = HIVE_SERVERS[dc]
    cmd = ["ssh", "{}@{}".format(username, hive_server), "rm", "-f",
           "{}/ad-hive*.jar".format(HIVE_SERVER2_AUX_JARS_DIR)]
    logging.debug("Deleting old ad-hive jars on hive server with: {}".format(cmd))
    subprocess.check_output(cmd)

    cmd = ["scp", ad_hive_jar, "{}@{}:{}".format(username, hive_server, HIVE_SERVER2_AUX_JARS_DIR)]
    logging.debug("Copying new ad-hive jar to hive server with: {}".format(cmd))
    subprocess.check_output(cmd)


def upload_hive_jar_to_hdfs(ad_hive_jar, dc):
    filename = os.path.basename(ad_hive_jar)
    logging.debug("Delete old ad-hive jar {} from hdfs.".format(os.path.join(HDFSDIR, filename)))
    hdfs.rm_in_hdfs(os.path.join(HDFSDIR, filename), dc)

    logging.debug("Uploading ad-hive jar to hdfs path {}".format(HDFSDIR))
    hdfs.upload_file_to_hdfs(ad_hive_jar, HDFSDIR, dc)


def register_permanent_functions(ad_hive_jar, dc):
    cmd = ["jar", "-xf", ad_hive_jar, PERMANENT_FUNCTIONS_FILE]
    logging.debug("Extracting permanent functions file with: {}".format(cmd))
    subprocess.check_output(cmd)

    hive_server = HIVE_SERVERS[dc]
    namenode = NAMENODES[dc]
    jdbc_url = "jdbc:hive2://{}:10000/default".format(hive_server)
    cmd = [BEELINE_CMD, "-n", "deployment", "-u", jdbc_url, "--hiveconf",
           "ARTIFACT={}".format(os.path.basename(ad_hive_jar))]
    cmd += ["--hiveconf", "NAMENODE={}".format(namenode), "--fastConnect=true", "-f", PERMANENT_FUNCTIONS_FILE]
    logging.debug("Registering permanent functions with: {}".format(cmd))
    subprocess.check_output(cmd)

    cmd = ["rm", PERMANENT_FUNCTIONS_FILE]
    logging.debug("Deleting permanent functions file with: {}".format(cmd))
    subprocess.check_output(cmd)


def deploy_ad_hive():
    parser = argparse.ArgumentParser(description='Argument parser')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument("--datacenter", help="Sync only one given data center. If not specified will sync all "
                                             "data centers.", choices=DATACENTERS, required=True)
    parser.add_argument("--branch", default="master", help="deployed ad-hive branch")
    parser.add_argument("--ad-hive-version", help="Version string of ad-hive to deploy", required=True)
    parser.add_argument("--email", help="notification email address", default=DEV_TEAM_EMAIL_ID)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    ad_hive_jar = download_artifact("com.hstreaming", "ad-hive", args.ad_hive_version, "dist", "/tmp", args.branch)
    logging.info("Downloaded {}".format(ad_hive_jar))

    logging.info("Uploading ad-hive jar to hiveserver")
    upload_hive_jar_to_hiveserver(ad_hive_jar, args.datacenter)

    logging.info("Uploading ad-hive jar to hdfs")
    upload_hive_jar_to_hdfs(ad_hive_jar, args.datacenter)

    logging.info("Registering permanent functions")
    register_permanent_functions(ad_hive_jar, args.datacenter)

    logging.info("Done!")
    send_deployment_mail(args.datacenter, ["ad-hive"], [args.ad_hive_version], args.email, args.branch)


if __name__ == "__main__":
    deploy_ad_hive()
