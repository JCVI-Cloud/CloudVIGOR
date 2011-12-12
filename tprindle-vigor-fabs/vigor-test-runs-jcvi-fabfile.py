#
# vigor-test-runs-jcvi-fabfile.py
#

import os.path
from fabric.api import cd, env, prefix, run, task
from fabric.network import disconnect_all

@task
def install():
    try:
        _initialize()
        # TODO - if dir exists, cancel install. which dir?
        _create_vigor_scratch_dir()
        _install_vigor()
        _install_vigor_sample_data()
    finally:
        disconnect_all()

@task
def clean_all():
    try:
        _initialize()
        _remove_vigor_repos_dir()
        _remove_vigor_scratch_dir()
        #if _path_exists(env.ROOT_DIR):
        #    run("rmdir %(ROOT_DIR)s" % env)
    finally:
        disconnect_all()

@task(default=True)
def help():
    print """
    Targets:
        install   - Creates appropriate resources and installs VIGOR pipeline.

        clean_all - Removes this VIGOR installation and all related resources.

        run_tests - Runs tests using the VIGOR pipeline and sample data.
        \n"""

@task
def run_tests():
    try:
        _initialize()

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

def _create_vigor_scratch_dir():
    if not _path_exists(env.VIGOR_SCRATCH_DIR):
        run("mkdir -p %(VIGOR_SCRATCH_DIR)s" % env)
    #if not _path_exists(env.VIGOR_TEMPSPACE_DIR):
    #    run("mkdir -p %(VIGOR_TEMPSPACE_DIR)s" % env)
    if not _path_exists(env.VIGOR_TEST_OUTPUT_DIR):
        run("mkdir -p %(VIGOR_TEST_OUTPUT_DIR)s" % env)
    run("find %(VIGOR_SCRATCH_DIR)s -type f -exec chmod -R 644 {} \;" % env)
    run("find %(VIGOR_SCRATCH_DIR)s -type d -exec chmod -R 755 {} \;" % env)

def _initialize():
    print("User[%s]" % env.user)
    print("Host[%s]" % env.host)
    print("VIGOR_SVN_TAG[%s]" % env.VIGOR_SVN_TAG)
    print("ROOT_DIR[%s]" % env.ROOT_DIR)
    print("SCRATCH_DIR[%s]" % env.SCRATCH_DIR)
    env.GROUP = "tigr"
    env.VIGOR_SCRATCH_DIR = os.path.join(env.SCRATCH_DIR, "vigor-scratch")
    env.VIGOR_SAMPLE_DATA_TAR_FILENAME = "vigor-sample-data.tgz"
    env.VIGOR_TEMPSPACE_DIR = "/usr/local/scratch/VIRAL/VIGOR/tempspace"
    env.VIGOR_REPOS_DIR = os.path.join(env.ROOT_DIR, "VIGOR-REPOS")
    env.SVN_URL = ("http://svn.jcvi.org/ANNOTATION/vigor/tags/%s"
                   % env.VIGOR_SVN_TAG)
    env.VIGOR_SAMPLE_DATA_URL = ("https://s3.amazonaws.com/VIGOR/%s"
                                 % env.VIGOR_SAMPLE_DATA_TAR_FILENAME)
    env.VIGOR_SAMPLE_DATA_DIR =  os.path.join(env.VIGOR_SCRATCH_DIR,
                                              "sample-data")
    env.VIGOR_TEST_OUTPUT_DIR =  os.path.join(env.VIGOR_SCRATCH_DIR,
                                              "test-output")

def _install_vigor():
    if not _path_exists(env.VIGOR_REPOS_DIR):
        run("svn --username=%(user)s export %(SVN_URL)s %(VIGOR_REPOS_DIR)s"
            % env)
    run("find %(VIGOR_REPOS_DIR)s -type f -exec chmod -R ugo-w {} \;" % env)
    run("find %(VIGOR_REPOS_DIR)s -type d -exec chmod -R 555 {} \;" % env)

def _install_vigor_sample_data():
    if not _path_exists(env.VIGOR_SAMPLE_DATA_DIR):
        run("mkdir -p %(VIGOR_SAMPLE_DATA_DIR)s" % env)
    if not _path_exists("%(VIGOR_SAMPLE_DATA_DIR)s/%(VIGOR_SAMPLE_DATA_TAR_FILENAME)s"
                   % env):
        run(("""wget --no-host-directories --cut-dirs=1 \
            --directory-prefix=%(VIGOR_SAMPLE_DATA_DIR)s \
             %(VIGOR_SAMPLE_DATA_URL)s""") % env)
    with cd(env.VIGOR_SAMPLE_DATA_DIR):
        run("tar xvfz %(VIGOR_SAMPLE_DATA_TAR_FILENAME)s" % env)
    run("find %(VIGOR_SAMPLE_DATA_DIR)s -type f -exec chmod -R ugo-w {} \;" % env)
    run("find %(VIGOR_SAMPLE_DATA_DIR)s -type d -exec chmod -R 555 {} \;" % env)

def _path_exists(path):
    found = False
    result = run("if [ -e %s ]; then echo 'true'; else echo 'false'; fi" % path )
    if result == "true": found = True
    return found

def _remove_vigor_repos_dir():
    # with prefix doesn't work in this case.
    if _path_exists(env.VIGOR_REPOS_DIR):
        run("find %(VIGOR_REPOS_DIR)s -type d -exec chmod -R 755 {} \;" % env)
        run("find %(VIGOR_REPOS_DIR)s -type f -exec chmod -R 644 {} \;" % env)
        run("rm -rf %(VIGOR_REPOS_DIR)s" % env)

def _remove_vigor_scratch_dir():
    # with prefix doesn't work in this case.
    if _path_exists(env.VIGOR_SCRATCH_DIR):
        run("find %(VIGOR_SCRATCH_DIR)s -type d -exec chmod -R 755 {} \;" % env)
        run("find %(VIGOR_SCRATCH_DIR)s -type f -exec chmod -R 644 {} \;" % env)
        run("rm -rf %(VIGOR_SCRATCH_DIR)s" % env)
