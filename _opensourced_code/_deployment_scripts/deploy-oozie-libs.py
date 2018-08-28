#!/usr/bin/env python
from __future__ import print_function, division

import argparse
import inspect
import logging
import os
import socket
import sys
import time

import requests
# Used to download specific artifacts from repository
from artifact_download import download_artifact

import hdfs_functions as hdfs
from deployment_configs import OOZIE_SERVERS, HADOOP_MANAGERS, OOZIE_SERVICE_NAMES, DATACENTERS
from shared_functions import send_deployment_mail

AUX_ARTIFACT_LIST = "artifacts.list"
HOSTNAME = "<hostname>"
DATASCIENCE_MAIL = "<data_science_team_email_address>"

SCRIPTROOT = os.path.join(os.path.dirname(os.path.realpath(inspect.getfile(inspect.currentframe()))), '../')
sys.path.append(os.path.join(SCRIPTROOT, 'deployment'))


# --------------- Helper methods --------------------------------------------------------------------------------------
def check_aux_jars_path(artifact_list_file, aux_jars_path):
    if not os.path.exists(aux_jars_path):
        raise RuntimeError("Aux jars path does not exist! ({})".format(aux_jars_path))

    with open(artifact_list_file, "r") as artifact_list:
        for line in artifact_list:
            if line.startswith("+"):
                line = line.strip().lstrip("+")
                artifact = os.path.join(aux_jars_path, line)
                if not os.path.isfile(artifact):
                    raise RuntimeError("Artifact {} not found, but configured in artifact list.".format(artifact))


# ---------------- Oozie share lib methods ----------------------------------------------------------------------------
# Setting up a new oozie sharelib folder using the hadoop manager rest API.
# Unfortunately, the location of the new folder needs be extracted using good old hadoop fs cmds.
#  This method will make this according to the current parameters.
def create_new_oozie_share_folder(dc, user, password):
    oozie_service_name = OOZIE_SERVICE_NAMES[dc]
    hadoop_manager = HADOOP_MANAGERS[dc]
    logging.info("Creating new share lib folder...")
    rest_url = 'http://{}:7180/api/v10/clusters/{}/services/{}/commands/installOozieShareLib'.format(hadoop_manager, dc,
                                                                                                     oozie_service_name)
    logging.debug("with rest url: {}".format(rest_url))
    res = requests.post(rest_url, auth=requests.auth.HTTPBasicAuth(user, password))
    if res.status_code != 200:
        raise RuntimeError("Creating new oozie share lib failed with: {}".format(res.text))

    # Here we need to wait for some time to ensure that Sharelib path is created above.
    logging.debug("Waiting 600 seconds for oozie...")
    time.sleep(600)

    liblist = hdfs.ls_in_hdfs("/user/oozie/share/lib", dc)
    liblist = sorted(liblist, reverse=True)
    for liblist_folder in liblist:
        if os.path.basename(liblist_folder).startswith("lib_"):
            logging.debug("New sharelib folder: {}".format(liblist_folder))
            return liblist_folder
    raise RuntimeError("No propert lib folder found for liblist: {}".format(liblist))


def modify_share_lib_path(artifact_list_file, aux_jars_path, oozie_share_lib_path, dc):
    with open(artifact_list_file, "r") as artifact_list:
        for line in artifact_list:
            if line.startswith("#"):
                continue
            elif line.startswith("+"):
                line = line.strip().lstrip("+")
                artifact = os.path.join(aux_jars_path, line)
                if not os.path.isfile(artifact):
                    raise RuntimeError("Artifact {} not found, but configured in artifact list.".format(artifact))
                remote_path = os.path.join(oozie_share_lib_path, line)
                logging.debug("Uploading {} to {}".format(artifact, remote_path))
                hdfs.upload_file_to_hdfs(artifact, remote_path, dc)
            elif line.startswith("-"):
                line = line.strip().lstrip("-")
                remote_path = os.path.join(oozie_share_lib_path, line)
                logging.debug("Deleting {} from HDFS.".format(remote_path))
                hdfs.rm_in_hdfs(remote_path, dc)
            else:
                raise RuntimeError("line {} not correctly formatted. Must start with +,-, or #.".format(line))


def update_oozie_share_lib(dc):
    logging.info("Updating to new share lib folder...")
    oozie_url = OOZIE_SERVERS[dc]
    rest_url = '{}/v2/admin/update_sharelib'.format(oozie_url)
    logging.debug("with rest url: {}".format(rest_url))
    res = requests.get(rest_url)
    if res.status_code != 200:
        raise RuntimeError("Update of oozie share lib failed with: {}".format(res.text))
    logging.debug(res.text)


# ---------------- Upload methods -------------------------------------------------------------------------------------
def upload_artifact(local_artifact_uri, oozie_share_lib_path, subfolder, dc):
    remote_path = os.path.join(oozie_share_lib_path, subfolder) + "/"
    logging.debug("Creating directory {} if not exists".format(remote_path))
    hdfs.mkdir_in_hdfs(remote_path, dc)
    logging.debug("Uploading {} to {}".format(local_artifact_uri, remote_path))
    hdfs.upload_file_to_hdfs(local_artifact_uri, remote_path, dc)


class WrongHostException(Exception):
    pass


def check_hostname():
    host = socket.gethostname()
    if host != HOSTNAME:
        raise WrongHostException("deploy-oozie-libs.py can only be executed from <HOSTNAME> machine")


# ----------------- Main ----------------------------------------------------------------------------------------------
def main():
    check_hostname()

    # Download ad-pig jar
    ad_pig_jar = download_artifact("com.hstreaming", "ad-pig", args.ad_pig_version, "dist", "/tmp", args.ad_pig_branch)
    logging.info("Downloaded {}".format(ad_pig_jar))

    # Download java actions jar
    java_actions_jar = download_artifact("com.adello", "oozie-java-actions", args.java_actions_version, "dist", "/tmp",
                                         args.java_actions_branch)
    logging.info("Downloaded {}".format(java_actions_jar))

    # Create new share lib folder
    share_lib_path = create_new_oozie_share_folder(args.datacenter, args.managerUser, args.managerPassword)

    # Upload ad-pig jar (will create target folder if needed)
    logging.info("Uploading ad-pig...")
    upload_artifact(ad_pig_jar, share_lib_path, "pig", args.datacenter)

    # Upload java actions jar (will create target folder if needed)
    logging.info("Uploading java actions...")
    upload_artifact(java_actions_jar, share_lib_path, "java", args.datacenter)

    # Modify newly generated sharelib path
    logging.info("Modifying new share lib path")
    modify_share_lib_path(args.artifact_list, args.aux_jars_path, share_lib_path, args.datacenter)

    # Make new share lib the default oozie share lib folder
    update_oozie_share_lib(args.datacenter)
    logging.info("done!")
    send_deployment_mail(args.datacenter, ["ad-pig", "java-actions"], [args.ad_pig_version, args.java_actions_version],
                         args.email)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     epilog="Helper script to deploy aux jars to oozie/share/lib\n"
                                            "Execute as <user> on <HOSTNAME>!\n"
                                            "Sample call:\n ./deploy-oozie-libs.py --datacenter <DC> "
                                            "--ad-pig-version 1.0.0 --java-actions-version 0.1.0 "
                                            "--aux-jars-path oozie-share-aux-jars "
                                            "-p <pw> -u <user> "
                                            "--parquet 1.5.0-cdh5.6.0-ADELLO")
    parser.add_argument("--datacenter", help="Sync only one given data center. If not specified will sync all "
                                             "data centers.", choices=DATACENTERS, required=True)
    parser.add_argument("--ad-pig-version", help="Version string of ad-pig to deploy", required=True)
    parser.add_argument("--java-actions-version", help="Version string of oozie java actions to deploy", required=True)
    parser.add_argument("--ad-pig-branch", help="branch of ad-pig build", default="master")
    parser.add_argument("--java-actions-branch", help="branch of java-actions build", default="master")
    parser.add_argument("--aux-jars-path", help="Path to folder containing aux jars", default="~/oozie-share-aux-jars")
    parser.add_argument("--artifact-list", help="Path to artifact list file", default="artifacts.list")
    parser.add_argument("-u", "--managerUser", help="Username of the hadoop cluster manager", type=str, required=True)
    parser.add_argument("-p", "--managerPassword", help="Password of the hadoop cluster manager", type=str,
                        required=True)
    parser.add_argument("--email", help="notification email address", default=DATASCIENCE_MAIL)
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()
    args.aux_jars_path = args.aux_jars_path.replace("~", os.path.expanduser("~"))

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    check_aux_jars_path(args.artifact_list, args.aux_jars_path)
    main()
