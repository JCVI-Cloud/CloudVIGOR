#
# cloud-install-fabfile.py
#

#
# TODO - create install_tool()
# TODO - diff remote test output files to local test output files
# TODO - finish run_tests
# TODO - finish validate_tests
# TODO - why doesn't clustalw work?
# TODO - fix timezone
#

import os.path
from fabric.api import cd, env, local, put, run, sudo, task
from fabric.network import disconnect_all

@task
def install():
    try:
        _initialize_script()
        _initialize_host()
        _install_tools()
        _install_vigor()
    finally:
        disconnect_all()

@task
def clean_all():
    try:
        _initialize_script()
        _remove_vigor()
        _remove_tools()
        if _path_exists(env.ROOT_DIR):
            run("rmdir %(ROOT_DIR)s" % env)
    finally:
        disconnect_all()

@task(default=True)
def help():
    print """
    Targets:
        install         - Initializes the VM, creates appropriate resources,
                            and installs VIGOR pipeline.

        clean_all       - Removes this VIGOR installation and all related
                            resources. (Does not return the VM to
                            pre-initialization state.)

        run_tests       - Runs tests using the VIGOR pipeline and sample data.

        validate_tests  - Compares the test output from these tests to a
                            curated copy of the test output.
        \n"""

# TODO - finish run_tests
@task
def run_tests():
    try:
        _initialize_script()

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Adenovirus.pm \
                -x %(VIGOR_REPOS_DIR)s/conf/hadv_FJ349096.cfg \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Adenovirus/34615.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/34615""") % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Coronavirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Coronavirus/GCV_35931.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/GCV_35931""") % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Coronavirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Coronavirus/GCV_32276.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/GCV_32276""") % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Coronavirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Coronavirus/GCV_32265.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/GCV_32265""") % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Flu.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Flu/FluB.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/FluB""") % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Rhinovirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Rhinovirus/Rhinovirus_genomes.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/Rhinovirus_genomes""") % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Rotavirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Rotavirus/rotaV_10_22_genome.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/rotaV_10_22_genome""") % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/YellowFeverV/YFV_genome.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/YFV_genome""") % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

    finally:
        disconnect_all()

# TODO - finish validate_tests
@task
def validate_tests():
    print "Not yet implemented."

def _create_scratch_dir():
    sudo("mkdir -p %(VIGOR_SCRATCH_DIR)s" % env)
    sudo("chown -R %(REMOTE_LINUX_USER)s:%(REMOTE_LINUX_USER)s %(VIGOR_SCRATCH_DIR)s" % env)
    sudo("find %(VIGOR_SCRATCH_DIR)s -type d -exec chmod -R 755 {} \;" % env)

def _create_tools_dir():
    sudo("mkdir -p %(TOOLS_DIR)s" % env)
    sudo("chown -R ubuntu:ubuntu %(TOOLS_DIR)s" % env)

#def _create_vigor_dir():
#    sudo("mkdir -p %s" % env.VIGOR_DIR)
#    sudo("chown -R ubuntu:ubuntu %s" % env.VIGOR_DIR)
#    #sudo("find %s -type d -exec chmod -R 755 {} \;" % env.ROOT_DIR)

def _create_vigor_scratch_dir():
    if not _path_exists(env.VIGOR_SCRATCH_DIR):
        run("mkdir -p %(VIGOR_SCRATCH_DIR)s" % env)
    if not _path_exists(env.VIGOR_TEST_OUTPUT_DIR):
        run("mkdir -p %(VIGOR_TEST_OUTPUT_DIR)s" % env)
    run("find %(VIGOR_SCRATCH_DIR)s -type f -exec chmod -R 644 {} \;" % env)
    run("find %(VIGOR_SCRATCH_DIR)s -type d -exec chmod -R 755 {} \;" % env)

def _create_vigor_tempspace_dir():
    sudo("mkdir -p %(VIGOR_TEMPSPACE_DIR)s" % env)
    sudo("chown -R %(REMOTE_LINUX_USER)s:%(REMOTE_LINUX_USER)s %(VIGOR_TEMPSPACE_DIR)s" % env)
    sudo("find %(VIGOR_TEMPSPACE_DIR)s -type d -exec chmod -R 755 {} \;" % env)

def _file_contains(filespec, phrase):
    found = False
    result = run("grep '%s' %s" % (phrase, filespec))
    if length(result) > 0: found = True
    return found

def _fix_etc_hosts():
    internal_ip = run("hostname")
    print("internal_ip[%s]" % internal_ip)
    filespec = "/etc/hosts"
    if not _file_contains(filespec, internal_ip):
        sudo("echo '127.0.0.1 %s' >> %s" % (internal_ip, filespec))

def _initialize_host():
    local("ssh-keygen -R %(host)s" % env)
    _fix_etc_hosts()
    _set_timezone()
    _update_aptget()
    #_install_build_tools()
    _create_scratch_dir()
    run("mkdir -p %s" % os.path.join(HOME, ".subversion"))
    run("rm -f %s" % os.path.join(HOME, ".subversion/config"))
    put("../upload/subversion-config", ".subversion/config", mode=0400)

def _initialize_script():
    print("User[%(user)s] (local)" % env)
    print("Host[%(host)s]" % env)
    print("Remote Linux User[%(REMOTE_LINUX_USER)s]" % env)
    print("VIGOR_REPOS_TAG[%(VIGOR_REPOS_TAG)s]" % env)
    print("ROOT_DIR[%(ROOT_DIR)s]" % env)
    print("SCRATCH_DIR[%(SCRATCH_DIR)s]" % env)
    env.HOME = os.path.join("/home", env.REMOTE_LINUX_USER)
    env.VIGOR_REPOS_DIR = os.path.join(env.ROOT_DIR, "VIGOR-REPOS")
    env.VIGOR_REPOS_URL = "%(REPOS_URL)s/%(VIGOR_REPOS_TAG)s" % env
    env.VIGOR_SCRATCH_DIR = os.path.join(env.SCRATCH_DIR, "vigor-scratch")
    env.VIGOR_TEMPSPACE_DIR = "/usr/local/scratch/VIRAL/VIGOR/tempspace"
    env.VIGOR_SAMPLE_DATA_DIR =  os.path.join(env.VIGOR_SCRATCH_DIR,
                                              "sample-data")
    env.VIGOR_TEST_OUTPUT_DIR =  os.path.join(env.VIGOR_SCRATCH_DIR,
                                              "test-output")
    env.VIGOR_SAMPLE_DATA_URL = ("%(AMAZONS3_URL)/%(VIGOR_SAMPLE_DATA_TAR_FILENAME)s" % env)
    env.TOOLS_DIR = os.path.join(env.ROOT_DIR, "tools")
    env.BLAST_DIR = os.path.join(env.TOOLS_DIR, "blast")
    env.CLUSTALW_DIR = os.path.join(env.TOOLS_DIR, "clustalw")
    env.EXE_DIR = "/usr/local/bin"
    #env.VIGOR_DIR = os.path.join(env.ROOT_DIR, "devel/ANNOTATION/VIRAL/VIGOR")
    env.BLAST_TAR_FILENAME = "%(BLAST_NAME)s-x64-linux.tar.gz" % env
    env.BLAST_URL = ("%(AMAZONS3_URL)s/%(BLAST_TAR_FILENAME)s" % env)
    env.CLUSTALW_TAR_FILENAME = "%(CLUSTALW_NAME)s.tgz" % env
    env.CLUSTALW_URL = ("%(AMAZONS3_URL)s/%(CLUSTALW_TAR_FILENAME)s" % env)

def _install_blast():
    sudo("mkdir -p %(BLAST_DIR)s" % env)
    sudo("chown ubuntu:ubuntu %(BLAST_DIR)s" % env)
    with cd(env.BLAST_DIR):
        sudo("""wget --no-host-directories --cut-dirs=1 \
              --directory-prefix=%(BLAST_DIR)s %(BLAST_URL)s""" % env)
        sudo("tar xvfz %(BLAST_TAR_FILENAME)s" % env)
    sudo("find %(BLAST_DIR)s -type d -exec chmod -R 755 {} \;" % env)
    sudo("ln -s %s/bin/* %s"
         % (os.path.join(env.BLAST_DIR, env.BLAST_NAME), env.EXE_DIR))

def _install_clustalw():
    sudo("mkdir -p %(CLUSTALW_DIR)s" % env)
    sudo("chown ubuntu:ubuntu %(CLUSTALW_DIR)s" % env)
    with cd(env.CLUSTALW_DIR):
        sudo("""wget --no-host-directories --cut-dirs=1 \
              --directory-prefix=%(CLUSTALW_DIR)s %(CLUSTALW_URL)s""" % env)
        sudo("tar xvfz %(CLUSTALW_TAR_FILENAME)s" % env)
    sudo("find %(CLUSTALW_DIR)s -type d -exec chmod -R 755 {} \;" % env)
    sudo("ln -s %s/bin/* %s"
         % (os.path.join(env.CLUSTALW_DIR, env.CLUSTALW_NAME), env.EXE_DIR))

#def _install_build_tools():
#    sudo("apt-get -y install gcc")
#    sudo("apt-get -y install g++")
#    sudo("apt-get -y install make")

def _install_subversion():
    sudo("apt-get -y install subversion")

def _install_tools():
    _create_tools_dir()
    _install_blast()
    _install_clustalw()
    _install_subversion()

#def _install_vigor():
#    _create_vigor_dir()
#    #_create_reference_db_dir()
#    sudo("chown -R root:root %s" % env.TOOLS_DIR)
#    sudo("find %s -type d -exec chmod -R 755 {} \;" % env.ROOT_DIR)
#    with cd(env.VIGOR_DIR):
#        #run("svn --username=tprindle checkout http://svn.jcvi.org/ANNOTATION/vigor/new .")
#        run("svn --username=%s export %s ." % ( env.user, env.VIGOR_REPOS_URL))
def _install_vigor():
    _create_vigor_tempspace_dir()
    _create_vigor_scratch_dir()
    _install_vigor_sample_data()
    if not _path_exists(env.VIGOR_REPOS_DIR):
        run("svn --username=%(user)s export %(VIGOR_REPOS_URL)s %(VIGOR_REPOS_DIR)s" % env)
    run("find %(VIGOR_REPOS_DIR)s -type f -exec chmod -R ugo-w {} \;" % env)
    run("find %(VIGOR_REPOS_DIR)s -type d -exec chmod -R 555 {} \;" % env)

def _install_vigor_sample_data():
    if not _path_exists(env.VIGOR_SAMPLE_DATA_DIR):
        run("mkdir -p %(VIGOR_SAMPLE_DATA_DIR)s" % env)
    if not _path_exists("%(VIGOR_SAMPLE_DATA_DIR)s/%(VIGOR_SAMPLE_DATA_TAR_FILENAME)s" % env):
        run(("""wget --no-host-directories --cut-dirs=1 \
            --directory-prefix=%(VIGOR_SAMPLE_DATA_DIR)s \
             %(VIGOR_SAMPLE_DATA_URL)s""") % env)
    with cd(env.VIGOR_SAMPLE_DATA_DIR):
        run("tar xvfz %(VIGOR_SAMPLE_DATA_TAR_FILENAME)s" % env)
    run("find %(VIGOR_SAMPLE_DATA_DIR)s -type f -exec chmod -R ugo-w {} \;" % env)
    run("find %(VIGOR_SAMPLE_DATA_DIR)s -type d -exec chmod -R 555 {} \;" % env)

def _path_exists(path):
    found = False
    result = run("if [ -e %s ]; then echo 'true'; else echo 'false'; fi" % path)
    if result == "true": found = True
    return found

def _path_is_dir(path):
    found = False
    result = run("if [ -d %s ]; then echo 'true'; else echo 'false'; fi" % path)
    if result == "true": found = True
    return found

def _remove_blast():
    #sudo("find %(EXE_DIR)s -lname %(BLAST_DIR)s -delete" % env)
    _remove_symlinks(env.BLAST_DIR, env.EXE_DIR)
    _remove_dir(env.BLAST_DIR)

def _remove_clustalw():
    #sudo("find %(EXE_DIR)s -lname %(CLUSTALW_DIR)s -delete" % env)
    _remove_symlinks(env.CLUSTALW_DIR, env.EXE_DIR)
    _remove_dir(env.CLUSTALW_DIR)

def _remove_dir(dirspec):
    if _path_is_dir(dirspec):
        run("find %s -type d -exec chmod -R 755 {} \;" % dirspec)
        run("find %s -type f -exec chmod -R 644 {} \;" % dirspec)
        run("rm -rf %s" % dirspec)

def _remove_symlinks(link_from_dir, link_to_dir):
    if _path_is_dir(link_from_dir) and _path_is_dir(link_to_dir):
        sudo("find %s -lname %s -delete" % (link_to_dir,link_from_dir))

def _remove_tools():
    _remove_blast()
    _remove_clustalw()
    _remove_dir(env.TOOLS_DIR)

def _remove_vigor():
    _remove_dir(env.VIGOR_REPOS_DIR)
    _remove_dir(env.VIGOR_SAMPLE_DATA_DIR)
    _remove_dir(env.VIGOR_TEMPSPACE_DIR)
    _remove_dir(env.VIGOR_SCRATCH_DIR)

# TODO - create install_tool()

# TODO - fix timezone
def _set_timezone():
    #sudo("dpkg-reconfigure tzdata")
    pass

def _update_aptget():
    sudo("apt-get -y update")
