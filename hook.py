# use UTP-8 #
"""
    This script is to run a backend service to
    handle http requests ( GET and POST ) from
    Gitlab server.
"""

__author__ = "Xu Fangzhou"
__email__ = "kevin.xu.fangzhou@gmail.com"

import web
import os
import run
import json
import re
import sys
import threading as thd
from time import asctime

urls = (
        '/', 'index'
        )

block = {}
lock = thd.RLock()

class index:
    def GET(self):
        return "This is LSEMS."
    def POST(self):
        global block
        data = json.loads(web.data())
        name = data['user_name']
        flag = False

        no_run = False
        for commit in data['commits']:
            if "no run" in commit['message']:
                no_run = True
        if no_run:
            return "Done."

        os.system("python exp.py -i '%s' &" %json.dumps(data))

        return "Done."

    # not in use, moved to exp.py
    def exp(self, data):
        print data
        repo_url = data['repository']['url']
        repo_name = re.split('/', data['repository']['homepage'])[-1:][0]
        print "current dir: "+os.getcwd()
        os.chdir('repos')
        if repo_name in os.listdir('.'):
            print("found repo existing.")
            os.system("rm -r -f "+repo_name)
            print("deleted.")
        os.system("git clone "+repo_url)
        os.chdir(repo_name)
        file_names = os.listdir('.')
        try:
            if 'exp.json' not in file_names:
                raise Exception("Cannot find file exp.json!\nAborting...")
            run.read('exp.json',
                {"commit_id": data['commits'][0]['id'],
                'repo_name': data['repository']['name'],
                'name': data['user_name'] },)
        except Exception as e:
            print e.message
        os.chdir('../..')

class MyApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

if __name__ == "__main__":
    app = MyApplication(urls, globals())
    # config = json.load(open(os.environ.get("HOME") + '/sandbox/config.json'))
    config = json.load(open("config.json"))
    app.run(port = config['hook_port'])
