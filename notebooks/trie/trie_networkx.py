import collections

AllCustomers = collections.namedtuple('AllCustomers', [])
Customer = collections.namedtuple('Customer', ["customer_id"])
AllCustomerOrders = collections.namedtuple('AllCustomerOrders', ["customer_id"])
CustomerOrder = collections.namedtuple('CustomerOrder', ["customer_id", "order_id"])
AllCustomerOrderLineitems = collections.namedtuple('AllCustomerOrderLineitems', ["customer_id", "order_id"])

import networkx as nx
from networkx.utils import generate_unique_node

DYNAMIC = 'dynamic'
SEPERATOR = '/'

def normal_traverse(trie, node, key, params=[]):
    return trie.successor(node, key)


def seperator_traverse(trie, node, key, params):
    dynamic_node = trie.successor(node, DYNAMIC)
    if dynamic_node is not None:
        params.append(key)
        return dynamic_node
    else:
        return normal_traverse(trie, node, key)


def dynamic_traverse(trie, node, key, params):
    if key == SEPERATOR:
        return normal_traverse(trie, node, key)
    else:
        params[-1] += key
        return node


class Trie:
    """
    >>> trie = Trie()
    >>> trie.insert(["customers"], AllCustomers)
    >>> trie.insert(["customers/", [DYNAMIC]], Customer)
    >>> trie.insert(["customers/", [DYNAMIC], "/orders"], AllCustomerOrders)
    >>> trie.insert(["customers/", [DYNAMIC], "/orders/", [DYNAMIC]], CustomerOrder)
    >>> trie.insert(["customers/", [DYNAMIC], "/orders/", [DYNAMIC], "/lineitems"], AllCustomerOrderLineitems)
    >>> resource = trie.search("/customers")
    >>> isinstance(resource, AllCustomers)
    True
    >>> resource = trie.search("/customers/")
    >>> isinstance(resource, AllCustomers)
    True
    >>> resource = trie.search("/customers/33245")
    >>> isinstance(resource, Customer)
    True
    >>> resource.customer_id
    '33245'
    >>> resource = trie.search("/customers/33245/orders")
    >>> isinstance(resource, AllCustomerOrders)
    True
    >>> resource.customer_id
    '33245'
    >>> resource = trie.search("/customers/33245/orders/8769")
    >>> isinstance(resource, CustomerOrder)
    True
    >>> (resource.customer_id, resource.order_id)
    ('33245', '8769')
    >>> resource = trie.search("/customers/33245/orders/8769/lineitems")
    >>> isinstance(resource, AllCustomerOrderLineitems)
    True
    >>> (resource.customer_id, resource.order_id)
    ('33245', '8769')
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        self._root, root_attr = self.__build_node(None)
        self.graph.add_node(self._root, **root_attr)


    def search(self, path):
        current = self._root
        params = []
        for char in path.strip(SEPERATOR):
            current = self.__traverse(current, char, params)
            if current is None:
               return None
        return self.__node(current).get('clazz')(*params)


    def insert(self, path_segments, value):
        current = self._root
        for segment in path_segments:
            for char in segment:
                next_node = self.successor(current, char)
                if next_node is None:
                    next_node, next_node_attr = self.__build_node(char)
                    self.graph.add_node(next_node, **next_node_attr)
                    self.graph.add_edge(current, next_node)
                current = next_node
        self.__node(current)['clazz'] = value


    def successor(self, node, key):
        return next(filter(lambda n: self.__node(n).get('key') == key, self.graph.succ[node]), None)


    def __node(self, node):
        return self.graph.nodes[node]

    def __build_node(self, key, clazz=None):
        return (generate_unique_node(), dict(key=key, clazz=clazz))

    def __traverse(self, node, char, params):
        NODES = {
            DYNAMIC: dynamic_traverse,
            SEPERATOR: seperator_traverse
        }
        return NODES.get(self.__node(node).get('key'), normal_traverse)(self, node, char, params)

