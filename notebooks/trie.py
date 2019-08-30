import collections

AllCustomers = collections.namedtuple('AllCustomers', [])
Customer = collections.namedtuple('Customer', ["customer_id"])
AllCustomerOrders = collections.namedtuple('AllCustomerOrders', ["customer_id"])
CustomerOrder = collections.namedtuple('CustomerOrder', ["customer_id", "order_id"])
AllCustomerOrderLineitems = collections.namedtuple('AllCustomerOrderLineitems', ["customer_id", "order_id"])


DYNAMIC = 'dynamic'
SEPERATOR = '/'


class Node():
    def __init__(self):
        self.children : Dict[str, Node] = {}
        self.value : Any = None

    def traversal(self, char, params=[]):
        if char in self.children:
            return self.children[char]
        else:
            return None


class SeperateNode(Node):
    def traversal(self, char, params):
        if DYNAMIC in self.children:
           params.append(char)
           return self.children[DYNAMIC]
        else:
           if char in self.children:
               return self.children[char]
           else:
               return None


class DynamicNode(Node):
    def traversal(self, char, params):
        if char == SEPERATOR:
            if char in self.children:
                return self.children[char]
            else:
                return None
        else:
            params[-1] += char
            return self

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
    NODES = {
        DYNAMIC: DynamicNode,
        SEPERATOR: SeperateNode
    }

    def __init__(self):
        self._root = Node()


    def search(self, path):
        current = self._root
        params = []
        for char in path.strip(SEPERATOR):
            current = current.traversal(char, params)
            if current is None:
               return None
        return current.value(*params)


    def insert(self, path_segments, value):
        current = self._root
        for segment in path_segments:
            for char in segment:
                clazz = self.NODES.get(char, Node)
                if char not in current.children:
                    current.children[char] = clazz()
                current = current.children[char]
        current.value = value


