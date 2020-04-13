#!/usr/bin/env python
#-- coding:UTF-8 --
import json
import re
import argparse
import os.path
# spec协议转换

def paresJson(fileName, eventFilter=None, propFilter=None, actionFilter=None):
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
            ps = parseProps(props, iid, propFilter)
            protocal['prop'].update(ps['names'])
            protocal['prop'].update(ps['ids'])
            consts['prop'].update(ps['consts'])
        if 'actions' in service:
            actions = service['actions']
            acs = parseAction(actions, iid, actionFilter)
            protocal['action'].update(acs['names'])
            consts['action'].update(acs['consts'])
        if 'events' in service:
            events = service['events']
            es = parseEvents(events, iid, eventFilter)
            protocal['event'].update(es['names'])
            protocal['event'].update(es['ids'])
            consts['event'].update(es['consts'])
    return {'protocal': protocal, 'consts': consts}


# abc-edf -> abcEdf 短横线命名转换为驼峰式命名
def parseName(nameStr):
    names = nameStr.split('-')
    if len(names) <= 1:
        return nameStr
    else:
        ns = list(map(lambda name: name.capitalize(), names[1:]))
        ns.insert(0, names[0])
        return ''.join(ns)


def parseAction(actions, sid, filter):
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
        if (not filter) or (not re.match(filter, '{}.{}'.format(sid, iid))):
            names[name] = {'siid': sid, 'aiid': iid}
            consts[cname] = name
    return {"names": names, "consts": consts}


def parseProps(props, sid, filter):
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
        if (not filter) or (not re.match(filter, idstr)):
            ids[idstr] = name
            # name -> id
            if ('read' in access) and ('notify' in access):
                names[name] = {'siid': sid, 'piid': iid}
                consts[cname] = name
    return {"names": names, "ids": ids, "consts": consts}


def parseEvents(events, sid, filter):
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
        if (not filter) or (not re.match(filter, idstr)):
            ids[idstr] = name
            # name -> id
            names[name] = {'siid': sid, 'eiid': iid}
            consts[cname] = name
    return {"names": names, "ids": ids, "consts": consts}


def format(data):
    d = re.sub('\"(\S+)\"(\s*:\s*)', lambda a: a.group(1) + a.group(2),
               json.dumps(data, indent=2, sort_keys=True))
    d = d.replace('\"', '\'')
    return d


def saveFile(data, outPath='./'):
    if not os.path.exists(outPath):
      os.makedirs(outPath)
    
    protocalFile = os.path.join(outPath, 'protocal.js')
    f = open(protocalFile, 'w')
    f.write('export default ')
    f.write(format(data['protocal']))
    constsFile = os.path.join(outPath, 'SpecConsts.js')
    f = open(constsFile, 'w')
    f.write('const PROP = ')
    consts = data['consts']
    f.write(format(consts['prop']))
    f.write('\nconst ACTION = ')
    f.write(format(consts['action']))
    f.write('\nconst EVENT = ')
    f.write(format(consts['event']))
    f.write('\n')
    f.write('export default { PROP, ACTION, EVENT }')

def parse(fileName, eventFilter=None, propFilter=None, actionFilter=None, outPath='./'):
    data = paresJson(fileName, eventFilter, propFilter, actionFilter)
    saveFile(data, outPath)


# 参数解析
def main():
    parser = argparse.ArgumentParser(description=u'将spec的json文件转换为协议文件')
    parser.add_argument("path", help=u'spec的json文件路径')
    parser.add_argument("-c", "--config", help=u'通过配置文件进行转换')
    parser.add_argument("-p",
                        "--propFilter",
                        help=u'需要过滤掉的prop(比如1.*)，支持正则表达式')
    parser.add_argument("-a",
                        "--actionFilter",
                        help=u'需要过滤掉的action(比如1.2)，支持正则表达式')
    parser.add_argument("-e",
                        "--eventFilter",
                        help=u'需要过滤掉的event(比如1.[2-10])，支持正则表达式')
    parser.add_argument("-o",
                    "--outPath",
                    default='./',
                    help=u'输出文件目录，默认为当前目录')

    args = parser.parse_args()
    if (args.path != None) and (os.path.exists(args.path)):
        parseConfig = vars(args)
        if (args.config != None) and (os.path.exists(args.config)):
            f = open(args.config, 'r')
            config = json.load(f)
            if config != None:
                parseConfig.update(config)
        parse(args.path,
              propFilter=parseConfig['propFilter'],
              actionFilter=parseConfig['actionFilter'],
              eventFilter=parseConfig['eventFilter'],
              outPath=parseConfig['outPath'],
              )

# parse('./example/light.json',
#       propFilter=r'(1.*)|(2.[2|4|5])|(4.[2-5])|(4.1[2-8])',
#       eventFilter=r'4.*',
#       actionFilter=r'(2.[1-2])|(4.[1|6|7])')

if __name__ == '__main__':
    main()
