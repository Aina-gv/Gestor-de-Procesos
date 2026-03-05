# Librerías
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import List, Tuple, Dict

# ========================
# 1. ESTRUCTURAS DE DATOS 
# ========================

@dataclass 
class Process:
	pid: str
	name: str
	arrival: int
	burst: int
	pages: int

# =========================
# 2. LÓGICA DE SIMULACIÓN
# =========================

def simple_memory_simulation(processes: List[Process], total_pages: int, algo_type: str, quantum: int = 0):
	"""
	Simulación genérica que maneja Admisión de Memoria + Planificación de CPU.
	"""
	time = 0
	completed = 0
	n = len(processes)
	
	# Info tracking
	p_info = {p.pid: {
		"process": p,
		"remaining": p.burst, # Tiempo restante de CPU
		"state": "NEW", # NEW, READY, RUNNING, TERMINATED
		"arrival": p.arrival,
		"start_time": None,
		"finish_time": 0
	} for p in processes}
	
	ready_queue = [] # Cola de procesos listos para CPU
	job_queue = sorted(processes, key=lambda x: x.arrival)  # Cola de trabajos que aún no han llegado
	waiting_for_memory = [] # Procesos esperando memoria
	
	free_pages = total_pages
	gantt = []
	
	# For RR
	current_quantum = 0
	running_pid = None
	
	logs = [] # Para registro de eventos
	logs.append(f"--- Iniciando simulación de planificación de CPU con algoritmo {algo_type} (Memoria Total: {total_pages}) ---")
	#ainara




	## CICLO PRINCIPAL DE SIMULACIÓN
	while completed < n: # Mientras queden procesos por completar
		# Esto libera memoria ANTES de que intentemos admitir nuevos procesos en este ciclo.
		if running_pid and p_info[running_pid]["remaining"] == 0:
			free_pages += p_info[running_pid]["process"].pages
			p_info[running_pid]["state"] = "TERMINATED"
			p_info[running_pid]["finish_time"] = time
			logs.append(f"[T={time}] FIN: {running_pid} termina ejecución. Libera {p_info[running_pid]['process'].pages} págs. (Libres: {free_pages - p_info[running_pid]['process'].pages} -> {free_pages})")
			completed += 1
			running_pid = None
			current_quantum = 0 # Reset quantum

		# 1. Process Arrivals
		while job_queue and job_queue[0].arrival <= time:
			p = job_queue.pop(0)
			waiting_for_memory.append(p)
			logs.append(f"[T={time}] LLEGADA: Proceso {p.pid} llega al sistema. (Requiere {p.pages} págs)")
			
		# 2. Memory Admission
		i = 0
		while i < len(waiting_for_memory):
			p = waiting_for_memory[i]
			if p.pages <= free_pages: # Admitir proceso si hay memoria
				free_pages -= p.pages
				p_info[p.pid]["state"] = "READY"
				ready_queue.append(p.pid)
				logs.append(f"[T={time}] MEMORIA: Proceso {p.pid} admitido. (Libres: {free_pages+p.pages} -> {free_pages})")
				waiting_for_memory.pop(i)
			else:
				logs.append(f"[T={time}] ESPERA MEMORIA: {p.pid} necesita {p.pages} págs, pero hay {free_pages}. Sigue esperando.")
				i += 1
		


		## EJECUCION DE ALGORITMOS DE PLANIFICACIÓN
		# 3. CPU Scheduling
		if algo_type == "FCFS":

			# Terminación ya manejada al inicio.
			if not running_pid and ready_queue:
				running_pid = ready_queue.pop(0)
				p_info[running_pid]["state"] = "RUNNING"
				logs.append(f"[T={time}] CPU: {running_pid} comienza ejecución.")
				if p_info[running_pid]["start_time"] is None:
					p_info[running_pid]["start_time"] = time
		
		elif algo_type == "SJF":

			if not running_pid and ready_queue:
				# Pick shortest burst
				ready_queue.sort(key=lambda pid: p_info[pid]["process"].burst)
				running_pid = ready_queue.pop(0)
				p_info[running_pid]["state"] = "RUNNING"
				logs.append(f"[T={time}] CPU: {running_pid} comienza ejecución (SJF - Ráfaga: {p_info[running_pid]['process'].burst}).")
				if p_info[running_pid]["start_time"] is None:
					p_info[running_pid]["start_time"] = time

		elif algo_type == "SRTF":

			# Terminación manejada arriba.
			
			# Put current running back to decision pool if valid to check against others
			if running_pid:
				ready_queue.append(running_pid)
				running_pid = None
				
			if ready_queue:

				ready_queue.sort(key=lambda pid: p_info[pid]["remaining"])
				best_pid = ready_queue.pop(0)
				
				# Logs solo si cambio
				running_pid = best_pid
				p_info[running_pid]["state"] = "RUNNING"
				logs.append(f"[T={time}] CPU: {running_pid} asignado (Restante: {p_info[running_pid]['remaining']}).")
				if p_info[running_pid]["start_time"] is None:
					p_info[running_pid]["start_time"] = time
		
		elif algo_type == "RR":

			# Check quantum
			if running_pid and current_quantum >= quantum:
				# Preempt
				ready_queue.append(running_pid)
				logs.append(f"[T={time}] QUANTUM: {running_pid} expropiado (Vuelve a cola).")
				running_pid = None
				current_quantum = 0
				
			if not running_pid and ready_queue:
				running_pid = ready_queue.pop(0)
				p_info[running_pid]["state"] = "RUNNING"
				logs.append(f"[T={time}] CPU: {running_pid} asignado (Nuevo Quantum).")
				current_quantum = 0
				if p_info[running_pid]["start_time"] is None:
					p_info[running_pid]["start_time"] = time

		# 4. Execute Step
		if running_pid:
			# Record usage
			if not gantt or gantt[-1][0] != running_pid:
				gantt.append((running_pid, time, time+1))
			else:
				# Extend last segment
				gantt[-1] = (running_pid, gantt[-1][1], time+1)
				
			p_info[running_pid]["remaining"] -= 1
			if algo_type == "RR":
				current_quantum += 1
		else:
			# CPU Idle
			# gantt.append(("IDLE", time, time+1)) # Optional: Show idle time
			pass
			
		time += 1
		
		
	stats = calculate_final_stats(p_info)
	return gantt, stats, logs

# Wrappers para los algoritmos
def fcfs(processes: List[Process], total_pages: int) -> Tuple[List[Tuple[str,int,int]], Dict[str, Dict[str,int]], List[str]]:
	return simple_memory_simulation(processes, total_pages, "FCFS")

def sjf_nonpreemptive(processes: List[Process], total_pages: int) -> Tuple[List[Tuple[str,int,int]], Dict[str, Dict[str,int]], List[str]]:
	return simple_memory_simulation(processes, total_pages, "SJF")

def srtf(processes: List[Process], total_pages: int) -> Tuple[List[Tuple[str,int,int]], Dict[str, Dict[str,int]], List[str]]:
	return simple_memory_simulation(processes, total_pages, "SRTF")

def round_robin(processes: List[Process], total_pages: int, quantum: int) -> Tuple[List[Tuple[str,int,int]], Dict[str, Dict[str,int]], List[str]]:
	return simple_memory_simulation(processes, total_pages, "RR", quantum)



# ============================
# 3. ESTADÍSTICAS Y MÉTRICAS
# ============================

def calculate_final_stats(p_info: Dict) -> Dict:
	stats = {}
	for pid, info in p_info.items():
		s = info["start_time"]
		f = info["finish_time"]
		arrival = info["arrival"]
		burst = info["process"].burst
		stats[pid] = {
			"arrival": arrival,
			"burst": burst,
			"start": s if s is not None else -1, 
			"finish": f,
			## Métricas
			"turnaround": f - arrival,
			"waiting": (f - arrival) - burst
		}
	return stats

def generate_stats_report(stats: Dict[str, Dict[str,int]], logs: List[str]) -> str:
	lines = []
	lines.append("--- REGISTRO DEL SISTEMA ---")
	lines.extend(logs)
	lines.append("\n--- ESTADÍSTICAS FINALES ---")
	
	total_wait = 0
	total_turn = 0
	for pid in sorted(stats.keys()):
		s = stats[pid]
		total_wait += s["waiting"]
		total_turn += s["turnaround"]
		lines.append(f"{pid}: llegada={s['arrival']} ráfaga={s['burst']} inicio={s['start']} fin={s['finish']} espera={s['waiting']} retorno={s['turnaround']}")
	n = len(stats)
	avg_w = total_wait / n if n else 0
	avg_t = total_turn / n if n else 0
	lines.append(f"\nPromedios: espera={avg_w:.2f}, retorno={avg_t:.2f}")
	return "\n".join(lines)


# ======================
# 4. FUNCIONES GRÁFICAS
# ======================

def round_rectangle(canvas, x1, y1, x2, y2, radius=15, **kwargs): 
	width = x2 - x1
	height = y2 - y1
	# Ajustar radio si el rectángulo es muy pequeño
	radius = min(radius, width/2, height/2)
	
	points = [x1+radius, y1,
			  x1+radius, y1,
			  x2-radius, y1,
			  x2-radius, y1,
			  x2, y1,
			  x2, y1+radius,
			  x2, y1+radius,
			  x2, y2-radius,
			  x2, y2-radius,
			  x2, y2,
			  x2-radius, y2,
			  x2-radius, y2,
			  x1+radius, y2,
			  x1+radius, y2,
			  x1, y2,
			  x1, y2-radius,
			  x1, y2-radius,
			  x1, y1+radius,
			  x1, y1+radius,
			  x1, y1]
	return canvas.create_polygon(points, **kwargs, smooth=True)


# =============================
# 5. GUI & INTERFAZ DE USUARIO
# =============================

class SchedulerGUI:
	def __init__(self, root):
		self.root = root
		root.title("Simulador de planificación de procesos")
		self.processes: List[Process] = []

		# --- Frame de Controles (Entrada de datos) ---
		control_frame = ttk.Frame(root, padding=8)
		control_frame.grid(row=0, column=0, sticky="nswe")

		ttk.Label(control_frame, text="PID:").grid(row=0, column=0)
		self.pid_entry = ttk.Entry(control_frame, width=5)
		self.pid_entry.grid(row=0, column=1)

		ttk.Label(control_frame, text="Nom:").grid(row=0, column=2)
		self.name_entry = ttk.Entry(control_frame, width=7)
		self.name_entry.grid(row=0, column=3)
		
		ttk.Label(control_frame, text="Llega:").grid(row=0, column=4)
		self.arrival_entry = ttk.Entry(control_frame, width=5)
		self.arrival_entry.grid(row=0, column=5)

		ttk.Label(control_frame, text="Ráf:").grid(row=0, column=6)
		self.burst_entry = ttk.Entry(control_frame, width=5)
		self.burst_entry.grid(row=0, column=7)
		
		# Campo Páginas
		ttk.Label(control_frame, text="Pág:").grid(row=0, column=8)
		self.pages_entry = ttk.Entry(control_frame, width=5)
		self.pages_entry.grid(row=0, column=9)

		add_btn = ttk.Button(control_frame, text="Añadir", command=self.add_process)
		add_btn.grid(row=0, column=10, padx=6)
		rem_btn = ttk.Button(control_frame, text="Borrar", command=self.remove_selected)
		rem_btn.grid(row=0, column=11)
        
		# Botón para añadir procesos de prueba
		test_btn = ttk.Button(control_frame, text="Test", command=self.add_default_processes)
		test_btn.grid(row=0, column=12, padx=6)
		
		# Botón de Explicación
		explain_btn = ttk.Button(control_frame, text="Ayuda", command=self.show_explanation)
		explain_btn.grid(row=0, column=13, padx=6)

		# --- Tabla de Procesos ---
		self.tree = ttk.Treeview(root, columns=("pid", "name", "arrival", "burst", "pages"), show="headings", height=6)
		self.tree.heading("pid", text="PID")
		self.tree.heading("name", text="Nombre")
		self.tree.heading("arrival", text="Llegada")
		self.tree.heading("burst", text="Ráfaga")
		self.tree.heading("pages", text="Páginas")
		
		self.tree.column("pid", width=60, anchor="center")
		self.tree.column("name", width=100, anchor="w")
		self.tree.column("arrival", width=60, anchor="center")
		self.tree.column("burst", width=60, anchor="center")
		self.tree.column("pages", width=60, anchor="center")
		self.tree.grid(row=1, column=0, sticky="we", padx=8)
		
		self.tree.bind("<Double-1>", self.on_tree_double_click)

		# --- Frame de Algoritmos ---
		algo_frame = ttk.Frame(root, padding=8)
		algo_frame.grid(row=2, column=0, sticky="we")
		self.algo_var = tk.StringVar(value="FCFS")
		for i, (val, label) in enumerate([("FCFS","FIFO (FCFS)"),("SJF","SJF (no-preemptivo)"),("SRTF","SJF Preemptivo (SRTF)"),("RR","Round Robin")]):
			ttk.Radiobutton(algo_frame, text=label, value=val, variable=self.algo_var).grid(row=0, column=i)
		ttk.Label(algo_frame, text="Quantum:").grid(row=1, column=0)
		self.quantum_entry = ttk.Entry(algo_frame, width=6)
		self.quantum_entry.insert(0, "2")
		self.quantum_entry.grid(row=1, column=1)
		
		ttk.Label(algo_frame, text="|  Memoria Total (Páginas):").grid(row=1, column=2, padx=5)
		self.mem_entry = ttk.Entry(algo_frame, width=6)
		self.mem_entry.insert(0, "10")
		self.mem_entry.grid(row=1, column=3)

		run_btn = ttk.Button(root, text="Ejecutar simulación", command=self.run_simulation)
		run_btn.grid(row=3, column=0, pady=8)

		# --- Área de Visualización (Canvas y Logs) ---
		self.canvas = tk.Canvas(root, height=200, bg="white")
		self.canvas.grid(row=4, column=0, sticky="we", padx=8, pady=8)

		self.stats_text = tk.Text(root, height=14)
		self.stats_text.grid(row=5, column=0, sticky="we", padx=8)
		
		self.stats_scroll = ttk.Scrollbar(root, orient="vertical", command=self.stats_text.yview)
		self.stats_scroll.grid(row=5, column=1, sticky="ns")
		self.stats_text.configure(yscrollcommand=self.stats_scroll.set)

	# --- Métodos de Interacción (Eventos) ---

	def on_tree_double_click(self, event):
		"""Habilita la edición de celdas al hacer doble clic"""
		region = self.tree.identify_region(event.x, event.y)
		if region != "cell":
			return
            
		column = self.tree.identify_column(event.x)
		item_id = self.tree.identify_row(event.y)
		
		# Column mapping: #1=pid, #2=name, #3=arrival, #4=burst, #5=pages
		if column == "#1":
			return # No editar PID ya que es la clave
			
		col_idx = int(column.replace("#", "")) - 1
		
		current_values = self.tree.item(item_id, "values")
		current_val = current_values[col_idx]
		
		x, y, width, height = self.tree.bbox(item_id, column)
		
		entry = ttk.Entry(self.tree)
		entry.place(x=x, y=y, width=width, height=height)
		entry.insert(0, current_val)
		entry.focus()
		
		def save_edit(event=None):
			new_val = entry.get()
			# Validations
			if col_idx in [2, 3, 4]: # Arrival, Burst, Pages -> int
				try:
					int(new_val)
				except ValueError:
					messagebox.showerror("Error", "Este campo debe ser un número entero.")
					entry.destroy()
					return

			new_values = list(current_values)
			new_values[col_idx] = new_val
			self.tree.item(item_id, values=new_values)
			
			for p in self.processes:
				if p.pid == item_id:
					if col_idx == 1: p.name = new_val
					elif col_idx == 2: p.arrival = int(new_val)
					elif col_idx == 3: p.burst = int(new_val)
					elif col_idx == 4: p.pages = int(new_val)
					break
			
			entry.destroy()

		def cancel_edit(event=None):
			entry.destroy()

		entry.bind("<Return>", save_edit)
		entry.bind("<Escape>", cancel_edit)

	def add_process(self):
		pid = self.pid_entry.get().strip()
		name = self.name_entry.get().strip()
		if not name: name = pid
		
		try:
			arrival = int(self.arrival_entry.get())
			burst = int(self.burst_entry.get())
			pages = int(self.pages_entry.get())
		except ValueError:
			messagebox.showerror("Error", "Llegada, Ráfaga y Páginas deben ser enteros")
			return
		if not pid:
			messagebox.showerror("Error", "PID no puede estar vacío")
			return
		self.processes.append(Process(pid, name, arrival, burst, pages))
		self.tree.insert("","end", iid=pid, values=(pid, name, arrival, burst, pages))
    
	def add_default_processes(self):
		defaults = [
			Process("P1", "Navegador", 0, 5, 2),
			Process("P2", "Word", 1, 3, 1),
			Process("P3", "Juego", 2, 8, 3),
			Process("P4", "Música", 3, 6, 2),
		]
		for p in defaults:
			if p.pid not in [proc.pid for proc in self.processes]:
				self.processes.append(p)
				self.tree.insert("", "end", iid=p.pid, values=(p.pid, p.name, p.arrival, p.burst, p.pages))

	def remove_selected(self):
		sel = self.tree.selection()
		for iid in sel:
			self.tree.delete(iid)
			self.processes = [p for p in self.processes if p.pid!=iid]

	def run_simulation(self):
		if not self.processes:
			messagebox.showinfo("Info","Añade procesos antes de ejecutar")
			return
		
		try:
			total_pages = int(self.mem_entry.get())
		except ValueError:
			messagebox.showerror("Error", "Memoria Total debe ser entero")
			return
			
		algo = self.algo_var.get()
		procs = sorted(self.processes, key=lambda x: (x.arrival, x.pid))
		
		valid_procs = []
		for p in procs:
			if p.pages > total_pages:
				messagebox.showwarning("Advertencia", f"El proceso {p.pid} requiere {p.pages} páginas, pero el sistema solo tiene {total_pages}. Se omitirá de la simulación.")
			else:
				valid_procs.append(p)
		
		if not valid_procs:
			messagebox.showinfo("Info", "No hay procesos válidos para ejecutar.")
			return

		if algo=="FCFS":
			gantt, stats, logs = fcfs(valid_procs, total_pages)
		elif algo=="SJF":
			gantt, stats, logs = sjf_nonpreemptive(valid_procs, total_pages)
		elif algo=="SRTF":
			gantt, stats, logs = srtf(valid_procs, total_pages)
		elif algo=="RR":
			try:
				q = int(self.quantum_entry.get())
				if q<=0:
					raise ValueError
			except ValueError:
				messagebox.showerror("Error","Quantum debe ser entero positivo")
				return
			gantt, stats, logs = round_robin(valid_procs, total_pages, q)
		else:
			messagebox.showerror("Error","Algoritmo no soportado")
			return
		self.draw_gantt(gantt)
		self.show_stats(stats, logs)

	# --- Métodos de Visualización (Graficos) ---

	def draw_gantt(self, gantt: List[Tuple[str,int,int]]):
		self.canvas.delete("all")
		if not gantt:
			return
		min_t = min(s for _,s,_ in gantt)
		max_t = max(e for _,_,e in gantt)
		span = max_t - min_t if max_t>min_t else 1
		width = int(self.canvas.winfo_width() or 800)
		height = int(self.canvas.winfo_height() or 200)
		xscale = (width-40)/span
		
		colors = ["#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA", "#F3D1F4", "#D5FCFF", "#FFF5BA"]
		color_map = {}
		
		self.canvas.create_line(10, 100, width-10, 100, fill="#dddddd", width=2)

		sorted_procs = sorted(self.processes, key=lambda x: x.pid)
		for i, p in enumerate(sorted_procs):
			color_map[p.pid] = colors[i % len(colors)]

		for seg in gantt:
			pid, s, e = seg
			x1 = 20 + (s - min_t)*xscale
			x2 = 20 + (e - min_t)*xscale
			
			if x2 - x1 < 1: x2 = x1 + 1
			
			# Usamos la función auxiliar externa
			round_rectangle(self.canvas, x1+3, 43, x2+3, 93, radius=10, fill="#e0e0e0")
			round_rectangle(self.canvas, x1, 40, x2, 90, radius=10, fill=color_map.get(pid, "#cccccc"), outline="white", width=1)
			
			proc_name = pid 
			for p in self.processes:
				if p.pid == pid:
					proc_name = p.name
					break
			
			mid_x = (x1+x2)/2
			self.canvas.create_text(mid_x, 65, text=proc_name, fill="#555555", font=("Helvetica", 10, "bold"))
			self.canvas.create_text(x1, 110, text=str(s), anchor="n", font=("Helvetica", 9), fill="#888888")
			
		final_x = 20 + (max_t - min_t)*xscale
		self.canvas.create_text(final_x, 110, text=str(max_t), anchor="n", font=("Helvetica", 9), fill="#888888")

	def show_explanation(self):
		exp_window = tk.Toplevel(self.root)
		exp_window.title("Explicación del Simulador")
		exp_window.geometry("700x600")
		
		text_area = tk.Text(exp_window, wrap="word", padx=10, pady=10, font=("Arial", 10))
		scroll = ttk.Scrollbar(exp_window, orient="vertical", command=text_area.yview)
		text_area.configure(yscrollcommand=scroll.set)
		
		scroll.pack(side="right", fill="y")
		text_area.pack(expand=True, fill="both")
		
		explanation = """
BIENVENIDO AL SIMULADOR DE PLANIFICACIÓN DE PROCESOS

¿QUÉ HACE ESTE PROGRAMA?
Este programa es una herramienta didáctica para visualizar cómo funcionan los diferentes algoritmos de planificación del procesador en un Sistema Operativo. Permite ver "quién se ejecuta cuándo" y calcula métricas clave como el tiempo de espera y el tiempo de retorno.

PARA QUÉ SIRVE:
Sirve para entender cómo el SO decide qué proceso tiene el control de la CPU en cada momento. Es fundamental para comprender la eficiencia y el comportamiento de los sistemas multitarea.

ALGORITMOS SOPORTADOS:

1. FIFO (First-In, First-Out) / FCFS:
   - Es el más simple: "El primero que llega, el primero que se sirve".
   - No es expropiativo (una vez que un proceso empieza, no se detiene hasta terminar).
   - Problema principal: El "efecto convoy", donde procesos cortos esperan mucho detrás de uno largo.

2. SJF (Shortest Job First) - No Preemptivo:
   - Prioriza los procesos con la ráfaga de CPU más corta.
   - Si un proceso llega y es más corto que los que esperan, se pone primero en la cola.
   - Una vez que un proceso empieza a ejecutarse, NO se interrumpe aunque llegue uno mas corto.
   - Minimiza el tiempo de espera promedio.

3. SRTF (Shortest Remaining Time First) - Preemptivo:
   - Es la versión "expropiativa" del SJF.
   - Si llega un proceso nuevo cuya ráfaga es menor que lo que le *falta* al proceso actual por terminar, el SO detiene al actual y pone al nuevo.
   - Es muy eficiente en tiempo de espera, pero tiene más sobrecarga por los cambios de contexto.

4. Round Robin (RR) - Turno Rotatorio:
   - Asigna a cada proceso un tiempo máximo de ejecución llamado "Quantum".
   - Si el proceso no termina en su quantum, se le interrumpe y se manda al final de la cola.
   - Es el algoritmo clásico de los sistemas de tiempo compartido.
   - El rendimiento depende mucho del tamaño del quantum elegido.

NUEVO: GESTIÓN DE MEMORIA (Paginación):
El simulador ahora incluye una restricción de memoria.
- Cada proceso requiere un número de "Páginas" para poder cargarse.
- El sistema tiene un "Total de Páginas" disponible (configurable).
- Si un proceso llega pero NO hay suficientes páginas libres, debe esperar en una "Cola de Trabajos" hasta que otros procesos terminen y liberen memoria.
- Esto añade un nivel extra de realismo: un proceso puede tener la CPU libre pero no poder ejecutarse por falta de RAM.
"""
		text_area.insert("1.0", explanation)
		text_area.config(state="disabled")

	def show_stats(self, stats: Dict[str, Dict[str,int]], logs: List[str]):
		report = generate_stats_report(stats, logs)
		self.stats_text.delete("1.0","end")
		self.stats_text.insert("1.0", report)


# ===============
# 6. ENTRY POINT
# ===============

def main():
	root = tk.Tk()
	app = SchedulerGUI(root)
	root.columnconfigure(0, weight=1)
	root.rowconfigure(4, weight=1)
	root.mainloop()

if __name__=="__main__":
	main()
