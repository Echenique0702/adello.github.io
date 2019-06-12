---
layout: post
title: Continuous Delivery for Data Science projects
subtitle: Running things with no clicks
category: data
tags: [howto, devops]
author: Bastian Kronenbitter
header-img: "images/scripting.jpg"
---

Hi all, today I want to write about a more mundane topic: Continuous delivery. Wikipedia describes continuous delivery as "a software engineering approach in which teams produce software in short cycles, ensuring that the software can be reliably released at any time and, when releasing the software, doing so manually". This is a fairly common approach nowadays and supported by most major build and deployment tools. It really helps with a fast development and testing cycle and makes sure, that everything is build and tested in a common way.
Standard ways of deployments are supported out of the box by tools like Jenkins and it is straight forward to deploy to a Maven, PyPI, or npm repository.

Things become more complicated if you want to deploy and integrate data science projects. You are not done by deploying software packages to make them available as dependencies. Data science projects often consist of dependencies, libraries, and scripts. All of them need to be available in the corresponding environment.
In our case, we want to deploy pySpark scripts and schedule them via Oozie.
Our approach has some requirements and premises:
- There is a general Python environment containing all required standard packages like Numpy or Pandas. We actually build our own Cloudera based Parcel for that but you could also use the [Anaconda parcel](https://www.cloudera.com/downloads/partner/anaconda.html).
- We want to be able to deploy both libraries to be used as dependencies in other projects and scripts to be run via Oozie like our [age estimation](https://adello.github.io/Age-Targeting-Part1/).
- We want to fully versionize the deployment and also want to be able to run branch versions for testing purpoeses.
- The deployment should fully integrate with our existing Jenkins build machine.

So the whole topic has two aspects: Building and deploying via Jenkins and running the job via Oozie.

### Building and deploying

This is fairly straight forward since it is a common task. For the Python packaging we decided to go with the standard setuptools. A normal `setup.py` file looks like this:

```
#!/usr/bin/env python
from __future__ import print_function, division

from setuptools import setup

setup(
    name="ad-demographic",
    version="1.2.0",
    install_requires=["ad-pycore==1.9.0"],
    setup_requires=['nose>=1.0']
    packages=["lib"],
    author="Adello Data Science",
    author_email="datascience@adello.com",
    test_suite="test",
    py_modules=[
        "run_gender_training",
        "run_age_training",
        "generate_gender_report",
        "generate_age_report",
        "__main__"
    ]
)
```

As you can see, we depend on one internal library `ad-pycore` and nothing else, hence the general availability of common libraries. This is something we are currently re-evaluating but let's take that as a given right now. Except for that, we see that the project consists of one package `lib` and a set of scripts. An interesting bit there is the `__main__` script. We will come to that later. And yes, I know, we need to upgrade to Python 3.

We use Jenkins as build tool and for contiuous delivery we make use of Jenkinsfiles. The full file can be found [here](https://github.com/adello/adello.github.io/blob/master/_opensourced_code/_deployment_scripts/Jenkinsfile).
A quick breakdown:
```
environment {
    PYTHONPATH=".pyenv/lib/python2.7/site-packages:/opt/cloudera/parcels/SPARK2/lib/spark2/python:/opt/cloudera/parcels/SPARK2/lib/spark2/python/lib/py4j-0.10.7-src.zip:$PYTHONPATH"
    SPARK_HOME="/opt/cloudera/parcels/SPARK2/lib/spark2"
    PATH="/opt/cloudera/parcels/ad_pydeps/envs/ad_pydeps/bin:.pyenv/bin:$PATH"
    VERSION=sh(returnStdout: true, script: 'python setup.py --version').trim()
    NAME=sh(returnStdout: true, script: 'python setup.py --name').trim().replaceAll("-", "_")
    PYPIREPO = 'https://artifactory.adello.com/repository/pypi-releases/'
    HDFSLOCATION = '/user/oozie/share/lib/python_libraries/'
  }
```
We set up the environment and determine some variables like name and version. We also configure the target for deployment in pypi and hdfs.

```
stage('Install') {
      steps {
        sh 'rm -rf .pyenv'
        sh 'pip install -I --prefix=.pyenv twine nose pycodestyle'
        sh "pip install -I --prefix=.pyenv -e . --extra-index-url ${env.PYPIREPO}/simple"
        setBuildDescription()
      }
    }
```
We prepare the environment and install extra dependencies. We don't use a virtualenv here because we depend on the environment in `/opt/cloudera/parcels/ad_pydeps/envs/ad_pydeps`.

The rest should be self-explanatory. We run unit tests and static code analysis. We deploy both wheel and egg packages since pip wants wheel and Spark wants egg. We have three datacenters. Therefore we deploy to three different HDFS systems.

### Running

One of the major ideas of this deployment was for the package to be self-containing. Thus, no additional scripts or code should be necessary to start the corresponding job. That is why we are packaging the run scripts `run_age_training.py` and `generate_age_report.py` into the egg file.
But how to run those scripts now? They are part of the egg file. One possibility would be to extract them from the egg file and deploy them separately. But then the deployment needs to be aware of the strucuture of our packages. I would like to avoid this.
We could extract them as part of the execution, but that is hard to integrate with Oozie and Spark. While playing around with this, I stumbled upon the #-notation of Python packages in Oozie. The corresponding package is added with the name after the # as alias. So by adding
```
<file>${DemographicEggFile}#run_age_training.py</file>
```
to my Spark-0.2 action in Oozie, the corresponding file is added to the working directory. Why we are using the name of the script within the package as alias will be explained below.

Of course, running the corresponding script via
```
<jar>run_age_training.py</jar>
```
doesn't work. It fails with
>  can't find '\_\_main__' module in 'run_reporting.py'

This makes sense. It tries to run the whole package, just under a different name. And if Python runs a directory, it expects a `__main__.py` file within. There  are multiple ways of making a package egg-secutable [sic]. We are adding a `__main__.py` file by hand:

```
#!/usr/bin/env python
from __future__ import print_function

import sys
import os
import importlib
# This file needs to be here to make the egg file runnable from the pipeline.
# Oozie is executing this script instead of the desired script file, while the corresponding sys.argv[0] still points
# to the correct file. So we use is to dynamically import it and run the corresponding main().

script_file = sys.argv[0]
module_name = os.path.splitext(script_file)[0]

print("== Running {} with arguments {}".format(script_file, sys.argv[1:]))

module = importlib.import_module(module_name)
module.main()
```
This reads the name of executed script, imports it, and executes the main function in it. So by calling it with different names, we are able to execute different scripts within the same package, just by using different aliases.

### Conclusion

Now, to run a new version of a package, independent if it is a branch or master, we need to
- commit the code
- wait for the build and deployment
- change the version or branch in Oozie
- run

So according to the Wikipedia definition, we achieved contiuous delivery!
