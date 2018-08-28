import logging
import subprocess


def send_mail(subject, address, body):
    cmd = ['mail', '-s', subject, address]
    logging.debug("Sending email with: {}".format(cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    p.stdin.write(body)
    p.stdin.close()
    if p.wait() != 0:
        logging.error("Failed to send alert email with header {} and body text {}".format(subject, body))
    else:
        logging.debug("Email send with header {} and body text {}".format(subject, body))


def send_deployment_mail(dc, lib_names, lib_vers, address, branch="master"):
    if branch == "master":
        body = "This mail is to notify you that the following artifacts have been deployed to {}:" \
               "".format(dc)
    else:
        body = "This mail is to notify you that branch {} of the following artifacts have been deployed to {}:" \
               "".format(branch, dc)

    artifacts = ""
    libs = ""
    for (lib_name, lib_ver) in zip(lib_names, lib_vers):
        artifacts = artifacts + "\n - {} ({})\n".format(lib_name, lib_ver)
        libs = libs + "{} ".format(lib_name)

    subject = "{} deployed in {}".format(libs, dc)
    body = body + artifacts
    send_mail(subject, address, body)
