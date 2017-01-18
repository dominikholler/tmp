#! /usr/bin/python
import json
import requests


class Entity(object):

    def __init__(self, ovirt, store={}, autoupdate=True):
        object.__setattr__(self, 'ovirt', ovirt)
        object.__setattr__(self, 'store', store)
        object.__setattr__(self, 'autoupdate', autoupdate)

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __getattr__(self, attr):
        if self.store.has_key(attr):
            return self.store[attr]
        else:
            if not attr == 'link':
                for link in self.store['link']:
                    if link.rel == attr:
                        return self.ovirt.get(link.href)
            raise KeyError('Key "{}" not found'.format(attr))

    def __setattr__(self, attr, value):
        self.store[attr] = value
        if self.autoupdate:
            self.update()

    def __repr__(self):
        return str(self.store)

    def values(self):
        return self.store.values()

    def update(self):
        return self.ovirt.put(self.href, self)

    def delete(self):
        return self.ovirt.delete(self.href)

    def add(self, path, data):
        if 'href' in self.store:
            href = self.href
        else:
            href = self.ovirt.base
        return self.ovirt.post(href + '/' + path, data)


def as_entity(ovirt):
    def entiy(dct):
        return Entity(ovirt, dct)
    return entiy

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Entity):
            return obj.store
        return json.JSONEncoder.default(self, obj)

class OVirt:

    HEADERS = {"Accept": "application/json", 'Content-type': 'application/json'}

    def __init__(self, auth=('admin@internal', 'engine'), host='http://localhost:8080', base='/ovirt-engine/api'):
        self.host=host
        self.base=base
        self.session = requests.Session()
        self.session.auth = auth
        self.session.headers.update(self.HEADERS)

    def _absolute_path(self, path):
        if path.startswith('/'):
            return path
        else:
            return self.base + '/' + path

    def _url(self, path):
        return self.host + self._absolute_path(path)

    def post(self, path, data):
        data = json.dumps(data, cls=ComplexEncoder)
        response = self.session.post(self._url(path), data=data)
        if response.ok:
            return json.loads(response.content, object_hook=as_entity(self))
        else:
            response.raise_for_status()

    def put(self, path, data):
        data = json.dumps(data, cls=ComplexEncoder)
        response = self.session.put(self._url(path), data=data)
        if response.ok:
            return json.loads(response.content, object_hook=as_entity(self))
        else:
            response.raise_for_status()

    def get(self, path):
        response = self.session.get(self._url(path))
        if response.ok:
            data = json.loads(response.content, object_hook=as_entity(self))

            if len(data) == 1:
                return data.values()[0]
            else:
                return data
        else:
            response.raise_for_status()

    def delete(self, path):
        response = self.session.delete(self._url(path))
        if response.ok:
            return json.loads(response.content)
        else:
            response.raise_for_status()

    def root(self):
        return self.get('')



name_prefix = 'Labeled_Net'
MANY_NETS = {'id': 'MANY_NETS'}
NUMBER_OF_NETS = 10


def removeNetworkAttachments(host):
    #nas = ovirt.get(host['href'] + '/networkattachments')
    nas = host.networkattachments
    for na in nas:
        if not na.network.id == '00000000-0000-0000-0000-000000000009':
            na.delete()

def removeNetworks(networks):
    for network in networks:
        if network.name.startswith(name_prefix):
            network.delete()

def createNetworks(ovirt, number):
    for i in range(1, number+1):
        net = Entity(ovirt.ovirt, autoupdate=False)
        net.usages = { 'usage': ['vm'] }
        net.data_center= ovirt.datacenters[0]
        net.name = '{}{:03d}'.format(name_prefix, i)
        net.description = 'Network on VLAN {}'.format(i)
        net.vlan = { 'id': str(i) }
        #response = networks.add(net)
        response = ovirt.add('networks', net)
        #path = response['href'] + '/networklabels'
        #ovirt.post(path, {'id': 'MANY_NETS'})
        response.add('networklabels', MANY_NETS)
        #print response.networklabels.add({'id': 'MANY_NETS2'})


def changeDesc(networks):
    for network in networks:
        if network.name == 'Labeled_Net001':
            network.description = 'changed8'
            #ovirt.put(network['href'], network)
            break

def addTocluster(ovirt):
    cluster=ovirt.clusters[0]
    for network in ovirt.networks:
        if network.name.startswith(name_prefix):
            network.required = False
            response = cluster.add('networks', network)



ovirt = OVirt().root()



#print ovirt

#hosts = ovirt.get('hosts')
#print hosts 
host = ovirt.hosts[0]
print host.name
#print host.networkattachments[0].id
#print host.networkattachments[0].network
#changeDesc(ovirt)


print 'delete labels'
for nic in host.nics:
    for label in nic.networklabels:
        print label
        print label.delete()

print 'removeNetworkAttachments(ovirt)'
removeNetworkAttachments(host)
print 'removeNetwork(ovirt)'
removeNetworks(ovirt.networks)
print 'createNetwork(ovirt)'
createNetworks(ovirt, NUMBER_OF_NETS)
print 'addTocluster(ovirt)'
addTocluster(ovirt)

#cluster=ovirt.get('clusters')[0].networks
#print cluster

print "host.nics[0].add('networklabels', MANY_NETS)"
print host.nics[0].add('networklabels', MANY_NETS)

print 'len(host.nics:) ', len(host.nics)
print host
