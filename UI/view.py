import flet as ft


class View(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        # page stuff
        self._page = page
        self._page.title = "Lab11-Simulazione esame"
        self._page.horizontal_alignment = 'CENTER'
        self._page.theme_mode = ft.ThemeMode.LIGHT
        # controller (it is not initialized. Must be initialized in the main, after the controller is created)
        self._controller = None
        # graphical elements
        self._title = None
        self.txt_name = None
        self.btn_hello = None
        self.txt_result = None
        self.txt_container = None

    def load_interface(self):
        # title
        self._title = ft.Text("TdP-Simulazione esame Chinook", color="blue", size=24)
        self._page.controls.append(self._title)


        self._ddGenre = ft.Dropdown(label="Genere")
        self._controller.fillDDGenre()
        self._btnCreaGrafo = ft.ElevatedButton(text="Crea Grafo", on_click=self._controller.handleCreaGrafo)

        row1 = ft.Row([self._ddGenre, self._btnCreaGrafo],
                      alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(row1)

        self._ddArtist = ft.Dropdown(label="Artist")
        self._btnCreaGrafo = ft.ElevatedButton(text="Trova Cammino", on_click=self._controller.handleCammino)

        row2 = ft.Row([self._ddArtist, self._btnCreaGrafo],
                      alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(row2)

        # List View where the reply is printed
        self.txt_result = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self._page.controls.append(self.txt_result)
        self._page.update()

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.dialog = dlg
        dlg.open = True
        self._page.update()

    def update_page(self):
        self._page.update()

    def popola_dropdown_generi(self, lista_generi):
        """lista_generi: lista di tuple (GenreId, Name) dal Model"""
        self._ddGenre.options = [
            ft.dropdown.Option(key=str(genere_id), text=nome)
            for genere_id, nome in lista_generi
        ]
        self.update_page()

    def get_genere_selezionato(self):
        """Restituisce l'id del genere selezionato (come stringa), o None se non scelto"""
        return self._ddGenre.value

    def popola_dropdown_artisti(self, lista_artisti):
        """lista_artisti: lista di oggetti Artist (con .artist_id e .name)"""
        self._ddArtist.options = [
            ft.dropdown.Option(key=str(artista.artist_id), text=artista.name)
            for artista in lista_artisti
        ]
        self.update_page()

    def get_artista_selezionato(self):
        """Restituisce l'id dell'artista selezionato (come stringa), o None"""
        return self._ddArtist.value

    def mostra_errore(self, messaggio):
        self.create_alert(messaggio)

    def mostra_risultati_grafo(self, num_nodi, num_archi, artista_top, influenza_top, top_5):
        self.txt_result.controls.clear()

        self.txt_result.controls.append(ft.Text("Grafo correttamente creato:"))
        self.txt_result.controls.append(ft.Text(f"Numero di nodi: {num_nodi}"))
        self.txt_result.controls.append(ft.Text(f"Numero di archi: {num_archi}"))

        if artista_top is not None:
            self.txt_result.controls.append(
                ft.Text(f"Artista più influente: {artista_top.name}, con influenza: {influenza_top}")
            )

        self.txt_result.controls.append(ft.Text("Top 5 archi:"))
        for nodo_a, nodo_b, dati in top_5:
            self.txt_result.controls.append(
                ft.Text(f"{nodo_a.name} -> {nodo_b.name} : {dati['weight']}")
            )

        self.update_page()

    def mostra_cammino(self, cammino):
        self.txt_result.controls.clear()

        self.txt_result.controls.append(ft.Text("Cammino trovato:"))
        testo_cammino = " -> ".join(artista.name for artista in cammino)
        self.txt_result.controls.append(ft.Text(testo_cammino))
        self.txt_result.controls.append(ft.Text(f"Lunghezza (numero di nodi): {len(cammino)}"))

        self.update_page()