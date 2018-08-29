---
layout: post
title: deployment.scripts
subtitle: For fast, secure and efficient deployment
category: data
tags: [data science, deployment, automation, scripts]
author: Dhiraj Pathania
header-img: "images/scripting.jpg"
---

First thing that comes to my mind when talking about scripts, is task automation. These days almost everyone in the computer science domain talks about automation. Most development teams are using automation in one form or another. While there are various ongoing debates on this, particularly in industries, in this post we are not going to discuss any of that and neither are we discussing about industrial automation. We will look into the very basic task automation. No AI or machine learning or any of that Skynet stuff. Not yet :-) !

Scripts are extremely useful for automating a lot of frequent and tedious tasks. At Adello, these scripts are everywhere and are used for doing a wide array of tasks: from generating a git tag to deploying a newly developed feature on our production system. The simple philosophy of a script is to complete a task which can only be done in one particular way. Such tasks generally consist of a standard list of sequential actions. So what kind of scripts do we use at Adello? Well, discussing all of them here is neither possible nor practical. But some of the most commonly used scripts in Adello are our deployment scripts, which are the focal point of this post. This is not to say that other scripts are not used that often, but to insinuate the existence of a special category of scripts, doing one particular task: code deployment.

As the name suggests, these are the scripts we use to deploy our new/updated code repositories or to deploy new/updated software libraries on our production systems (multiple data centers located globally). Whenever we need to deploy an artifact, instead of deploying it manually, the task is handed over to these so called, deployment scripts (yes, we have many). To get a better understanding of the content of these scripts, we shall look into two of our deployment scripts available [here](https://github.com/adello/adello.github.io/tree/master/_opensourced_code/_deployment_scripts).

---
At Adello, we use Cloudera Hadoop Distribution (CDH) as our big data platform. Like any other company dealing with big data, we have to create, update, and maintain a variety of ETL pipelines. Many of our pipelines use Apache Oozie Scheduler where we configure our workflows to run actions from Hive, Pig, Spark, Sqoop, HDFS and so on. Whenever we upgrade to a more recent CDH version, we need to redeploy our Oozie libraries. The deployment of Spark and Pig libraries is highly customized to our custom needs and is therefore not included in this post. Oozie supports a ShareLib directory to accommodate the external JAR files of all the actions (such as Distcp, Hive, Sqoop etc.) rather than providing these files in the workflow for each individual action. For each type of action in an Oozie workflow, the correspoding JAR files can be stored in this ShareLib path. Also the old files from this shared directory can be deleted once they are no longer needed. Whenever Oozie needs to be redeployed, for instance after a CDH upgrade, the corresponding JAR files for various actions are to be downloaded from a central repository. The old files are therefore removed from shared path during deployment.

#### Oozie libs deployment script
The main function of deploy-oozie-libs script is shown below.

```python
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
    send_deployment_mail(args.datacenter, args.ad_pig_version, args.java_actions_version, args.email)
```

As shown above, main function performs following steps:
- Verify correct system from which deployment has to be done.
- Check if new artifactories are available for download after build and download them on local system.
- Creating new target directories.
- Upload downloaded artifactories to target locations.
- Upload relevant artifacts or dependent resources to target locations.
- Modify content from ShareLib path.
- Send email notification to responsible team.


All the functions used above are self explanatory. The `download_artifact` function downloads the artifacts to be deployed from our central repository (all artifacts are stored in this repository). Let's have a look at not so obvious function, `modify_share_lib_path`.

```python
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
```
In this function, all dependency artifacts are deployed with the help of a file `artifact_list_file`. This file contains the names of all dependency artifacts which are either to be deployed or to be removed. Depending on whether the new artifact has to be added (marked with a '+' in front of the name) or removed (marked with a '-' in the beginning of the name), these artifacts are uploaded (or removed) to (from) target location (Oozie shared lib path).

---

For quering data stored in Hadoop cluster, we use Hive. But a lot of times, the data stored in cluster needs to be combined together using some logic to get more meaningful or pluggable results. Therefore, we frequently need to write our own UDFs and deploy them on Hive server for regular usage. Once a new UDF branch is merged in the base repository and integration testing is completed successfully, a new release of ad-hive repository is generated. To make this new UDF available for regular use (i.e. to use it like a permanent Hive function), this recent ad-hive version has to be deployed. The deployment process involves the update of underlying code with the new one containing new UDF(s) and registering these UDF(s) with Hive server as permanent functions. We are using Tez as execution engine to run queries on Hive and therefore we need to deploy the JAR file to Hive server local file system as well (in addition to HDFS).


#### Hive deployment script
The `deploy_ad_hive` function from ad-hive deployment script shown below accomplishes following tasks.
- Dowload the artifacts from central repository on the local system.
- Upload jar files to Hive server (needed to run Tez).
- Upload jar files to target HDFS location.
- Register Hive UDFs on Hive server.
- Send email notification to responsible team.

```python
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
    send_deployment_mail(args.datacenter, args.ad_hive_version, args.email, args.branch)
```


Here, `register_permanent_functions` is a special function which actually does the registering of all UDFs with Hive server. This function actually depends on one file we maintain in our ad-hive repo. In the code, this file is extracted from jar files and reference by `PERMANENT_FUNCTIONS_FILE` variable. 

```python
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
```

`PERMANENT_FUNCTIONS_FILE` file consists of the specification of all the UDFs we have in our repository and we want to register with Hive server. A sample of this file with one UDF specification can be found [here](https://github.com/adello/adello.github.io/blob/master/_opensourced_code/_deployment_scripts/UDF_specification_file.hive) (notice the `reload` command at the end of this file). Using `beeline` command, this file is sent to the desired Hive server via a JDBC connection. After this, all UDFs have been registered in Hive permanently.

There are several other deployment sub-tasks apart from the ones discussed above which can be delegated to deployment scripts. Some of these sub-tasks are:

- Validating address and configuration of the target system.
- Assigning right permissions to the newly deployed repositories.
- Add/update the relevant fields to some existing configuration file (or generate a new config file).
- If required, renaming or removing earlier deployed versions.

---
Now, all these tasks are done by a script. In short, these are all the things that we, as developers, do not have to worry about. But most importantly, since deployment is done using these scripts, everything that needs to be done will be done in a predefined order without "forgetting" any step. This reduces the impact on production systems mainly because of two reasons:

- Automated deployment would result in smooth deployment and therefore, reduces the chances of botching up the deployment on running system.
- In case anything goes wrong, reverting to previous state (redeploying last stable release) can be done as quickly using these same scripts.

Given that we deploy our repos quite frequently, writing such scripts saves a lot of time in the long run. Also, the target datacenter and the versions of artifacts which we want to deploy are configured as arguments to the script on command line, giving all the control to user while maintaining flexibility during deployment.

Deployment is not the only place where we do this. There are various other tasks which end up taking a lot of time on daily basis. While working with data, we have to create or update multiple data pipelines. Writing an Oozie pipeline in XML file can be a tedious task. When we know that this same thing needs to be done multiple times in future as well, there is a clear incentive to automate the whole thing. There comes a generating script which generates a skeleton of an Oozie pipeline. A templating script which replicates the workflow actions with different parameters and so on. But in case of deployment, using scripts also minimizes the risk of running into some unintended problems because of human error while ensuring fast deployment.

This leaves a lot less and hopefully, more important things for developers to worry about. They do not have to worry about the deployment locations and the files to be copied. All deployment steps will be handled by the script. If the scripts are written well, they can be easily plugged into an end-to-end automation system in future. Therefore, it is important that only the part which involves a set of specific tasks is implemented, configuration is managed properly and variables like target data center or release version are taken as input. This makes the scripts generic, easy to maintain and reusable. 

I agree that not everything can be automated and not every trivial task is worth automating. But a big chunk of tedious tasks, which developers do more frequently than they think, can be automated easily. Scripts are easy to write and a powerfull tool. They take the burden of doing essential but tedious tasks off the shoulders of developers. However, identifying these tasks which are worth automating, is something which comes with time. Software deployment, I would argue, is one such task.

