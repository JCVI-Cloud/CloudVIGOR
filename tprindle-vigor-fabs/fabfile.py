#
# fabfile.py
# 20111005 tprindle
#

#
# TODO - why doesn't clustalw work?
#

import os.path

USER = "ubuntu"
HOME = os.path.join("/home", USER)

SCRATCH_DIR = "/usr/local/scratch"
VIGOR_SCRATCH_DIR = os.path.join(SCRATCH_DIR, "VIRAL/VIGOR")
TEMPSPACE_DIR = os.path.join(VIGOR_SCRATCH_DIR, "tempspace")

ROOT_DIR = "/usr/local"
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
VIGOR_DIR = os.path.join(ROOT_DIR, "devel/ANNOTATION/VIRAL/VIGOR")

#BUILD_DIR = os.path.join(HOME, "_BUILD")
EXE_DIR = "/usr/local/bin"

AMAZONS3_URL = "https://s3.amazonaws.com/VIGOR"

CLUSTALW_NAME = "clustalw-1.83"
CLUSTALW_TAR_FILENAME = "%s.tgz" % CLUSTALW_NAME
CLUSTALW_URL = os.path.join(AMAZONS3_URL, CLUSTALW_TAR_FILENAME)
CLUSTALW_DIR = os.path.join(TOOLS_DIR, "clustalw")

BLAST_NAME = "blast-2.2.15"
BLAST_TAR_FILENAME = "%s-x64-linux.tar.gz" % BLAST_NAME
BLAST_URL = os.path.join("%s/%s" % (AMAZONS3_URL, BLAST_TAR_FILENAME))
BLAST_DIR = os.path.join(TOOLS_DIR, "blast")

VIGOR_SVN_TAG = "GSCcloud-release-20111129"
SVN_USER = "tprindle"
SVN_URL = "http://svn.jcvi.org/ANNOTATION/vigor/tags/%s" % VIGOR_SVN_TAG

CONFIG =

####

import urllib
from fabric.api import cd, env, local, put, run, sudo, task
from fabric.network import disconnect_all

@task(default=True)
def install():
    try:
        _initialize()
        _install_vigor()
    finally:
        disconnect_all()

def _initialize():
    env.user = USER
    print("User[%s]" % env.user)
    print("Host[%s]" % env.host)
    result = local("ssh-keygen -R %s" % env.host)
    result = run("mkdir -p %s" % os.path.join(HOME, ".subversion"))
    result = run("rm -f %s" % os.path.join(HOME, ".subversion/config"))
    result = put("../upload/subversion-config", ".subversion/config", mode=0400)
    _fix_etc_hosts()
    #_set_timezone()
    _update_aptget()
    #_install_build_tools()

def _install_vigor():
    _create_tools_dir()
    _install_blast()
    _install_clustalw()
    _install_subversion()
    _create_scratch_dir()
    _create_vigor_dir()
    #_create_reference_db_dir()
    result = sudo("chown -R root:root %s" % TOOLS_DIR)
    result = sudo("find %s -type d -exec chmod -R 755 {} \;" % ROOT_DIR)
    with cd(VIGOR_DIR):
        #result = run("svn --username=tprindle checkout http://svn.jcvi.org/ANNOTATION/vigor/new .")
        result = run("svn --username=%s export %s ." % ( SVN_USER, SVN_URL))

def _create_scratch_dir():
    result = sudo("mkdir -p %s" % TEMPSPACE_DIR)
    result = sudo("chown -R %s:%s %s" % (USER, USER, VIGOR_SCRATCH_DIR))
    result = sudo("find %s -type d -exec chmod -R 755 {} \;" % VIGOR_SCRATCH_DIR)

def _create_tools_dir():
    result = sudo("mkdir -p %s" % TOOLS_DIR)
    result = sudo("chown -R ubuntu:ubuntu %s" % TOOLS_DIR)
    #result = sudo("find %s -type d -exec chmod -R 755 {} \;" % ROOT_DIR)

def _create_vigor_dir():
    result = sudo("mkdir -p %s" % VIGOR_DIR)
    result = sudo("chown -R ubuntu:ubuntu %s" % VIGOR_DIR)
    #result = sudo("find %s -type d -exec chmod -R 755 {} \;" % ROOT_DIR)

def _exists(filespec):
    with settings(warn_only=True):
        return run("test -e %s" % filespec)

def _fix_etc_hosts():
    internal_ip = run("hostname")
    print("internal_ip[%s]" % internal_ip)
    result = sudo("echo '' >> /etc/hosts")
    result = sudo("echo '127.0.0.1 %s' >> /etc/hosts" % internal_ip)
    #result = sudo("echo '%s %s' >> /etc/hosts" % (env.host, internal_ip))
    result = sudo("echo '' >> /etc/hosts")

def _install_blast():
    # TODO - ftp://ftp.ncbi.nlm.nih.gov/blast/executables/release/2.2.15/
    #result = sudo("apt-get -y install blast2")
    result = sudo("mkdir -p %s" % BLAST_DIR)
    result = sudo("chown ubuntu:ubuntu %s" % BLAST_DIR)
    with cd(BLAST_DIR):
        result = sudo(("wget --no-host-directories --cut-dirs=1 "
                      + "--directory-prefix=%s %s")
                      % (BLAST_DIR, BLAST_URL))
        result = sudo("tar xvfz %s" % BLAST_TAR_FILENAME)
    result = sudo("find %s -type d -exec chmod -R 755 {} \;" % BLAST_DIR)
    result = sudo("ln -s %s/bin/* %s"
                  % (os.path.join(BLAST_DIR, BLAST_NAME), EXE_DIR))

def _install_clustalw():
    #build_dir = os.path.join(BUILD_DIR, "clustalw")
    #result = run("mkdir -p %s" % build_dir)
    #with cd(build_dir):
    #    run("wget ftp://ftp.ebi.ac.uk/pub/software/clustalw2/2.0.10/clustalw-2.0.10-src.tar.gz")
    #    run("tar xvfz clustalw-2.0.10-src.tar.gz")
    #    with cd("clustalw-2.0.10"):
    #        run("./configure")
    #        run("make")
    #        sudo("make install")
    result = sudo("mkdir -p %s" % CLUSTALW_DIR)
    result = sudo("chown ubuntu:ubuntu %s" % CLUSTALW_DIR)
    with cd(CLUSTALW_DIR):
        result = sudo(("wget --no-host-directories --cut-dirs=1 "
                      + "--directory-prefix=%s %s")
                      % (CLUSTALW_DIR, CLUSTALW_URL))
        result = sudo("tar xvfz %s" % CLUSTALW_TAR_FILENAME)
    result = sudo("find %s -type d -exec chmod -R 755 {} \;" % CLUSTALW_DIR)
    result = sudo("ln -s %s/bin/clustalw %s"
                  % (os.path.join(CLUSTALW_DIR, CLUSTALW_NAME), EXE_DIR))

#def _install_build_tools():
#    result = sudo("apt-get -y install gcc")
#    result = sudo("apt-get -y install g++")
#    result = sudo("apt-get -y install make")

def _install_subversion():
    result = sudo("apt-get -y install subversion")

def _set_timezone():
    #result = sudo("dpkg-reconfigure tzdata")
    pass

def _update_aptget():
    result = sudo("apt-get -y update")
