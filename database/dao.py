from database.DB_connect import DBConnect
from model.state import State
from model.sighting import Sighting

class DAO:

    # PRENDO TUTTI GLI STATI
    @staticmethod
    def get_all_states():
        conn = DBConnect.get_connection() #connessione
        result = [] #creo la lista per i risultati
        cursor = conn.cursor(dictionary=True) #cursore

        query = """ SELECT * FROM state """ #creo la query -> prendo tutti gli stati

        cursor.execute(query)

        for row in cursor:
            #creo oggetti "State" e li "appendo" nella lista "result"
            result.append(State(row["id"], row["name"], row["capital"], row["lat"], row["lng"], row["area"], row["population"], row["neighbors"]))


        cursor.close() #chiudo il cursore
        conn.close() #chiudo la connessione
        return result #restituisco il "result" -> una lista di oggetti "State"

    # PRENDO TUTTI GLI AVVISTAMENTI
    @staticmethod
    def get_all_sighting():
        conn = DBConnect.get_connection()
        result = []  #creo la lista per i risultati
        cursor = conn.cursor(dictionary=True)  #cursore

        query = """ SELECT * 
                    FROM sighting 
                    ORDER BY s_datetime ASC """  #creo la query -> prendo tutti gli avvistamenti (in ordine crescente in base all'anno)

        cursor.execute(query)

        for row in cursor:
            #creo oggetti "Sights" e li "appendo" nella lista "result"
            result.append(Sighting(**row))

        cursor.close()  #chiudo il cursore
        conn.close()  #chiudo la connessione
        return result  #restituisco il "result" -> una lista di oggetti "State"

    # PRENDO TUTTE LE FORME
    @staticmethod
    def get_all_shapes():
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)  # cursore

        query = """ SELECT DISTINCT shape
                    FROM sighting 
                    WHERE shape != "" """  # creo la query -> prendo tutti gli avvistamenti (in ordine crescente in base all'anno)

        cursor.execute(query)

        for row in cursor:
            # creo oggetti "Sights" e li "appendo" nella lista "result"
            result.append(row['shape'])

        cursor.close()  # chiudo il cursore
        conn.close()  # chiudo la connessione
        return result  # restituisco il "result" -> una lista di str "shape"

    @staticmethod
    def get_all_weighted_neigh(year, shape):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)

        query = """ SELECT LEAST(n.state1, n.state2) AS st1,
                           GREATEST(n.state1, n.state2) AS st2,
                           COUNT(*) AS N
                    FROM sighting s, neighbor n
                    WHERE year(s.s_datetime) = %s
                          AND s.shape = %s
                          AND (s.state = n.state1 OR s.state = n.state2)
                    GROUP BY st1, st2 """

        cursor.execute(query, (year, shape))

        for row in cursor:
            result.append((row['st1'], row['st2'], row["N"])) #appendo i due stati e il numero di avvistamenti

        cursor.close()
        conn.close()
        return result