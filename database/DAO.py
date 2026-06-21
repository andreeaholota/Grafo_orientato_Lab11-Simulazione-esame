from database.DB_connect import DBConnect


class DAO:
    """Unico strato che parla con il database. Nessuna logica di business qui."""

    # GENERI PER LA TENDINA
    @staticmethod
    def get_all_generi():
        """Recupera tutti i generi per popolare la tendina 'Genere'."""
        conn = DBConnect.get_connection()
        result = []

        if conn is None:
            return result

        try:
            cursor = conn.cursor(dictionary=True)

            query = "SELECT GenreId, Name FROM genre ORDER BY Name ASC"
            cursor.execute(query)

            for row in cursor:
                result.append((row["GenreId"], row["Name"]))

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Errore nel metodo get_all_generi: {e}")
            if conn:
                conn.close()

        return result

    # VERTICE: ARTISTI
    @staticmethod
    def get_artisti_per_genere(genere_id):
        """Vertici del grafo: artisti con almeno un brano del genere scelto.
        JOIN a catena artist -> album -> track per arrivare al genere."""
        conn = DBConnect.get_connection()
        result = []

        if conn is None:
            return result

        try:
            cursor = conn.cursor(dictionary=True)

            query = """
                    SELECT DISTINCT a.ArtistId, a.Name
                    FROM artist a
                    JOIN album al ON a.ArtistId = al.ArtistId
                    JOIN track t ON al.AlbumId = t.AlbumId
                    WHERE t.GenreId = %s
                    """
            cursor.execute(query, (genere_id,))

            for row in cursor:
                result.append((row["ArtistId"], row["Name"]))

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Errore nel metodo get_artisti_per_genere: {e}")
            if conn:
                conn.close()

        return result


    @staticmethod
    def get_popolarita_artisti():
        """Popolarita' di OGNI artista = somma dei brani acquistati (SUM Quantity).
        Non filtra per genere: la popolarita' e' un dato globale dell'artista."""
        conn = DBConnect.get_connection()
        result = {}  # dizionario per accesso O(1): ArtistId -> popolarita'

        if conn is None:
            return result

        try:
            cursor = conn.cursor(dictionary=True)

            query = """
                    SELECT al.ArtistId, SUM(il.Quantity) AS Popolarita
                    FROM invoiceline il
                    JOIN track t ON il.TrackId = t.TrackId
                    JOIN album al ON t.AlbumId = al.AlbumId
                    GROUP BY al.ArtistId
                    """
            cursor.execute(query)

            for row in cursor:
                result[row["ArtistId"]] = row["Popolarita"] # Chiave ArtistID e valore Popolarita

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Errore nel metodo get_popolarita_artisti: {e}")
            if conn:
                conn.close()

        return result

    # CREO ARCHI
    @staticmethod
    def get_coppie_clienti_comuni(genere_id):
        """Coppie di artisti (id1 < id2) acquistati dallo stesso CLIENTE (non fattura),
        entrambi nel genere scelto. Self-join: due 'rami' della stessa catena di JOIN,
        collegati tramite CustomerId."""
        conn = DBConnect.get_connection()
        result = []

        if conn is None:
            return result

        try:
            cursor = conn.cursor(dictionary=True)

            query = """
                    SELECT DISTINCT al1.ArtistId AS id1, al2.ArtistId AS id2
                    FROM invoice i1
                    JOIN invoiceline il1 ON i1.InvoiceId = il1.InvoiceId
                    JOIN track t1 ON il1.TrackId = t1.TrackId
                    JOIN album al1 ON t1.AlbumId = al1.AlbumId

                    JOIN invoice i2 ON i1.CustomerId = i2.CustomerId
                    JOIN invoiceline il2 ON i2.InvoiceId = il2.InvoiceId
                    JOIN track t2 ON il2.TrackId = t2.TrackId
                    JOIN album al2 ON t2.AlbumId = al2.AlbumId

                    WHERE t1.GenreId = %s
                      AND t2.GenreId = %s
                      AND al1.ArtistId < al2.ArtistId
                    """
            cursor.execute(query, (genere_id, genere_id))

            for row in cursor:
                result.append((row["id1"], row["id2"]))

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Errore nel metodo get_coppie_clienti_comuni: {e}")
            if conn:
                conn.close()

        return result