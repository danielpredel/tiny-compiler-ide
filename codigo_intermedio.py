from node import Node


class GeneradorCodigoIntermedio:
    def __init__(self, arbol_semantico: Node) -> None:
        self.arbol_semantico = arbol_semantico
        self.instrucciones = []
        self.label_count = 1

    def generar_codigo_intermedio(self):
        if self.arbol_semantico is not None:
            self.recorrer_arbol(self.arbol_semantico)

        self.instrucciones.append("stp")
        return self.instrucciones

    def recorrer_arbol(self, nodo: Node):
        if nodo.node_kind[1] == "MAIN":
            self.generar_main(nodo)
        elif nodo.node_kind[1] == "SELECCION":
            self.generar_seleccion(nodo)
        elif nodo.node_kind[1] == "ITERACION":
            self.generar_iteracion(nodo)
        elif nodo.node_kind[1] == "REPETICION":
            self.generar_repeticion(nodo)
        elif nodo.node_kind[1] == "IN":
            self.generar_in(nodo)
        elif nodo.node_kind[1] == "OUT":
            self.generar_out(nodo)
        elif nodo.node_kind[1] == "ASIGNACION":
            self.generar_asignacion(nodo)
        elif nodo.node_kind[1] == "OPERADOR":
            self.generar_operador(nodo)
        elif nodo.node_kind[1] == "CONSTANTE":
            self.generar_constante(nodo)
        elif nodo.node_kind[1] == "IDENTIFICADOR":
            self.generar_identificador(nodo)

    def generar_main(self, nodo: Node):
        if nodo.child[0] != None:
            # Generar primer sentencia
            self.recorrer_arbol(nodo.child[0])

        for sibling in nodo.siblings:
            # Generar el resto de las sentencias
            self.recorrer_arbol(sibling)

    def generar_seleccion(self, nodo: Node):
        # Generar condicion
        self.recorrer_arbol(nodo.child[0])

        label_1 = f"L{self.label_count}"
        self.label_count += 1

        # Salto a false
        self.instrucciones.append(f"fjp {label_1}")

        # Si el bloque then tiene sentencias
        # Generar bloque then (true)
        if nodo.child[1] != None:
            self.recorrer_arbol(nodo.child[1])

        # Si existe bloque else
        # Generar bloque else (false)
        if nodo.child[2] != None:
            label_2 = f"L{self.label_count}"
            self.label_count += 1

            # Evitar bloque else
            self.instrucciones.append(f"upj {label_2}")

            # Establecer label bloque else
            self.instrucciones.append(f"lab {label_1}")

            # Generar bloque else
            self.recorrer_arbol(nodo.child[2])

            # Establecer label final
            self.instrucciones.append(f"lab {label_2}")
        else:
            # Establecer label final
            self.instrucciones.append(f"lab {label_1}")

    def generar_iteracion(self, nodo: Node):
        label_1 = f"L{self.label_count}"
        self.label_count += 1

        # Establecer label de inicio
        self.instrucciones.append(f"lab {label_1}")

        # Generar condicion
        self.recorrer_arbol(nodo.child[0])

        label_2 = f"L{self.label_count}"
        self.label_count += 1

        # Establecer salto a false
        self.instrucciones.append(f"fjp {label_2}")

		# Si existen sentencias
        # Generar bloque true
        if nodo.child[1] != None:
            self.recorrer_arbol(nodo.child[1])

        # Establecer salto al inicio
        self.instrucciones.append(f"upj {label_1}")

        # Establecer label final
        self.instrucciones.append(f"lab {label_2}")

    def generar_repeticion(self, nodo: Node):
        label_1 = f"L{self.label_count}"
        self.label_count += 1

        # Establecer label de inicio
        self.instrucciones.append(f"lab {label_1}")

		# Si existen sentencias
        # Generar bloque true
        if nodo.child[0] != None:
            self.recorrer_arbol(nodo.child[0])

        # Generar condicion
        self.recorrer_arbol(nodo.child[1])

        label_2 = f"L{self.label_count}"
        self.label_count += 1

        # Establecer salto a false
        self.instrucciones.append(f"fjp {label_2}")

        # Establecer salto al inicio
        self.instrucciones.append(f"upj {label_1}")

        # Establecer label final
        self.instrucciones.append(f"lab {label_2}")

    def generar_in(self, nodo: Node):
        # Cargar direccion del identificador
        self.instrucciones.append(f"lda {nodo.child[0].name}")

        # Leer valor
        self.instrucciones.append("read")

    def generar_out(self, nodo: Node):
        # Generar expresion
        self.recorrer_arbol(nodo.child[0])

        # Escribir valor
        self.instrucciones.append("write")

    def generar_asignacion(self, nodo: Node):
        # Cargar direccion del identificador
        self.instrucciones.append(f"lda {nodo.child[0].name}")

        # Generar expresion
        self.recorrer_arbol(nodo.child[1])
        
        # Almacenar tope en direccion anterior
        self.instrucciones.append('sto')

    def generar_operador(self, nodo: Node):
        operador = nodo.op

        # Generar operaciones logicas
        if operador == "AND":
            self.instrucciones.append("and")
        elif operador == "OR":
            self.instrucciones.append("or")

        # Generar operaciones relacionales
        elif operador == "MENOR":
            self.instrucciones.append("lt")
        elif operador == "MENOR_IGUAL":
            self.instrucciones.append("leq")
        elif operador == "MAYOR":
            self.instrucciones.append("gt")
        elif operador == "MAYOR_IGUAL":
            self.instrucciones.append("geq")
        elif operador == "DIFERENTE":
            self.instrucciones.append("neq")
        elif operador == "IGUAL":
            self.instrucciones.append("eql")

        # Generar operaciones aritmeticas
        elif operador == "SUMA":
            self.instrucciones.append("add")
        elif operador == "RESTA":
            self.instrucciones.append("sub")
        elif operador == "MULTIPLICACION":
            self.instrucciones.append("mul")
        elif operador == "DIVISION":
            self.instrucciones.append("div")
        elif operador == "MODULO":
            self.instrucciones.append("mod")
        elif operador == "POTENCIA":
            self.instrucciones.append("pow")

    def generar_constante(self, nodo: Node):
        # Cargar constante
        self.instrucciones.append(f"ldc {nodo.val}")

    def generar_identificador(self, nodo: Node):
        # Cargar valor de variable
        self.instrucciones.append(f"lod {nodo.name}")
