#!/usr/bin/env python3
import json
from os import path, access, X_OK
from sys import argv
from plumbum import local as sh

src_dir, output_dir = argv[1:]
MASTER = 'index'

class View(object):

    def __init__(self, name, dir=None):
        self.name = name
        self.dir = dir or src_dir

    def key(self):
        return '__{}.html__'.format(self.name)

    def view(self):
        view_path = '{}/{}.html'.format(self.dir, self.name)
        print('[{}] view_path: {}'.format(self.name, view_path))
        return view_path

    def child_dir(self):
        child_dir_path = path.join(self.dir, self.name)
        if path.isdir(child_dir_path):
            return child_dir_path

    def child_script(self):
        child_script_path = path.join(self.dir, '{}.py'.format(self.name))
        if path.isfile(child_script_path) and access(child_script_path, X_OK):
            return child_script_path
        else:
            print('{} is not an executable script'.format(child_script_path))

    def load(self):
        with open(self.view(), 'r') as fd:
            return fd.read()

    def render_script(self, content, script):
        print('Rendering view using script')
        try:
            cmd = sh['python3'][script][output_dir]
            print('render cmd: "{}"'.format(cmd))
            result = json.loads(cmd().strip())
            for key in result:
                print('child_key: {}'.format(key))
                content = content.replace("__{}__".format(key), result[key])
            return content
        except Exception as ex:
            print('Failed to render view from script. \n{}'.format(ex))

    def render_static_content(self, content, children):
        for child in children:
            print('child_key: {}'.format(child.key()))
            content = content.replace(child.key(), child.render())
        return content

    def render(self):
        content = self.load()
        script = self.child_script()
        if script:
            result = self.render_script(content, script)
            if result:
                return result
        else:
            print('No script found')
        # If the rendering failed, fall back to just using static content.
        children = self.child_views()
        return self.render_static_content(content, children)

    def find_children(self):
        child_dir = self.child_dir()
        if child_dir:
            return sh['find'][child_dir]['-maxdepth']['1']['-type']['f']().strip().split()
        return []

    def child_views(self):
        child_views = []
        for child in self.find_children():
            file_name = child.split('/')[-1:][0]
            name = file_name
            if name.endswith('.html'):
                name = name.replace('.html', '')
            dir = self.child_dir()
            child_views.append(View(name, dir))
        return child_views


def main():
    master = View(MASTER)
    output = master.render()
    output_path = '{}/{}.html'.format(output_dir, MASTER)
    print('output_path: ' + output_path)
    with open(output_path, 'w') as fd:
        fd.write(output)
    print('Wrote {} bytes'.format(len(output)))

if __name__ == "__main__":
    main()
