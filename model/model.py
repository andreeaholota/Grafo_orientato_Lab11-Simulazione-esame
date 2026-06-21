import networkx as nx
from database.DAO import DAO


class Artist:
    """Classe di dominio: rappresenta un artista e diventa nodo del grafo."""

    def __init__(self, artist_id: int, name: str):
        self._artist_id = artist_id
        self._name = name
        self._popolarita = 0  # impostata dopo, leggendo i dati di vendita

    @property
    def artist_id(self):
        return self._artist_id

    @property
    def name(self):
        return self._name

    @property
    def popolarita(self):
        return self._popolarita

    @popolarita.setter
    def popolarita(self, valore):
        self._popolarita = valore

    def __eq__(self, other):
        # due Artist sono uguali se hanno lo stesso id
        if not isinstance(other, Artist):
            return False
        return self._artist_id == other._artist_id

    def __hash__(self):
        # OBBLIGATORIO insieme a __eq__: serve a NetworkX per usare Artist come nodo
        return hash(self._artist_id)

    def __str__(self):
        return self._name

    def __repr__(self):
        return f"Artist({self._artist_id}, {self._name})"


class Model:
    """Logica di business: costruzione del grafo, statistiche, backtracking."""

    def __init__(self):
        self._grafo = None
        self._id_map = {}     # Identity Map: ArtistId -> oggetto Artist (unicita')
        self._migliore = []   # stato del backtracking: miglior cammino trovato
        self._parziale = []   # stato del backtracking: cammino in costruzione

    # ---------- accessori di stato (usati dal Controller) ----------

    def get_grafo(self):
        return self._grafo

    def get_id_map(self):
        return self._id_map

    # ---------- PUNTO 1 ----------

    def get_generi(self):
        """Passacarte verso il DAO per popolare la tendina dei generi."""
        return DAO.get_all_generi()

    # CREA GRAFO

    def crea_grafo(self, genere_id):
        # Reset dello stato ad ogni nuova creazione
        self._grafo = nx.DiGraph()
        self._id_map = {} # Azzera la mappa d'identità

        # 1. Recupero i vertici: artisti del genere selezionato
        lista_artisti = DAO.get_artisti_per_genere(genere_id)

        for artist_id, nome in lista_artisti:
            artista = Artist(artist_id, nome)
            self._id_map[artist_id] = artista

        # 2. Recupero la popolarità di TUTTI gli artisti (non solo quelli del genere)
        mappa_popolarita = DAO.get_popolarita_artisti()

        # 3. Assegno la popolarità ai soli artisti presenti nella Identity Map
        for artist_id, artista in self._id_map.items():
            artista.popolarita = mappa_popolarita.get(artist_id, 0) #arricchisce gli oggetti Artist presenti nella
            # nostra mappa, inserendo dentro l'attributo .popolarita il valore numerico corrispondente.
            # Se un artista non ha vendite, assegna di default 0 grazie a .get(..., 0).

        # 4. Aggiungo i nodi al grafo
        self._grafo.add_nodes_from(self._id_map.values())

        # 5. Recupero le coppie di artisti acquistati dallo stesso cliente
        coppie = DAO.get_coppie_clienti_comuni(genere_id)

        # 6. Per ogni coppia, creo l'arco/i con verso e peso corretti
        for id1, id2 in coppie:
            # entrambi gli id devono essere artisti del genere selezionato
            if id1 not in self._id_map or id2 not in self._id_map:
                continue

            artista1 = self._id_map[id1]
            artista2 = self._id_map[id2]

            peso = artista1.popolarita + artista2.popolarita

            if artista1.popolarita > artista2.popolarita:
                self._grafo.add_edge(artista1, artista2, weight=peso)
            elif artista2.popolarita > artista1.popolarita:
                self._grafo.add_edge(artista2, artista1, weight=peso)
            else:
                # stessa popolarità: due archi, uno per verso
                self._grafo.add_edge(artista1, artista2, weight=peso)
                self._grafo.add_edge(artista2, artista1, weight=peso)

        return self._grafo.number_of_nodes(), self._grafo.number_of_edges()

    def get_artista_piu_influente(self):
        """Influenza = peso archi uscenti - peso archi entranti, per ogni nodo."""
        if self._grafo is None or self._grafo.number_of_nodes() == 0: #Controllo se il grafo esiste o se vuoto
            return None, 0

        artista_top = None
        influenza_top = float('-inf') #Inizializzare il valore massimo a meno infinito

        for artista in self._grafo.nodes():
            peso_uscenti = sum(dati["weight"] for _, _, dati in self._grafo.out_edges(artista, data=True))
            peso_entranti = sum(dati["weight"] for _, _, dati in self._grafo.in_edges(artista, data=True))
            influenza = peso_uscenti - peso_entranti

            if influenza > influenza_top:
                influenza_top = influenza
                artista_top = artista

        return artista_top, influenza_top

    def get_top_5_archi(self):
        """I 5 archi con peso maggiore, ordine decrescente."""
        if self._grafo is None:
            return []

        lista_archi = list(self._grafo.edges(data=True))
        # ordino con una lambda perche' Artist non ha __lt__ definito
        lista_archi.sort(key=lambda arco: arco[2]["weight"], reverse=True) #arco[2]: Il dizionario degli attributi
                                                                           # dell'arco (dove è memorizzato il peso).
        return lista_archi[:5]

    # ---------- PUNTO 2: backtracking ----------

    def trova_cammino(self, artista_iniziale):
        """Funzione pubblica di innesco: inizializza lo stato e lancia la ricorsione."""
        self._migliore = [artista_iniziale]
        self._parziale = [artista_iniziale]

        self._cerca(artista_iniziale, peso_minimo=0)

        return self._migliore

    def _cerca(self, nodo_attuale, peso_minimo):
        """Esplora l'albero delle decisioni in profondita' (DFS + backtracking)."""

        # caso terminale: il cammino parziale e' il migliore finora -> lo congelo
        if len(self._parziale) > len(self._migliore):
            self._migliore = list(self._parziale)  # copia fisica, non riferimento!

        # ciclo di esplorazione: provo ogni arco uscente dal nodo attuale
        for vicino in self._grafo.successors(nodo_attuale):

            if vicino in self._parziale:
                continue  # vincolo: cammino semplice, niente nodi ripetuti

            peso_arco = self._grafo[nodo_attuale][vicino]["weight"]

            if peso_arco > peso_minimo:  # vincolo: peso strettamente crescente
                self._parziale.append(vicino)        # PUSH
                self._cerca(vicino, peso_arco)        # esploro
                self._parziale.pop()                  # POP (torno indietro)