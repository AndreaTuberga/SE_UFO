import flet as ft

class Controller:
    def __init__(self, view, model):
        self._view = view
        self._model = model
        self._list_year = []
        self._list_shape = []

    # ----- metodo per popolare i dropdown -----
    def populate_dd(self):

        # riempio la lista degli AVVISTAMENTI
        sighting_list = self._model.list_sighting

        #riempio la lista con le SHAPES
        self._list_shape =self._model.list_shapes

        # riempio la lista con gli ANNI (non ripetuti)
        for n in sighting_list: #per ogni avvistamento
            if n.s_datetime.year not in self._list_year: #se l'anno non è ancora presente nella lista
                self._list_year.append(n.s_datetime.year) #aggiungo l'anno alla lista

        # popolo dropdown shapes
        for shape in self._list_shape:
            self._view.dd_shape.options.append(ft.dropdown.Option(shape))

        # popolo dropdown years
        for year in self._list_year:
            self._view.dd_year.options.append(ft.dropdown.Option(year))

        self._view.update()

    # ----- handler per gestire creazione del grafo -----
    def handle_graph(self, e):

        # seguono due alternative per gestire le eccezioni
        # versione 1
        try:
            selected_year = int(self._view.dd_year.value) #prendo l'anno selezionato dal dropdown
        except Exception:
            self._view.show_alert("Anno Invalido")
            return
        #versione 2
        selected_shape = self._view.dd_shape.value #prendo la forma selezionata dal dropdown
        if selected_shape is None:
            self._view.show_alert("Forma Invalida")
            return

        #pulisco la view dove stamperò il risultato
        self._view.lista_visualizzazione_1.clean()

        #costruisco il grafo con i parametri selezionati
        self._model.build_graph(selected_shape, selected_year)

        #stampo le informazioni del grafo
        self._view.lista_visualizzazione_1.controls.append(
            ft.Text(
                f"Numero di vertici: {self._model.get_num_of_nodes()} "
                f"Numero di archi: {self._model.get_num_of_edges()}"
            )
        )

        #stampo somma pesi per nodo
        for node_info in self._model.get_sum_weight_per_node():
            self._view.lista_visualizzazione_1.controls.append(
                ft.Text(f"Nodo {node_info[0]}, somma pesi su archi = {node_info[1]}")
            )

        self._view.update()

    # ----- Handler per gestire il problema ricorsivo di ricerca del cammino -----
    def handle_path(self, e):
        self._model.compute_path()

        #pulisce area percorso
        self._view.lista_visualizzazione_2.controls.clear()

        #mostra peso cammino massimo
        self._view.lista_visualizzazione_2.controls.append(
            ft.Text(f"Peso cammino massimo: {self._model.sol_best}")
        )

        #mostra dettagli percorso
        for edge in self._model.path_edge:
            self._view.lista_visualizzazione_2.controls.append(
                ft.Text(
                    f"{edge[0].id} --> {edge[1].id} "
                    f"peso {edge[2]} "
                    f"distanza {self._model.get_distance_weight(edge)}"
                )
            )

        self._view.update()

