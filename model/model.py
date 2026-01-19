from UI.controller import Controller
from database.dao import DAO
import networkx as nx
from geopy import distance

class Model:
    def __init__(self):
        self.list_sighting = []
        self.list_shapes = []
        self.list_states = []

        # chiamo i metodi direttamente "nel main" -> per riempire direttamente le liste
        self.load_sighting()
        self.load_shapes()
        self.load_states()

        self.G = nx.Graph() #creo un grafo
        self._nodes = [] #creo una lista vuota di nodi
        self._edges = [] #creo una lista vuota di archi
        self.id_map = {} #creo una mappa per identificare i vari nodi
        self.sol_best = 0

        self.path = []
        self.path_edge = []

    #richiamo il DAO e riempo la lista degli avvistamenti
    def load_sighting(self):
        self.list_sighting = DAO.get_all_sighting()

    # richiamo il DAO e riempo la lista delle forme
    def load_shapes(self):
        self.list_shapes = DAO.get_all_shapes()

    # richiamo il DAO e riempo la lista degli stati
    def load_states(self):
        self.list_states = DAO.get_all_states()

    #metodo per creare il grafo
    def build_graph(self, s, a):
        self.G.clear() #pulisco il grafo come primissima cosa
        print(a, s)

        for p in self.list_states: #per ogni nodo (stato) nella lista di stata
            self._nodes.append(p) #riempio la lista di nodi con i vari nodi (stati)

        self.G.add_nodes_from(self._nodes) #aggiungo i nodi al grafo
        self.id_map = {}
        for n in self._nodes: #per ogni nodo nella lista di nodi
            self.id_map[n.id] = n #aggiungo i nodi nella mappa, con chiave l'id e valore il nodo

        tmp_edges = DAO.get_all_weighted_neigh(a, s)

        self._edges.clear() #pulisco la lingua di edges
        # aggiungo nella lista: il primo oggetto 'st1', il secondo oggetto 'st2' e il numero di casi 'N'
        for e in tmp_edges:
            self._edges.append((self.id_map[e[0]], self.id_map[e[1]], e[2]))

        self.G.add_weighted_edges_from(self._edges)

    #metodo per trovare il peso di ciascun nodo
    def get_sum_weight_per_node(self):
        pp = []
        for n in self.G.nodes():
            sum_w = 0
            for e in self.G.edges(n, data=True):
                sum_w += e[2]['weight']
            pp.append((n.id, sum_w))
        return pp

    def get_nodes(self):
        return self.G.nodes

    def get_edges(self):
        return self.G.edges

    def get_num_of_nodes(self):
        return self.G.number_of_nodes()

    def get_num_of_edges(self):
        return self.G.number_of_edges()

    def compute_path(self):
        self.path = []
        self.path_edge = []
        self.sol_best = 0

        partial = [] #lista dove inserirò i nodi

        for n in self.get_nodes():  #per ogni nodo
            partial.clear() #pulisco la lista
            partial.append(n) #appendo il nodo nella lista
            self._ricorsione(partial, []) #parto con la ricorsione, passando il nodo e la lista di archi

    def _ricorsione(self, partial, partial_edge):
        n_last = partial[-1]

        neighbors = self.get_admissible_neighbs(n_last, partial_edge) #analizzo tutti i possibili vicini

        if len(neighbors) == 0: #quando ho esplorato tutti i possibili vicini
            weight_path = self.compute_weight_path(partial_edge)
            if weight_path > self.sol_best:
                self.sol_best = weight_path + 0.0
                self.path = partial[:]
                self.path_edge = partial_edge[:]
            return

        for n in neighbors:
            partial_edge.append((n_last, n, self.G.get_edge_data(n_last, n)['weight'])) #lista archi da esplorare
            partial.append(n) #lista nodi da esplorare

            self._ricorsione(partial, partial_edge) #lancio di nuovo la ricorsione

            partial.pop() #cancello i nodi (tornando su) per ripartire con la ricorsione
            partial_edge.pop() #cancello gli archi (tornando su) per ripartire con la ricorsione

    def get_admissible_neighbs(self, n_last, partial_edges):
        all_neigh = self.G.edges(n_last, data=True)
        result = []

        for e in all_neigh:
            if len(partial_edges) != 0:
                if e[2]["weight"] > partial_edges[-1][2]:
                    result.append(e[1])
            else:
                result.append(e[1])
        return result

    def compute_weight_path(self, mylist):
        weight = 0
        for e in mylist:
            weight += distance.geodesic((e[0].lat, e[0].lng), (e[1].lat, e[1].lng)).km
        return weight

    def get_distance_weight(self, e):
        return distance.geodesic((e[0].lat, e[0].lng), (e[1].lat, e[1].lng)).km

