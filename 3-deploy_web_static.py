#!/usr/bin/python3
"""a script to pack static content into a tarball
"""
from fabric.api import *
from fabric.operations import put
from datetime import datetime
import os

env.hosts = ['107.22.142.201', '35.153.57.148']




def do_pack():
    """packages all contents from web_static into .tgz archive
    """
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    local('mkdir -p versions')
    filename = 'versions/web_static_{}.tgz'.format(now)
    result = local('tar -cvzf {} web_static'
                   .format(filename), capture=True)
    if result.failed:
        print('Failed to create tar package')
        return None
    else:
        return filename


def do_deploy(archive_path):
    """deploys a static archive to web servers
    """
    if not os.path.isfile(archive_path):
        print('archive file does not exist...')
        return False
    try:
        archive = archive_path.split('/')[1]
        no_ext_archive = archive.split('.')[0]
    except:
        print('failed to get archive name from split...')
        return False
    uploaded = put(archive_path, '/tmp/')
    if uploaded.failed:
        return False
    res = run('mkdir -p /data/web_static/releases/{}/'.format(no_ext_archive))
    if res.failed:
        print('failed to create archive directory for relase...')
        return False
    res = run('tar -C /data/web_static/releases/{} -xzf /tmp/{}'.format(
               no_ext_archive, archive))
    if res.failed:
        print('failed to untar archive...')
        return False
    res = run('rm /tmp/{}'.format(archive))
    if res.failed:
        print('failed to remove archive...')
        return False
    res = run('mv /data/web_static/releases/{}/web_static/* \
               /data/web_static/releases/{}'
              .format(no_ext_archive, no_ext_archive))
    if res.failed:
        print('failed to move extraction to proper directory...')
        return False
    res = run('rm -rf /data/web_static/releases/{}/web_static'
              .format(no_ext_archive))
    if res.failed:
        print('failed to remove first copy of extraction after move...')
        return False
    # clean up old release and remove it
    res = run('rm -rf /data/web_static/current')
    if res.failed:
        print('failed to clean up old release...')
        return False
    res = run('ln -sfn /data/web_static/releases/{} /data/web_static/current'
              .format(no_ext_archive))
    if res.failed:
        print('failed to create link to new release...')
        return False

    print('\nNew Version Successfuly Deployed!\n')

    return True


def deploy():
    """deploy executes do_pack and do_deploy to deploy the latest
        changes to the server list
    """
    ar_path = do_pack()
    print(ar_path)
    if ar_path is None:
        print('Failed to create archive from web_static')
        return False
    return do_deploy(ar_path)
