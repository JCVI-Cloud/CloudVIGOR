#
# cloud-install-fabfile.py
#

#
# TODO - test validate_tests
#

import os.path, re
from fabric.api import cd, env, hide, local, run, settings, sudo, task
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
        _remove_dir(env.SCRATCH_DIR)
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

        help            - This text.
        \n"""

@task
def run_tests():
    try:
        _initialize_script()

        cmd = ("""%(VIGOR_RUNTIME_DIR)s/VIGOR.pl \
                -v 1 \
                -l %(VIGOR_RUNTIME_DIR)s/Adenovirus.pm \
                -x %(VIGOR_RUNTIME_DIR)s/conf/hadv_FJ349096.cfg \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Adenovirus/34615.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/34615 \
                > %(VIGOR_TEST_OUTPUT_DIR)s/34615.log 2>&1 \
                """) % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_RUNTIME_DIR)s/VIGOR.pl \
                -v 1 \
                -l %(VIGOR_RUNTIME_DIR)s/Coronavirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Coronavirus/GCV_35931.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/GCV_35931 \
                > %(VIGOR_TEST_OUTPUT_DIR)s/GCV_35931.log 2>&1 \
                """) % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_RUNTIME_DIR)s/VIGOR.pl \
                -v 1 \
                -l %(VIGOR_RUNTIME_DIR)s/Coronavirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Coronavirus/GCV_32276.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/GCV_32276 \
                > %(VIGOR_TEST_OUTPUT_DIR)s/GCV_32276.log 2>&1 \
                """) % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_RUNTIME_DIR)s/VIGOR.pl \
                -v 1 \
                -l %(VIGOR_RUNTIME_DIR)s/Coronavirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Coronavirus/GCV_32265.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/GCV_32265 \
                > %(VIGOR_TEST_OUTPUT_DIR)s/GCV_32265.log 2>&1 \
                """) % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_RUNTIME_DIR)s/VIGOR.pl \
                -v 1 \
                -l %(VIGOR_RUNTIME_DIR)s/Flu.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Flu/FluB.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/FluB \
                > %(VIGOR_TEST_OUTPUT_DIR)s/FluB.log 2>&1 \
                """) % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_RUNTIME_DIR)s/VIGOR.pl \
                -v 1 \
                -l %(VIGOR_RUNTIME_DIR)s/Rhinovirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Rhinovirus/Rhinovirus_genomes.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/Rhinovirus_genomes \
                > %(VIGOR_TEST_OUTPUT_DIR)s/Rhinovirus_genomes.log 2>&1 \
                """) % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_RUNTIME_DIR)s/VIGOR.pl \
                -v 1 \
                -l %(VIGOR_RUNTIME_DIR)s/Rotavirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Rotavirus/rotaV_10_22_genome.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/rotaV_10_22_genome \
                > %(VIGOR_TEST_OUTPUT_DIR)s/rotaV_10_22_genome.log 2>&1 \
                """) % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_RUNTIME_DIR)s/VIGOR.pl \
                -v 1 \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/YellowFeverV/YFV_genome.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/YFV_genome \
                > %(VIGOR_TEST_OUTPUT_DIR)s/YFV_genome.log 2>&1 \
                """) % env
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

    finally:
        disconnect_all()

# TODO - test validate_tests
@task
def validate_tests():
    try:
        _initialize_script()
        _install_tarfile(env.AMAZONS3_URL, "vigor-test-output.tgz",
                         env.VIGOR_VALIDATION_TEST_DATA_DIR)
        results = run("""diff -qr %(VIGOR_VALIDATION_TEST_DATA_DIR)s \
                      %(VIGOR_TEST_OUTPUT_DIR)s""" % env)
        if results:
            print "Validation Failed:\n%s" % results
    finally:
        disconnect_all()

def _create_scratch_dir():
    if not _path_is_dir(env.VIGOR_SCRATCH_DIR):
        sudo("mkdir -p %(VIGOR_SCRATCH_DIR)s" % env)
    sudo("chown -R %(user)s:%(user)s %(VIGOR_SCRATCH_DIR)s" % env)
    sudo("find %(VIGOR_SCRATCH_DIR)s -type d -exec chmod -R 775 {} \;" % env)

def _create_tools_dir():
    if not _path_is_dir(env.TOOLS_DIR):
        sudo("mkdir -p %(TOOLS_DIR)s" % env)
    sudo("chown -R %(user)s:%(user)s %(TOOLS_DIR)s" % env)

def _create_vigor_scratch_dir():
    if not _path_is_dir(env.VIGOR_SCRATCH_DIR):
        sudo("mkdir -p %(VIGOR_SCRATCH_DIR)s" % env)
    if not _path_is_dir(env.VIGOR_TEST_OUTPUT_DIR):
        sudo("mkdir -p %(VIGOR_TEST_OUTPUT_DIR)s" % env)
    sudo("find %(VIGOR_SCRATCH_DIR)s -type f -exec chmod -R 666 {} \;" % env)
    sudo("find %(VIGOR_SCRATCH_DIR)s -type d -exec chmod -R 777 {} \;" % env)

def _create_vigor_tempspace_dir():
    if not _path_is_dir(env.VIGOR_TEMPSPACE_DIR):
        sudo("mkdir -p %(VIGOR_TEMPSPACE_DIR)s" % env)
    sudo("chown -R %(user)s:%(user)s %(VIGOR_TEMPSPACE_DIR)s" % env)
    sudo("find %(VIGOR_TEMPSPACE_DIR)s -type d -exec chmod -R 777 {} \;" % env)

def _fix_etc_hosts():
    internal_ip = sudo("hostname")
    print("internal_ip[%s]" % internal_ip)
    filespec = "/etc/hosts"
    sudo("echo '127.0.0.1 %s' >> %s" % (internal_ip, filespec))

def _initialize_host():
    local("ssh-keygen -R %(host)s" % env)
    _fix_etc_hosts()
    _create_scratch_dir()

def _initialize_script():
    print("user[%(user)s]" % env)
    print("host[%(host)s]" % env)
    print("ROOT_DIR[%(ROOT_DIR)s]" % env)
    print("SCRATCH_DIR[%(SCRATCH_DIR)s]" % env)
    print("AMAZONS3_URL[%(AMAZONS3_URL)s]" % env)
    print("BLAST_NAME[%(BLAST_NAME)s]" % env)
    print("CLUSTALW_NAME[%(CLUSTALW_NAME)s]" % env)
    print("VIGOR_NAME[%(VIGOR_NAME)s]" % env)
    print("VIGOR_SAMPLE_DATA_TAR_FILENAME[%(VIGOR_SAMPLE_DATA_TAR_FILENAME)s]"
          % env)
    env.HOME = os.path.join("/home", env.user)

    env.TOOLS_DIR = os.path.join(env.ROOT_DIR, "tools")
    env.VIGOR_RUNTIME_DIR = os.path.join(env.TOOLS_DIR, "vigor")
    env.VIGOR_SCRATCH_DIR = os.path.join(env.SCRATCH_DIR, "vigor")
    #env.VIGOR_TEMPSPACE_DIR = "/usr/local/scratch/VIRAL/VIGOR/tempspace"
    env.VIGOR_TEMPSPACE_DIR = os.path.join(env.VIGOR_SCRATCH_DIR, "tempspace")
    env.VIGOR_SAMPLE_DATA_DIR = os.path.join(env.VIGOR_SCRATCH_DIR,
                                              "sample-data")
    env.VIGOR_TAR_FILENAME = "%(VIGOR_NAME)s.tgz" % env
    env.VIGOR_TEST_OUTPUT_DIR = os.path.join(env.VIGOR_SCRATCH_DIR,
                                              "test-output")
    env.VIGOR_VALIDATION_TEST_DATA_DIR = os.path.join(env.VIGOR_SCRATCH_DIR,
                                                      "validate-test-data")
    env.BLAST_DIR = os.path.join(env.TOOLS_DIR, "blast")
    env.CLUSTALW_DIR = os.path.join(env.TOOLS_DIR, "clustalw")
    env.EXE_DIR = "/usr/local/bin"
    env.BLAST_TAR_FILENAME = "%(BLAST_NAME)s-%(BLAST_ARCH)s.tar.gz" % env
    env.CLUSTALW_TAR_FILENAME = "%(CLUSTALW_NAME)s-%(CLUSTALW_ARCH)s.tar.gz" % env

def _install_blast():
    _create_tools_dir()
    _install_tarfile(env.AMAZONS3_URL, env.BLAST_TAR_FILENAME, env.BLAST_DIR)
    if not _path_exists(os.path.join(env.EXE_DIR, "blastall")):
        sudo("ln -s %s %s"
            % (os.path.join(env.BLAST_DIR, env.BLAST_NAME, "bin", "*"),
                env.EXE_DIR))

def _install_clustalw():
    _create_tools_dir()
    _install_tarfile(env.AMAZONS3_URL, env.CLUSTALW_TAR_FILENAME,
                     env.CLUSTALW_DIR)
    #if not _path_exists(os.path.join(env.EXE_DIR, "clustalw*")):
    if not _path_exists(os.path.join(env.EXE_DIR, "clustalw")):
        sudo("ln -s %s %s"
             % (os.path.join(env.CLUSTALW_DIR, env.CLUSTALW_NAME, "bin", "*"),
                env.EXE_DIR))
        if re.search("64", env.CLUSTALW_ARCH):
           sudo("ln -s %s %s"
                % (os.path.join(env.CLUSTALW_DIR, env.CLUSTALW_NAME, "clustalw2"),
                   os.path.join(env.EXE_DIR, "clustalw")))

def _install_tools():
    _create_tools_dir()
    _install_blast()
    _install_clustalw()

def _install_vigor():
    _create_vigor_tempspace_dir()
    _create_vigor_scratch_dir()
    _install_vigor_sample_data()
    _install_tarfile(env.AMAZONS3_URL, env.VIGOR_TAR_FILENAME,
                     env.VIGOR_RUNTIME_DIR)
    if not _path_exists(os.path.join(env.EXE_DIR, "perl")):
        sudo("ln -s %s %s" % ("/usr/bin/perl", env.EXE_DIR))

def _install_vigor_sample_data():
    _install_tarfile(env.AMAZONS3_URL, env.VIGOR_SAMPLE_DATA_TAR_FILENAME,
                 env.VIGOR_SAMPLE_DATA_DIR)
    sudo("find %(VIGOR_SAMPLE_DATA_DIR)s -type f -exec chmod -R ugo-w {} \;"
         % env)
    sudo("find %(VIGOR_SAMPLE_DATA_DIR)s -type d -exec chmod -R 555 {} \;"
         % env)

def _remove_blast():
    _remove_symlinks(os.path.join(env.BLAST_DIR, env.BLAST_NAME, "bin", "*"),
                     env.EXE_DIR)
    _remove_dir(env.BLAST_DIR)

def _remove_clustalw():
    _remove_symlinks(os.path.join(env.CLUSTALW_DIR, env.CLUSTALW_NAME, "bin", "*"),
                     env.EXE_DIR)
    _remove_dir(env.CLUSTALW_DIR)

def _remove_tools():
    _remove_blast()
    _remove_clustalw()
    _remove_dir(env.TOOLS_DIR)

def _remove_vigor():
    _remove_dir(env.VIGOR_RUNTIME_DIR)
    _remove_dir(env.VIGOR_SAMPLE_DATA_DIR)
    _remove_dir(env.VIGOR_TEMPSPACE_DIR)
    _remove_dir(env.VIGOR_TEST_OUTPUT_DIR)
    _remove_dir(env.VIGOR_VALIDATION_TEST_DATA_DIR)
    _remove_dir(env.VIGOR_SCRATCH_DIR)

# Utility methods.

def _install_tarfile(download_url, tar_filename, install_dir):
    if not _path_is_dir(install_dir):
        sudo("mkdir -p %s" % install_dir)
    with cd(install_dir):
        if not _path_exists(os.path.join(install_dir, tar_filename)):
            sudo("""wget --no-host-directories --cut-dirs=1 \
                 --directory-prefix=%s %s/%s"""
                % (install_dir, download_url, tar_filename))
            sudo("tar xvfz %s" % tar_filename)
    sudo("chown -R %s:%s %s" % (env.user, env.user, install_dir))
    sudo("find %s -type d -exec chmod -R 755 {} \;" % install_dir)

def _path_exists(path):
    found = False
    with settings(hide("running","stdout")):
        result = sudo("test -e '%s' || echo 'FALSE'" % path)
    if result != "FALSE": found = True
    return found

def _path_is_dir(path):
    found = False
    with settings(hide("running","stdout")):
        result = sudo("test -d '%s' || echo 'FALSE'" % path)
    if result != "FALSE": found = True
    return found

def _remove_dir(dirspec):
    if _path_is_dir(dirspec):
        _unlock_dir(dirspec)
        sudo("rm -rf %s" % dirspec)

def _remove_symlinks(link_from_filespec, link_to_dir):
    if _path_is_dir(link_to_dir):
        sudo("find %s -lname '%s' -delete" % (link_to_dir, link_from_filespec))

def _unlock_dir(dirspec):
    with settings(hide("running","stdout")):
        sudo("find %s -type d -exec chmod -R 755 {} \;" % dirspec)
        sudo("find %s -type d -exec chmod -R g+s {} \;" % dirspec)
        sudo("find %s -type f -exec chmod -R 644 {} \;" % dirspec)
