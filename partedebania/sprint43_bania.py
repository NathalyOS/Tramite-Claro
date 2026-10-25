import tkinter as tk
from tkinter import ttk, messagebox

class Sprint2App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Trámite Claro - Sprint 2 (Bania)")
        self.geometry("600x650")
        self.configure(bg="#f4f4f4")

        # Datos simulados del trámite
        self.tramite_data = {
            "nombre": "Licencia de Conducir Digital",
            "fuente": "",
            "requisitos": [
                "Identificación oficial (INE)",
                "Comprobante de domicilio (original y copia)",
                "Comprobante de pago de derechos",
                "Fotografía tamaño infantil"
            ],
            "publicado": False
        }

        self.vars_checklist = []
        self.crear_interfaz()

    def crear_interfaz(self):
        # Título principal
        titulo = tk.Label(self, text="Gestor de Trámites - Módulo Bania", font=("Arial", 14, "bold"), bg="#f4f4f4", fg="#001F3F")
        titulo.pack(pady=10)

        # ==========================================
        # HISTORIA 4.1: Verificar fuente oficial
        # ==========================================
        frame_admin = ttk.LabelFrame(self, text=" 4.1 - Administración de Fuente Oficial ")
        frame_admin.pack(fill="x", padx=15, pady=10)

        ttk.Label(frame_admin, text="Enlace o referencia de la fuente oficial:").pack(anchor="w", padx=10, pady=2)
        self.entry_fuente = ttk.Entry(frame_admin, width=65)
        self.entry_fuente.pack(padx=10, pady=5)

        self.btn_publicar = ttk.Button(frame_admin, text="Publicar Trámite", command=self.validar_y_publicar)
        self.btn_publicar.pack(padx=10, pady=8)

        # ==========================================
        # HISTORIA 3.2: Porcentaje de checklist completado
        # ==========================================
        frame_user = ttk.LabelFrame(self, text=" 3.2 - Checklist de Requisitos y Progreso ")
        frame_user.pack(fill="both", expand=True, padx=15, pady=10)

        # Etiqueta de progreso visible
        self.lbl_progreso = ttk.Label(frame_user, text="Progreso: 0%", font=("Arial", 11, "bold"))
        self.lbl_progreso.pack(anchor="w", padx=10, pady=5)

        # Barra de progreso simple
        self.barra_progreso = ttk.Progressbar(frame_user, orient="horizontal", length=540, mode="determinate")
        self.barra_progreso.pack(padx=10, pady=5)

        # Contenedor de checklist
        self.frame_checks = ttk.Frame(frame_user)
        self.frame_checks.pack(fill="both", expand=True, padx=10, pady=5)

        self.cargar_checklist()

        # ==========================================
        # VISTA DE FUENTE PARA EL USUARIO FINAL
        # ==========================================
        self.frame_fuente_vista = ttk.LabelFrame(self, text=" Fuente Oficial Registrada ")
        self.frame_fuente_vista.pack(fill="x", padx=15, pady=10)
        
        self.lbl_fuente_info = ttk.Label(self.frame_fuente_vista, text="Fuente: [Pendiente de publicación]", font=("Arial", 9, "italic"))
        self.lbl_fuente_info.pack(anchor="w", padx=10, pady=8)

    def cargar_checklist(self):
        requisitos = self.tramite_data.get("requisitos", [])

        if not requisitos:
            ttk.Label(self.frame_checks, text="Checklist no disponible / Sin requisitos", foreground="red").pack(anchor="w", pady=5)
            return

        for req in requisitos:
            var = tk.IntVar()
            chk = ttk.Checkbutton(self.frame_checks, text=req, variable=var, command=self.actualizar_progreso)
            chk.pack(anchor="w", pady=3)
            self.vars_checklist.append(var)

        self.actualizar_progreso()

    def actualizar_progreso(self):
        total = len(self.vars_checklist)
        
        if total == 0:
            porcentaje = 0
            self.lbl_progreso.config(text="Progreso: 0%")
            self.barra_progreso['value'] = 0
        else:
            completados = sum(var.get() for var in self.vars_checklist)
            porcentaje = int((completados / total) * 100)
            self.lbl_progreso.config(text=f"Progreso: {porcentaje}%")
            self.barra_progreso['value'] = porcentaje

    def validar_y_publicar(self):
        fuente = self.entry_fuente.get().strip()
        
        # Criterio de aceptación 4.1: Publicar solo si hay al menos 1 fuente[cite: 1]
        if not fuente:
            messagebox.showwarning("Advertencia", "Falta fuente oficial para publicar")[cite: 1]
            return
        
        self.tramite_data["fuente"] = fuente
        self.tramite_data["publicado"] = True
        
        # Actualiza la vista del usuario con la fuente oficial
        self.lbl_fuente_info.config(text=f"Fuente: {fuente}", font=("Arial", 9))
        messagebox.showinfo("Éxito", "Trámite publicado correctamente con su fuente oficial.")[cite: 1]

if __name__ == "__main__":
    app = Sprint2App()
    app.mainloop()