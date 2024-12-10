from collections import deque


class VirtualMachine:
    def __init__(self, instrucciones, tabla_simbolos):
        self.instrucciones = instrucciones
        self.tabla_simbolos = tabla_simbolos
        self.pila = deque()
        self.contador = 0
        self.output = ["Inicio de la Ejecucion"]
        # print(tabla_simbolos)

    def execute(self):
        # Set de instrucciones:
        # stp 		-> fin del programa
        # sto		-> almacenar top en direccion anterior a top
        # read		-> leer valor de variable en top
        # write		-> escribir valor en top
        # fjp label	-> salto a label, solo si top es false
        # upj label	-> salto forzoso a label
        # lab label	-> crear label
        # lda id	-> cargar direccion de identificador
        # lod id	-> cargar valor de id
        # ldc const	-> cargar constante
        # and		->
        # or		->
        # lt		-> menor
        # leq		-> menor igual
        # gt		-> mayor
        # geq		-> mayor igual
        # neq		-> diferente
        # eql		-> igual
        # add		->
        # sub		->
        # mul		->
        # div		->
        # mod		->
        # pow		->
        inst = self.instrucciones[self.contador]

        # Usar while o llamadas a la funcion por cada caso?
        # No, se debe usar un ciclo para asi retornar el status, salida y/o variable por leer
        # self.instrucciones[self.contador]
        # while inst != "stp":
        while True:
            # print(inst)
            if inst == "stp":
                self.output.append("Fin de la ejecucion")
                return {"status": "END", "output": self.output}
            elif inst == "sto":
                valor = self.pila.pop()
                variable = self.pila.pop()
                # print(f'{variable}={valor}')
                # cast al tipo de dato si es necesario
                self.tabla_simbolos[variable]["value"] = valor
            elif inst == "read":
                variable = self.pila.pop()
                variable_type = self.get_variable_type(variable)
                self.output.append(
                    f"Ingresa {variable_type} para la variable {variable}:"
                )
                return {
                    "status": "INPUT",
                    "output": self.output,
                    "variable": {"name": variable, "type": variable_type},
                }
            elif inst == "write":
                valor = self.pila.pop()
                self.output.append(valor)
            elif inst.startswith("fjp"):
                _, label = inst.split()
                valor = self.pila.pop()
                if not valor:
                    index = self.get_label_index(f"lab {label}")
                    self.contador = index
                    # Asi evitamos el caso inecesario en el que se evalua un label
                    # inst = self.instrucciones[index]
                    # continue
            elif inst.startswith("upj"):
                _, label = inst.split()
                index = self.get_label_index(f"lab {label}")
                self.contador = index
                # Asi evitamos el caso inecesario en el que se evalua un label
                # inst = self.instrucciones[index]
                # continue
            elif inst.startswith("lda"):
                _, variable = inst.split()
                self.pila.append(variable)
            elif inst.startswith("lod"):
                _, variable = inst.split()
                valor = self.get_variable_value(variable)
                self.pila.append(valor)
            elif inst.startswith("ldc"):
                _, constante = inst.split()
                valor = float(constante)
                if valor.is_integer():
                    valor = int(valor)
                self.pila.append(valor)
            elif inst == "and":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2 and valor1)
            elif inst == "or":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2 or valor1)
            elif inst == "lt":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2 < valor1)
            elif inst == "leq":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2 <= valor1)
            elif inst == "gt":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2 > valor1)
            elif inst == "geq":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2 >= valor1)
            elif inst == "neq":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2 != valor1)
            elif inst == "eql":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2 == valor1)
            elif inst == "add":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2 + valor1)
            elif inst == "sub":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2 - valor1)
            elif inst == "mul":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2 * valor1)
            elif inst == "div":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2 / valor1)
            elif inst == "mod":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2 % valor1)
            elif inst == "pow":
                valor1 = self.pila.pop()
                valor2 = self.pila.pop()
                self.pila.append(valor2**valor1)

            self.contador += 1
            inst = self.instrucciones[self.contador]

        # return {status: "END", output: self.output}

    def set_variable_value(self, variable, valor):
        self.tabla_simbolos[variable]["value"] = valor
        self.output.append(valor)
        self.contador += 1
        pass

    def get_variable_type(self, variable):
        return self.tabla_simbolos[variable]["type"]

    def get_variable_value(self, variable):
        return self.tabla_simbolos[variable]["value"]

    def get_label_index(self, label):
        if label in self.instrucciones:
            return self.instrucciones.index(label)
        return 0
