#!/usr/bin/env python
#-- coding:UTF-8 --
import json
import re
# spec协议转换


def paresJson(fileName):
    f = open(fileName, mode='r')
    data = json.load(f)
    services = data['services']
    protocal = {
        'prop': {},
        'action': {},
        'event': {},
    }
    consts = {
        'prop': {},
        'action': {},
        'event': {},
    }
    for service in services:
        iid = service['iid']
        if 'properties' in service:
            props = service['properties']
            ps = parseProps(props, iid)
            protocal['prop'].update(ps['names'])
            protocal['prop'].update(ps['ids'])
            consts['prop'].update(ps['consts'])
        if 'actions' in service:
            actions = service['actions']
            acs = parseAction(actions, iid)
            protocal['action'].update(ps['names'])
            consts['action'].update(ps['consts'])
        if 'events' in service:
            events = service['events']
            ps = parseEvents(events, iid)
            protocal['event'].update(ps['names'])
            protocal['event'].update(ps['ids'])
            consts['event'].update(ps['consts'])
    return {'protocal': protocal, 'const': consts}


# abc-edf -> abcEdf 短横线命名转换为驼峰式命名
def parseName(nameStr):
    names = nameStr.split('-')
    if len(names) <= 1:
        return nameStr
    else:
        ns = list(map(lambda name: name.capitalize(), names[1:]))
        ns.insert(0, names[0])
        return ''.join(ns)


def parseAction(actions, sid):
    names = {}
    consts = {}
    for action in actions:
        iid = action['iid']
        t = action['type']
        obj = re.search(r':action:(.*?):', t)
        oname = obj.group(1)
        name = parseName(oname)
        cname = oname.upper().replace('-', '_')
        # name -> id
        names[name] = {'siid': sid, 'aiid': iid}
        consts[cname] = name
    return {"names": names, "consts": consts}


def parseProps(props, sid):
    names = {}
    ids = {}
    consts = {}
    for prop in props:
        iid = prop['iid']
        t = prop['type']
        access = prop['access']
        obj = re.search(r':property:(.*?):', t)
        oname = obj.group(1)
        name = parseName(oname)
        cname = oname.upper().replace('-', '_')
        # id -> name
        idstr = '{}.{}'.format(sid, iid)
        ids[idstr] = name
        # name -> id
        if ('write' in access) or ('notify' in access):
            names[name] = {'siid': sid, 'piid': iid}
            consts[cname] = name
    return {"names": names, "ids": ids, "consts": consts}


def parseEvents(events, sid):
    names = {}
    ids = {}
    consts = {}
    for prop in events:
        iid = prop['iid']
        t = prop['type']
        obj = re.search(r':event:(.*?):', t)
        oname = obj.group(1)
        name = parseName(oname)
        cname = oname.upper().replace('-', '_')
        # id -> name
        idstr = '{}.{}'.format(sid, iid)
        ids[idstr] = name
        # name -> id
        names[name] = {'siid': sid, 'eiid': iid}
        consts[cname] = name
    return {"names": names, "ids": ids, "consts": consts}


def saveFile(data):
    f = open('./protocal.js', 'w')
    json.dump(data, f, indent=2, sort_keys=True)


def parse(fileName):
    data = paresJson(fileName)
    print(data)
    saveFile(data)

parse('./example/light.json')
