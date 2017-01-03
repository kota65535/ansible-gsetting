#!/usr/bin/python

import json
import re
import subprocess
import q

from ansible.module_utils.basic import *

def _decode_value(value):
    '''Decode value to python object.
    * list: convert from str to list object
    * tuple: convert from str to tuple object
    * str: strip single quotes
    * int, float, bool: eval fails, so does nothing
    '''
    try:
        value = eval(value)
    except Exception:
        pass
    return value

def _encode_value(value):
    '''Encord value from python object.
    * str:  add single quotes
    * list, int, float, bool: convert to str
    '''
    if   isinstance(value, (list, tuple)):
        value = "{0}".format(str(value))
    elif isinstance(value, str):
        value = "'{0}'".format(value)
    elif isinstance(value, bool):
        value = 'true' if value else 'false'
    elif isinstance(value, (int, float)):
        value = str(value)
    return value

def _append_value(target, value):
    '''append value to target if the value does not exists'''
    ret = _decode_value(target)
    if not isinstance(ret, list):
        ret = [ret]

    if value not in ret:
        ret.append(value)
    return ret

def _remove_value(target, value):
    '''remove value from target if the value exists'''
    ret = _decode_value(target)
    if not isinstance(ret, list):
        return target

    if value in ret:
        ret.remove(value)
    return ret

def _escape_single_quotes(string):
    return re.sub("'", r"'\''", string)

def _set_value(user, schema, key, value):

    command = " ".join([
        'export `/usr/bin/dbus-launch`',
        ';',
        '/usr/bin/gsettings set', schema, key,
        "'%s'" % _escape_single_quotes(value),
        ';',
        'kill $DBUS_SESSION_BUS_PID &> /dev/null'
    ])

    return subprocess.check_output([
        'sudo', '-u', user , 'sh', '-c', command
    ]).strip()

def _get_value(user, schema, key):

    command = " ".join([
        'export `/usr/bin/dbus-launch`',
        ';',
        '/usr/bin/gsettings get', schema, key,
        ';',
        'kill $DBUS_SESSION_BUS_PID &> /dev/null'
    ])

    q(command)
    return subprocess.check_output([
        'sudo', '-u', user , 'sh', '-c', command
    ]).strip()

def main():

    module = AnsibleModule(
        argument_spec = {
            'state': { 'choices': ['present', 'append', 'absent'], 'default': 'present' },
            'user': { 'required': True },
            'schema': { 'required': True },
            'key': { 'required': True },
            'value': { 'required': True },
        },
        supports_check_mode = True,
    )

    params = module.params
    state = module.params['state']
    user = module.params['user']
    schema = module.params['schema']
    key = module.params['key']
    value = module.params['value']

    old_value = _get_value(user, schema, key)
    q(old_value)

    value = _decode_value(value)

    if state == 'append':
        value = _append_value(old_value, value)
    elif state == 'absent':
        value = _remove_value(old_value, value)

    value =_encode_value(value)
    q(value)

    changed = old_value != value

    if changed and not module.check_mode:
        _set_value(user, schema, key, value)

    print json.dumps({
        'changed': changed,
        'key': key,
        'value': value,
        'old_value': old_value,
    })

main()
