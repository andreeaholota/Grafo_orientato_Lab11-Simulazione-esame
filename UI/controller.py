import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    def fillDDGenre(self):
        """Chiamato dalla View all'avvio per popolare la tendina dei generi"""
        lista_generi = self._model.get_generi()
        self._view.popola_dropdown_generi(lista_generi)

    def handleCreaGrafo(self, e):
        """Gestisce il click sul bottone 'Crea Grafo'"""

        # 1. Validazione input: l'utente deve aver selezionato un genere
        genere_id = self._view.get_genere_selezionato()

        if genere_id is None:
            self._view.mostra_errore("Seleziona un genere prima di procedere.")
            return

        try:
            genere_id = int(genere_id)
        except (ValueError, TypeError):
            self._view.mostra_errore("Genere non valido.")
            return

        # 2. Costruzione del grafo tramite il Model
        num_nodi, num_archi = self._model.crea_grafo(genere_id)

        if num_nodi == 0:
            self._view.mostra_errore("Nessun artista trovato per il genere selezionato.")
            return

        # 3. Calcolo statistiche derivate dal grafo
        artista_top, influenza_top = self._model.get_artista_piu_influente()
        top_5 = self._model.get_top_5_archi()

        # 4. Passo tutto alla View per la visualizzazione
        self._view.mostra_risultati_grafo(num_nodi, num_archi, artista_top, influenza_top, top_5)

        # 5. Popolo la seconda tendina (artisti) con gli artisti del genere selezionato
        lista_artisti = self._model.get_id_map().values()
        self._view.popola_dropdown_artisti(lista_artisti)

    def handleCammino(self, e):
        """Click su 'Trova Cammino'."""
        if self._model.get_grafo() is None:
            self._view.mostra_errore("Devi prima creare il grafo.")
            return

        # 1. Recupera il valore selezionato dal dropdown degli artisti
        artista_id_str = self._view.get_artista_selezionato()

        if artista_id_str is None:
            self._view.mostra_errore("Seleziona un artista prima di procedere.")
            return

        # 2. Converti l'ID in intero in modo sicuro
        try:
            artista_id = int(artista_id_str)
        except (ValueError, TypeError):
            self._view.mostra_errore("ID Artista non valido.")
            return

        # 3. Recupera l'oggetto Artist reale dalla Identity Map del modello
        id_map = self._model.get_id_map()
        artista_iniziale = id_map.get(artista_id)

        if artista_iniziale is None:
            self._view.mostra_errore("L'artista selezionato non fa parte del grafo corrente.")
            return

        # 4. Lancia la ricorsione ed ottieni il cammino dei nodi
        cammino_ottimo = self._model.trova_cammino(artista_iniziale)

        # 5. Passa il cammino alla view per stamparlo
        self._view.mostra_cammino(cammino_ottimo)
