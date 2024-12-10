import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from tokens import tokens
from colores_token import colores
import lexico
from sintactico import AnalizadorSintactico
from semantico import AnalizadorSemantico
from codigo_intermedio import GeneradorCodigoIntermedio
import subprocess
import threading

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    ruta_archivo = ""
    nombre_archivo = "untitled"
    icons = ["open_file.png","close_file.png","new_file.png","save_file.png","save_as_file.png","build.png","run.png"]
    icons_dirname = "icons"
    icon_images = []
    analisis_lexico = []
    comentarios = []
    errores = []
    editor_font_size = 15
    
    # Estado del archivo:
    # 0 - nuevo
    # 1 - editado
    # 2 - guardado
    estado_archivo = 0
    saltar_advertencia = False
    
    arbol_sintactico = None
    
    
    # Analisis semantico
    arbol_sintactico_anotado = None
    tabla_simbolos = None
    errores_semanticos = None
    
    # Generacion de codigo
    instrucciones = []
    
    
    def __init__(self):
        super().__init__()

        # Configuracion de la ventana principal
        self.title("Super IDE")
        self.geometry(f"{1100}x{580}")
        
        # Intercambir las dos siguientes lineas para regresar al estado anterior del IDE
        # self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure((0,1), weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Menu
        # Frame del menu
        self.menu_frame = ctk.CTkFrame(self, corner_radius=0)
        self.menu_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        
        # Logo
        self.logo_label = ctk.CTkLabel(self.menu_frame, text="Super IDE", font=ctk.CTkFont(size=20, weight="bold"), height=30)
        self.logo_label.grid(row=0, column=0, padx=(20,5), pady=10)
        
        # Nombre del archivo
        self.archivo_label = ctk.CTkTextbox(self.menu_frame, height=36)
        self.archivo_label.grid(row=0, column=1, padx=5, pady=10)
        self.archivo_label.insert("0.0", "untitled")
        self.archivo_label.configure(state="disabled")
        
        # Selector de operaciones del archivo
        self.menu_archivo = ctk.CTkOptionMenu(self.menu_frame, dynamic_resizing=False,values=["Abrir", "Cerrar", "Nuevo", "Guardar", "Guardar como"], command=self.operacion_archivo, height=36)
        self.menu_archivo.grid(row=0, column=2, padx=5, pady=10)
        
        for i in range(0, len(self.icons)):
            absolute_path = os.path.abspath(os.path.join(self.icons_dirname, self.icons[i]))
            image = ctk.CTkImage(light_image=Image.open(absolute_path),dark_image=Image.open(absolute_path), size=(30, 30))
            self.icon_images.append(image)
        
        # Botones para operaciones sobre archivos
        self.open_file_button = ctk.CTkButton(self.menu_frame, text=None, image=self.icon_images[0], width=40, command= lambda: self.operacion_archivo(operacion="Abrir"))
        self.open_file_button.grid(row=0, column=3, padx=5, pady=10)
        self.close_file_button = ctk.CTkButton(self.menu_frame, text=None, image=self.icon_images[1], width=40, command= lambda: self.operacion_archivo(operacion="Cerrar"))
        self.close_file_button.grid(row=0, column=4, padx=5, pady=10)
        self.new_file_button = ctk.CTkButton(self.menu_frame, text=None, image=self.icon_images[2], width=40, command= lambda: self.operacion_archivo(operacion="Nuevo"))
        self.new_file_button.grid(row=0, column=5, padx=5, pady=10)
        self.save_file_button = ctk.CTkButton(self.menu_frame, text=None, image=self.icon_images[3], width=40, command= lambda: self.operacion_archivo(operacion="Guardar"))
        self.save_file_button.grid(row=0, column=6, padx=5, pady=10)
        self.save_as_file_button = ctk.CTkButton(self.menu_frame, text=None, image=self.icon_images[4],width=40, command= lambda: self.operacion_archivo(operacion="Guardar como"))
        self.save_as_file_button.grid(row=0, column=7, padx=5, pady=10)
        
        # Botones compilar y ejecutar
        self.build_button = ctk.CTkButton(self.menu_frame, text=None, image=self.icon_images[5], width=40, command=self.build_file)
        self.build_button.grid(row=0, column=8, padx=5, pady=10)
        self.run_button = ctk.CTkButton(self.menu_frame, text=None, image=self.icon_images[6], width=40, command=self.run_file)
        self.run_button.grid(row=0, column=9, padx=5, pady=10)
        
        # Editor de Codigo
        # Frame del Editor
        self.editor_frame = ctk.CTkFrame(self, corner_radius=0)
        self.editor_frame.grid(row=1, column=0, sticky="nsew")
        self.editor_frame.grid_rowconfigure(0, weight=1)
        self.editor_frame.grid_columnconfigure(1, weight=1)
        
        # Textbox para numero de linea
        self.line_textbox = ctk.CTkTextbox(self.editor_frame, width=50, wrap='word', activate_scrollbars=False,state="disabled",font=("TkDefaultFont", 15))
        self.line_textbox.grid(row=0, column=0, padx=(20,0), pady=(10,20), sticky="nsew")
        
        # Textbox para editor de codigo
        self.code_textbox = ctk.CTkTextbox(self.editor_frame, wrap='none', activate_scrollbars=False,font=("TkDefaultFont", 15), text_color="black")
        self.code_textbox.grid(row=0, column=1, padx=(10,10), pady=(10,20), sticky="nsew")
        self.code_textbox.configure(yscrollcommand=self.on_scroll)
        self.code_textbox.bind('<KeyRelease>', self.on_key_release)
        self.code_textbox.bind('<ButtonRelease-1>', self.on_click)
        self.code_textbox.bind('<Control-plus>', self.aumentar_fuente)
        self.code_textbox.bind('<Control-minus>', self.disminuir_fuente)
        
        # Outputs para analizadores, errores y ejecucion
        # Frame
        self.output_frame = ctk.CTkFrame(self, corner_radius=0)
        self.output_frame.grid(row=1, column=1, sticky="nsew")
        self.output_frame.grid_rowconfigure((0,1), weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)
        
        # Tabview de analizadores ...
        self.analisis_tabview = ctk.CTkTabview(self.output_frame, width=500)
        self.analisis_tabview.grid(row=0, column=0, padx=(10, 20), pady=0, sticky="nsew")
        self.analisis_tabview.add("Lexico")
        self.analisis_tabview.add("Sintactico")
        self.analisis_tabview.add("Semantico")
        self.analisis_tabview.add("T. Simbolos")
        self.analisis_tabview.add("C. Intermedio")
        self.analisis_tabview.add("Ejecucion")
        
        # Textbox de salida para Analisis Lexico
        self.analisis_tabview.tab("Lexico").grid_columnconfigure(0, weight=1)
        self.analisis_tabview.tab("Lexico").grid_rowconfigure(1, weight=1)
        
        self.lexico_tab = ctk.CTkTextbox(self.analisis_tabview.tab("Lexico"), wrap='none')
        self.lexico_tab.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        self.lexico_tab.configure(state="disabled")
        
        for i in range(0, len(tokens)):
            self.lexico_tab.tag_config(tokens[i], foreground=colores[i])
        
        # Textbox de salida para Analisis Sintactico
        self.analisis_tabview.tab("Sintactico").grid_columnconfigure(0, weight=1)
        self.analisis_tabview.tab("Sintactico").grid_rowconfigure(0, weight=1)
        self.tree_button = ctk.CTkButton(self.analisis_tabview.tab("Sintactico"), text='Mostrar Arbol Sintactico', width=40, command= lambda: self.mostrar_analisis_sintactico())
        self.tree_button.grid(row=0, column=0, padx=5, pady=10)
        
        # Textbox de salida para Analisis Semantico
        self.analisis_tabview.tab("Semantico").grid_columnconfigure(0, weight=1)
        self.analisis_tabview.tab("Semantico").grid_rowconfigure(0, weight=1)
        self.anotations_tree_button = ctk.CTkButton(self.analisis_tabview.tab("Semantico"), text='Mostrar Arbol Sintactico con Anotaciones', width=40, command= lambda: self.mostrar_analisis_semantico())
        self.anotations_tree_button.grid(row=0, column=0, padx=5, pady=10)
        
        # Textbox de salida para Codigo Intermedio
        self.analisis_tabview.tab("C. Intermedio").grid_columnconfigure(0, weight=1)
        self.analisis_tabview.tab("C. Intermedio").grid_rowconfigure(0, weight=1)
        self.cod_int_tab = ctk.CTkTextbox(self.analisis_tabview.tab("C. Intermedio"), wrap='word')
        self.cod_int_tab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.cod_int_tab.configure(state="disabled")
        
        # Textbox de salida para Tabla de Simbolos
        self.analisis_tabview.tab("T. Simbolos").grid_columnconfigure(0, weight=1)
        self.analisis_tabview.tab("T. Simbolos").grid_rowconfigure(1, weight=1)
        self.tabla_simb_tab = ctk.CTkTextbox(self.analisis_tabview.tab("T. Simbolos"), wrap='none')
        self.tabla_simb_tab.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        self.tabla_simb_tab.configure(state="disabled")
        
        # Textbox de salida para la Ejecucion
        self.analisis_tabview.tab("Ejecucion").grid_columnconfigure(0, weight=1)
        self.analisis_tabview.tab("Ejecucion").grid_rowconfigure(0, weight=1)
        self.ejecucion_tab = ctk.CTkTextbox(self.analisis_tabview.tab("Ejecucion"), wrap='word')
        self.ejecucion_tab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.ejecucion_tab.insert("end", ">>> Inicio de la Ejecucion <<<\n")
        self.ejecucion_tab.configure(state="disabled")
        
        # Widget para ingresar comandos
        self.input = ctk.CTkEntry(self.analisis_tabview.tab("Ejecucion"), placeholder_text="Ingresa el numero aqui ...")
        self.input.grid(row=1, column=0, padx=0, pady=5, sticky="nsew")
        self.input.bind("<Return>", self.send_command)
        
        # Tabview Errores
        self.err_run_tabview = ctk.CTkTabview(self.output_frame, width=500)
        self.err_run_tabview.grid(row=1, column=0, padx=(10, 20), pady=(10, 0), sticky="nsew")
        self.err_run_tabview.add("Errores") 
        
        # Textbox de salida para Ejecucion
        self.err_run_tabview.tab("Errores").grid_columnconfigure(0, weight=1)
        self.err_run_tabview.tab("Errores").grid_rowconfigure(0, weight=1)
        self.errores_tab = ctk.CTkTextbox(self.err_run_tabview.tab("Errores"), wrap='word')
        self.errores_tab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.errores_tab.configure(state="disabled")
        
        # Indicador linea y columna del cursor en archivo
        # Label line-col
        self.line_col_label = ctk.CTkTextbox(self.output_frame, height=20)
        self.line_col_label.grid(row=2, column=0, padx=(10,20), pady=(20,20), sticky="ew")
        self.line_col_label.insert("0.0", "Ln 1, Col 1")
        self.line_col_label.configure(state="disabled")

    def operacion_archivo(self, operacion: str):
        # Transiscion entre estados del archivo
        #           Nuevo   Abrir   Cerrar  Guardar Guardar como
        # Nuevo     O       O       O       O       O
        # Editado   X       X       X       O       O
        # Guardado  O       O       O       O       O
        matriz = [[True, True, True, False, True],
                  [False, False, False, True, False],
                  [True, True, True, True, True]]

        if operacion == "Nuevo":
            if matriz[self.estado_archivo][0]:
                self.nuevo_archivo(self)
            else:
                self.adv_op = operacion
                self.generar_confirmacion(self)
        elif operacion == "Abrir":
            if matriz[self.estado_archivo][1]:
                self.abrir_archivo(self)
            else:
                self.adv_op = operacion
                self.generar_confirmacion(self)
        elif operacion == "Cerrar":
            if matriz[self.estado_archivo][2]:
                self.cerrar_archivo(self)
            else:
                self.adv_op = operacion
                self.generar_confirmacion(self)
        elif operacion == "Guardar":
            if matriz[0][3]:
                self.guardar_como_archivo(self)
            elif matriz[1][3]:
                if self.ruta_archivo != "":
                    self.guardar_archivo(self)
                else:
                    self.guardar_como_archivo(self)
            elif matriz[2][3]:
                self.guardar_archivo(self)
        elif operacion == "Guardar como":
            self.guardar_como_archivo(self)
            
        self.menu_archivo.set("Abrir")
        self.enlazar_scroll()
        self.actualizar_posicion_cursor()
    
    # Operaciones de archivos
    def nuevo_archivo(self, *args):
        self.code_textbox.delete("1.0", tk.END)
        self.estado_archivo = 0
        self.nombre_archivo = "untitled"
        self.ruta_archivo = ""
        self.title(self.nombre_archivo)
        self.actualizar_archivo_label()
        self.actualizar_lineas()
        self.actualizar_posicion_cursor()
    
    def cerrar_archivo(self, *args):
        self.code_textbox.delete("1.0", tk.END)
        self.ruta_archivo = ""
        self.title("Super IDE")
        self.estado_archivo = 0
        self.nombre_archivo = "untitled"
        self.actualizar_archivo_label()
        self.actualizar_lineas()
        self.actualizar_posicion_cursor()

    def abrir_archivo(self, *args):
        self.ruta_archivo = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])

        if self.ruta_archivo:
            with open(self.ruta_archivo, 'r') as file:
                content = file.read()
                self.code_textbox.delete("1.0", tk.END)
                self.code_textbox.insert(tk.END, content)
                
            self.title(self.ruta_archivo)
            self.estado_archivo = 2
            self.nombre_archivo = os.path.basename(self.ruta_archivo)
            self.actualizar_archivo_label()
            self.actualizar_lineas()
            self.actualizar_posicion_cursor()
            self.analizar_lexico(self)

    def guardar_archivo(self, *args):
        if self.ruta_archivo:
            with open(self.ruta_archivo, 'w') as file:
                content = self.code_textbox.get("1.0", tk.END)
                file.write(content)
            self.estado_archivo = 2
            self.title(self.ruta_archivo)
            self.actualizar_archivo_label()

    def guardar_como_archivo(self, *args):
        nueva_ruta_archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if nueva_ruta_archivo:
            with open(nueva_ruta_archivo, 'w') as file:
                content = self.code_textbox.get("1.0", tk.END)
                file.write(content)
            self.estado_archivo = 2
            self.title(nueva_ruta_archivo)
            self.ruta_archivo = nueva_ruta_archivo
            self.nombre_archivo = os.path.basename(self.ruta_archivo)
            self.actualizar_archivo_label()
    
    # Eventos
    def on_scroll(self, *args):
        self.enlazar_scroll()

    def on_key_release(self, *args):
        self.enlazar_scroll()
        self.actualizar_posicion_cursor()
        self.estado_archivo = 1
        if self.ruta_archivo == "":
            self.title(f"{self.nombre_archivo} *")
        else:
            self.title(f"{self.ruta_archivo} *")
        
        self.actualizar_archivo_label()
        self.analizar_lexico_lite(self)

    def on_click(self, *args):
        self.actualizar_posicion_cursor()
    
    def aumentar_fuente(self, event):
        if self.editor_font_size < 16:
            self.editor_font_size += 1
            self.code_textbox.configure(font=("TkDefaultFont", self.editor_font_size))
            self.line_textbox.configure(font=("TkDefaultFont", self.editor_font_size))

    def disminuir_fuente(self, event):
        if self.editor_font_size > 10:
            self.editor_font_size -= 1
            self.code_textbox.configure(font=("TkDefaultFont", self.editor_font_size))
            self.line_textbox.configure(font=("TkDefaultFont", self.editor_font_size))
    
    # Acciones a eventos
    def enlazar_scroll(self, *args):
        primera_posicion, *_ = self.code_textbox.yview()
        self.actualizar_lineas()
        self.line_textbox.yview_moveto(primera_posicion)
    
    def actualizar_lineas(self, *args):
        self.line_textbox.configure(state="normal")
        self.line_textbox.delete("0.0", "end")
        contenido = self.code_textbox.get("1.0", tk.END)
        
        # Contar el número de líneas divididas por el salto de línea
        n = len(contenido.split('\n')) - 1
        
        for i in range(1, n + 1):
            if i < n:
                self.line_textbox.insert(tk.END, f"{i}\n")
            else:
                self.line_textbox.insert(tk.END, f"{i}")
        
        self.line_textbox.configure(state="disabled")

    def actualizar_posicion_cursor(self, *args):
        # Obtiene la posición del cursor
        cursor_pos = self.code_textbox.index(ctk.INSERT)
        
        # Extrae la parte antes del "." para obtener el número de línea
        linea = cursor_pos.split('.')[0]
        col = int(cursor_pos.split('.')[1]) + 1
        
        # Actualiza la etiqueta con la información de la línea actual
        self.line_col_label.configure(state="normal")
        self.line_col_label.delete("0.0", "end")
        self.line_col_label.insert("0.0", f"Ln {linea}, Col {col}")
        self.line_col_label.configure(state="disabled")
    
    def actualizar_archivo_label(self, *args):
        self.archivo_label.configure(state="normal")
        self.archivo_label.delete("0.0", "end")
        
        if self.estado_archivo == 1:
            self.archivo_label.insert("0.0", f"{self.nombre_archivo} *")
        else:
            self.archivo_label.insert("0.0", f"{self.nombre_archivo}")
        
        self.archivo_label.configure(state="disabled")
    
    def generar_confirmacion(self, *args):
        # Crear la ventana de advertencia
        self.ventana_advertencia = ctk.CTkToplevel(self)
        self.ventana_advertencia.title("Super IDE")

        # Agregar el mensaje de advertencia
        mensaje = ctk.CTkLabel(self.ventana_advertencia, text="¿Deseas guardar tus cambios?\nTus cambios se perderan si no los guardas",font=("Arial", 15))
        mensaje.grid(row=0, column=0, padx=5, pady=10, columnspan=3)

        # Agregar el botón de aceptar
        boton_guardar = ctk.CTkButton(self.ventana_advertencia, text="Guardar",command=lambda: self.get_resultado_advertencia(self, "SI"))
        boton_guardar.grid(row=1, column=0, padx=5, pady=10)

        # Agregar el botón de cancelar
        boton_cancelar = ctk.CTkButton(self.ventana_advertencia, text="Cancelar",command=lambda: self.get_resultado_advertencia(self, "CANCELAR"))
        boton_cancelar.grid(row=1, column=1, padx=5, pady=10)

        boton_no_guardar = ctk.CTkButton(self.ventana_advertencia, text="No guardar",command=lambda: self.get_resultado_advertencia(self, "NO"))
        boton_no_guardar.grid(row=1, column=2, padx=5, pady=10)
    
    def get_resultado_advertencia(self, *args):
        self.ventana_advertencia.destroy()
        extra, resultado, *_ = args
        
        if resultado == "SI":
            # si no hay ruta guardar como, si la hay guardar
            if self.ruta_archivo != "":
                self.guardar_archivo(self)
            else:
                self.guardar_como_archivo(self)
        
        if resultado != "CANCELAR":
            if self.adv_op == "Abrir":
                self.abrir_archivo(self)
            elif self.adv_op == "Nuevo":
                self.nuevo_archivo(self)
            elif self.adv_op == "Cerrar":
                self.cerrar_archivo(self)

    def build_file(self, *args):
        self.operacion_archivo('Guardar')
        self.analizar_lexico(self)
        n_errores = self.analizar_sintactico(self) + len(self.errores)
        if n_errores == 0:
            n_errores = self.analizar_semantica(self)
        
        if n_errores == 0:
            self.generar_codigo_intermedio(self)
    
    def run_file(self, *args):
        self.build_file(self)
        
        # Ciclo de ejecucion de la VM
        # Caso simple: sin lectura de varibles
        #   vm.execute = output -> ide
        # Caso complejo: con lectura de varibles
        #   vm.output => ide
        #   vm.input  <= ide
        #   vm.output => ide
        
    def analizar_lexico(self, *args):
        codigo = self.code_textbox.get("1.0","end-1c")
        self.analisis_lexico, self.errores, self.comentarios = lexico.ejecutar_lexico(codigo)
        self.mostrar_analisis_lexico(self)
        self.style_code(self)
    
    # Analizador lexico usado al dar color a los tokens
    def analizar_lexico_lite(self, *args):
        codigo = self.code_textbox.get("1.0","end-1c")
        self.analisis_lexico, _, self.comentarios = lexico.analizador_lexico(codigo)
        for token in tokens:
            self.code_textbox.tag_delete(token)
        
        self.code_textbox.tag_delete('L')
        self.code_textbox.tag_delete('M')
        self.style_code(self)
    
    def mostrar_analisis_lexico(self, *args):
        self.lexico_tab.configure(state="normal")
        self.lexico_tab.delete("0.0", "end")
        self.lexico_tab.insert("end", "LEXEMA\t\tTOKEN\t\t\tSUBTOKEN\t\t\tFILA\tCOL_I\tCOL_F\n")
        for lexema in self.analisis_lexico:
            token = tokens.index(lexema[1])
            self.lexico_tab.insert("end", f"{lexema[0]}\t\t{lexema[1]}\t\t\t{lexema[2]}\t\t\t{lexema[3]}\t{lexema[4]}\t{lexema[5]}\n",
                                    (lexema[1],colores[token]))
        self.lexico_tab.configure(state="disabled")
        
        self.errores_tab.configure(state="normal")
        self.errores_tab.delete("0.0", "end")
        for error in self.errores:
            self.errores_tab.insert("end", f"{error}\n")
        self.errores_tab.configure(state="disabled")
    
    def style_code(self, *args):
        for lexema in self.analisis_lexico:
            token = tokens.index(lexema[1])
            start_index = f"{lexema[3]}.{int(lexema[4])-1}"
            end_index = f"{lexema[3]}.{int(lexema[5])-1}"
            self.code_textbox.tag_add(lexema[1], start_index, end_index)
            self.code_textbox.tag_config(lexema[1], foreground=colores[token])
            
        for comentario in self.comentarios:
            start_index = f"{comentario[1]}.{int(comentario[3])-1}"
            end_index = f"{comentario[2]}.{int(comentario[4])-1}"
            self.code_textbox.tag_add(comentario[0], start_index, end_index)
            self.code_textbox.tag_config(comentario[0], foreground=colores[10])
    
    def borrar_tags(self,*args):
        for token in tokens:
            self.code_textbox.tag_delete(token)
        
        self.code_textbox.tag_delete('L')
        self.code_textbox.tag_delete('M')

    def analizar_sintactico(self, *args):
        parser = AnalizadorSintactico(self.analisis_lexico)
        self.arbol_sintactico = parser.analisis_sintactico()
        if self.arbol_sintactico != None:
            parser.tree_to_json(self.arbol_sintactico)
        errores = parser.get_errores()
        self.errores_tab.configure(state="normal")
        for error in errores:
            self.errores_tab.insert("end", error)
        self.errores_tab.configure(state="disabled")
        return len(errores)
    
    def mostrar_analisis_sintactico(self, *args):
        self.errores_tab.configure(state="normal")
        # Analizar la existencia de los archivos necesarios: 
        if os.path.exists(os.path.join('analisis_sintactico','tree.json')):
            if os.path.exists('Tree.class'):
                # Compilar Tree.java: javac -cp json-20240303.jar Tree.java
                if os.path.exists('json-20240303.jar'):
                    subproceso_java = threading.Thread(target=self.arbol_sintactico_window)
                    # Iniciar el subproceso
                    subproceso_java.start()
                    
                else:
                    self.errores_tab.insert("end", f"No existe el archivo {'json-20240303.jar'}\n")
            else:
                self.errores_tab.insert("end", f"No existe el archivo {'Tree.class'}\n")
        else:
            self.errores_tab.insert("end", f"No existe el archivo {os.path.join('analisis_sintactico','tree.json')}\n")
        
        self.errores_tab.configure(state="disabled")
    
    def arbol_sintactico_window(self, *args):
        if os.name == 'posix':
            subprocess.run(["java", "-cp",".:json-20240303.jar","Tree"])
        elif os.name == 'nt':
            subprocess.run(["java", "-cp",".;json-20240303.jar","Tree"])
    
    def analizar_semantica(self, *args):
        analizador_semantico = AnalizadorSemantico(self.arbol_sintactico)
        self.arbol_sintactico_anotado, self.tabla_simbolos, errores = analizador_semantico.analisis_semantico()
        if self.arbol_sintactico_anotado is not None:
            analizador_semantico.tree_to_json(self.arbol_sintactico_anotado)
        
        self.tabla_simb_tab.configure(state="normal")
        self.tabla_simb_tab.delete("0.0", "end")
        self.tabla_simb_tab.insert("end", "Variable\tTipo\tValor\tLOC\tLineas\n")
        for key, data in self.tabla_simbolos.items():
            self.tabla_simb_tab.insert("end", f"{key}\t{data['type']}\t{data['value']}\t{data['loc']}\t{data['lines']}\n")
        self.tabla_simb_tab.configure(state="disabled")
        
        self.errores_tab.configure(state="normal")
        for error in errores:
            self.errores_tab.insert("end", error)
            self.errores_tab.insert("end", '\n')
        self.errores_tab.configure(state="disabled")
        return len(errores)
       
    def mostrar_analisis_semantico(self, *args):
        self.errores_tab.configure(state="normal")
        # Analizar la existencia de los archivos necesarios: 
        if os.path.exists(os.path.join('analisis_semantico','tree.json')):
            if os.path.exists('Tree.class'):
                # Compilar Tree.java: javac -cp json-20240303.jar Tree.java
                if os.path.exists('json-20240303.jar'):
                    subproceso_java = threading.Thread(target=self.arbol_sintactico_anotado_window)
                    # Iniciar el subproceso
                    subproceso_java.start()
                    
                else:
                    self.errores_tab.insert("end", f"No existe el archivo {'json-20240303.jar'}\n")
            else:
                self.errores_tab.insert("end", f"No existe el archivo {'Tree.class'}\n")
        else:
            self.errores_tab.insert("end", f"No existe el archivo {os.path.join('analisis_semantico','tree.json')}\n")
        
        self.errores_tab.configure(state="disabled")
    
    def arbol_sintactico_anotado_window(self, *args):
        if os.name == 'posix':
            subprocess.run(["java", "-cp",".:json-20240303.jar","Tree", "true"])
        elif os.name == 'nt':
            subprocess.run(["java", "-cp",".;json-20240303.jar","Tree", "true"])
    
    def generar_codigo_intermedio(self, *args):
        generador_codigo = GeneradorCodigoIntermedio(self.arbol_sintactico_anotado)
        self.instrucciones = generador_codigo.generar_codigo_intermedio()
        self.mostrar_codigo_intermedio(self)
    
    def mostrar_codigo_intermedio(self, *args):
        self.cod_int_tab.configure(state="normal")
        self.cod_int_tab.delete("0.0", "end")
        for instruccion in self.instrucciones:
            self.cod_int_tab.insert("end", f'{instruccion};\n')
        self.cod_int_tab.configure(state="disabled")
    
    def enviar_input(self, event=None):
        valor = self.input.get()
        print(valor)
        self.input.delete(0, "end")  # Limpia el campo de entrada
        # self.input.configure(state="disabled")
    
    def send_command(self, *args):
        self.enviar_input()
    
if __name__ == "__main__":
    app = App()
    app.mainloop()
