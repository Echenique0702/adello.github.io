#!/usr/bin/env python
from __future__ import division, print_function
import subprocess
import logging
from deployment_configs import *


def get_dc_specifics(data_center):
    try:
        return HADOOP_CONFIGS[data_center], HADOOPCOMMAND
    except KeyError as e:
        logging.error("Selected data center {} unknown!", data_center)
        logging.error(e.message)


def upload_file_to_hdfs(local_file_path, remote_file_path, dc, force=False):
    hadoop_config, hadoop_cmd = get_dc_specifics(dc)

    logging.debug("Uploading {} to {}...".format(local_file_path, remote_file_path))
    # We can upload directly as the directory should be newly created and no equally named file exist
    try:
        cmd = [hadoop_cmd, "--config", hadoop_config, "fs", "-copyFromLocal"]
        if force:
            cmd.append("-f")
        cmd += [local_file_path, remote_file_path]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        logging.debug("done!")
    except subprocess.CalledProcessError as e:
        logging.error("failed!")
        logging.error(e.message)


def ls_in_hdfs(file_path, dc):
    hadoop_config, hadoop_cmd = get_dc_specifics(dc)
    logging.debug("Getting file list in {}".format(file_path))
    files = []
    try:
        files = subprocess.check_output([hadoop_cmd, "--config", hadoop_config, "fs", "-ls", file_path])
        files = files.split("\n")
        files = [line.split(" ") for line in files]
        files = [line for sublist in files for line in sublist]
        files = [line for line in files if line.startswith(file_path)]
    except subprocess.CalledProcessError as e:
        logging.error("HDFS ls failed")
        logging.error(e.message)
    return files


def cp_in_hdfs(source_path, target_path, dc):
    hadoop_config, hadoop_cmd = get_dc_specifics(dc)
    logging.debug("Copying {} to {}".format(source_path, target_path))
    try:
        subprocess.check_output([hadoop_cmd, "--config", hadoop_config, "fs", "-cp", source_path, target_path])
    except subprocess.CalledProcessError as e:
        logging.error("HDFS cp failed")
        logging.error(e.message)


def mv_in_hdfs(source_path, target_path, dc):
    hadoop_config, hadoop_cmd = get_dc_specifics(dc)
    logging.debug("Moving {} to {}".format(source_path, target_path))
    try:
        subprocess.check_output([hadoop_cmd, "--config", hadoop_config, "fs", "-mv", source_path, target_path])
    except subprocess.CalledProcessError as e:
        logging.error("HDFS mv failed")
        logging.error(e.message)


def rm_in_hdfs(path, dc):
    hadoop_config, hadoop_cmd = get_dc_specifics(dc)
    logging.debug("Deleting {}".format(path))
    try:
        subprocess.check_output([hadoop_cmd, "--config", hadoop_config, "fs", "-rm", path])
    except subprocess.CalledProcessError as e:
        logging.error("HDFS rm failed")
        logging.error(e.message)


def mkdir_in_hdfs(path, dc):
    hadoop_config, hadoop_cmd = get_dc_specifics(dc)
    logging.debug("Creating {}".format(path))
    try:
        subprocess.check_output([hadoop_cmd, "--config", hadoop_config, "fs", "-mkdir", "-p", path])
    except subprocess.CalledProcessError as e:
        logging.error("HDFS mkdir failed")
        logging.error(e.message)