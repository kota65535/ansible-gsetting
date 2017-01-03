import pytest
import subprocess
import os

def test_set_int():
    schema = 'org.gnome.system.proxy.https'
    key = 'port'
    value = 0
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'gsetting',
        '-a', 'user={0} schema={1} key={2} value={3}'.format(os.environ['USER'], schema, key, value),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0
    output = subprocess.check_output([
        'gsettings', 'get', schema, key
    ]).strip()
    assert output == str(value)

def test_set_str():
    schema = 'org.gnome.system.proxy.https'
    key = 'host'
    value = 'aaa@example.com'
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'gsetting',
        '-a', 'user={0} schema={1} key={2} value={3}'.format(os.environ['USER'], schema, key, value),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0
    output = subprocess.check_output([
        'gsettings', 'get', schema, key
    ]).strip()
    assert output == "'{0}'".format(value)

def test_set_list_int():
    schema = 'org.mate.system-monitor.disktreenew'
    key = 'columns-order'
    value = "[1, 2, 3]"
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'gsetting',
        '-a', 'user={0} schema={1} key={2} value="{3}"'.format(os.environ['USER'], schema, key, value),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0
    output = subprocess.check_output([
        'gsettings', 'get', schema, key
    ]).strip()
    assert output == value

def test_set_list_str():
    schema = 'org.mate.panel'
    key = 'object-id-list'
    value = "['piyo', 'fuga']"
    added = 'moge'
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'gsetting',
        '-a', 'user={0} schema={1} key={2} value="{3}"'.format(os.environ['USER'], schema, key, value),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0
    output = subprocess.check_output([
        'gsettings', 'get', schema, key
    ]).strip()
    assert output == value

def test_append_list_str():
    schema = 'org.mate.panel'
    key = 'object-id-list'
    value = ['piyo', 'fuga']
    added = 'moge'

    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'gsetting',
        '-a', 'user={0} schema={1} key={2} value="{3}"'.format(os.environ['USER'], schema, key, value),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0

    # If added value exists in the list, append fails.
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'gsetting',
        '-a', 'user={0} schema={1} key={2} value={3} state=append'.format(os.environ['USER'], schema, key, value[0]),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0
    output = subprocess.check_output([
        'gsettings', 'get', schema, key
    ]).strip()
    assert output == str(value)

    # Normal case
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'gsetting',
        '-a', 'user={0} schema={1} key={2} value={3} state=append'.format(os.environ['USER'], schema, key, added),
        '-i', 'localhost,',
        '-c', 'local'
    ])

    assert status == 0
    output = subprocess.check_output([
        'gsettings', 'get', schema, key
    ]).strip()
    assert output == str(value + [added])


def test_remove_list_str():
    schema = 'org.mate.panel'
    key = 'object-id-list'
    value = ['piyo', 'fuga']
    removed = 'fuga'
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'gsetting',
        '-a', 'user={0} schema={1} key={2} value="{3}"'.format(os.environ['USER'], schema, key, value),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0

    # If removed value exists in the list, remove fails.
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'gsetting',
        '-a', 'user={0} schema={1} key={2} value={3} state=absent'.format(os.environ['USER'], schema, key, 'moge'),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0
    output = subprocess.check_output([
        'gsettings', 'get', schema, key
    ]).strip()
    assert output == str(value)

    # Normal case
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'gsetting',
        '-a', 'user={0} schema={1} key={2} value={3} state=absent'.format(os.environ['USER'], schema, key, removed),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0
    output = subprocess.check_output([
        'gsettings', 'get', schema, key
    ]).strip()
    value.remove(removed)
    assert output == str(value)

