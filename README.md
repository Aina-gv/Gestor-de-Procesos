Este proyecto contiene un simulador con interfaz gráfica (Tkinter) que permite probar diferentes algoritmos de planificación de CPU mientras se tiene en cuenta la gestión de memoria por páginas. Su objetivo es ayudar a visualizar cómo un Sistema Operativo toma decisiones sobre qué proceso ejecutar, cuándo admitirlo en memoria y cómo repartir los tiempos de CPU.

¿Para qué sirve este proyecto?
Sirve como herramienta didáctica para entender cómo funciona la planificación de procesos en un sistema operativo real.
Permite ver, paso a paso, cómo influyen factores como:

El orden de llegada
La duración de los procesos
La memoria disponible
El algoritmo elegido
La cola de listos y la cola de espera

Lo que normalmente es algo abstracto, aquí se convierte en algo visual, ordenado y fácil de interpretar.

¿Qué problema estoy resolviendo?
El proyecto resuelve la necesidad de visualizar y comprender cómo operan los algoritmos clásicos de planificación:

FIFO (FCFS)
SJF
SRTF
Round Robin (RR)

Y además añade un reto extra:
la gestión de memoria basada en páginas, que hace que no todos los procesos puedan ejecutarse inmediatamente solo por haber llegado.
Esto permite ver situaciones reales como:

Procesos que deben esperar por falta de memoria
Procesos que terminan y liberan páginas
Procesos que entran a ejecución solo cuando cumplen condiciones


Algoritmos soportados

FIFO (FCFS) — el primero que llega, el primero que se ejecuta.
SJF (no preemptivo) — ejecuta primero el proceso más corto.
SRTF (preemptivo) — permite interrupciones si llega un proceso con menor tiempo restante.
Round Robin (RR) — cada proceso recibe un quantum fijo.


Cómo ejecutar (Windows / PowerShell)
Asegúrate de tener Python 3 instalado.
Desde la carpeta del proyecto ejecuta:

```powershell
python main.py
```

Uso del simulador

Añade procesos indicando:

PID
Tiempo de llegada
Ráfaga
Páginas necesarias


Selecciona un algoritmo de planificación.
Configura (si aplica) el quantum para RR.
Pulsa "Ejecutar simulación".

Verás:

Diagrama de Gantt
Log de eventos del sistema
Tiempos de espera
Tiempo de retorno
Promedios globales


Notas

No requiere dependencias externas.
Tkinter viene incluido en la mayoría de instalaciones de Python.
El quantum solo afecta a Round Robin.


Cómo está organizado el código y por qué
El proyecto está dividido en varias partes internas bien diferenciadas, todo dentro del archivo main.py, para facilitar la lectura y mantenimiento.

1. Modelo de datos: representación clara de procesos
El dataclass hace que la información sea fácil de manejar:

@dataclass
class Process:
    pid: str
    name: str
    arrival: int
    burst: int
    pages: int
Esto permite evitar fallos y tener todos los atributos ordenados.

2. Simulación central: CPU + memoria trabajando juntas
Toda la lógica compleja vive en simple_memory_simulation().
Ahí se controla:

Llegada de procesos
Admisión en memoria
Estados: NEW, READY, RUNNING, TERMINATED
Elección de procesos según algoritmo
Liberación de memoria
Avance del tiempo global

Un fragmento clave del ciclo:

if running_pid and p_info[running_pid]["remaining"] == 0:
    free_pages += p_info[running_pid]["process"].pages
    p_info[running_pid]["state"] = "TERMINATED"
    completed += 1
    running_pid = None
    
Esto garantiza que un proceso solo deje de ejecutarse cuando realmente ha terminado, y que libere memoria correctamente.

3️. Algoritmos modulados y reutilizables
Los algoritmos son muy fáciles de extender porque cada uno es solo un “wrapper”:

def fcfs(processes, total_pages):
    return simple_memory_simulation(processes, total_pages, "FCFS")
Esto hace que modificar o agregar uno nuevo sea rapidísimo.

4️. Interfaz gráfica: organizada y clara
Tkinter se usa para:

Mostrar la tabla de procesos
Permitir editar valores
Elegir el algoritmo
Dibujar el Gantt
Mostrar estadísticas

La clase SchedulerGUI se encarga de toda la parte visual, manteniendo el código limpio y separado de la lógica interna.

Dificultades que tuve (y cómo las resolví)
1. Integrar memoria + planificación
El proyecto se volvía caótico cuando un proceso:

llegaba
no tenía memoria
debía esperar
luego podía entrar

Tuve que reestructurar la cola de espera varias veces hasta que funcionó.

2. Dibujar el diagrama de Gantt
Hacerlo visual, bonito y proporcional fue un reto.
La solución fue crear rectángulos redondeados por proceso:
round_rectangle(self.canvas, x1, 40, x2, 90, radius=10, fill=color)
3. Round Robin y SRTF
Ambos requieren interrupciones.
Tuve que revisar varias veces la forma en que “devolvía” procesos a la cola y cómo actualizaba el quantum.

4. Control de estados y tiempos
Hubo momentos donde:

procesos no terminaban bien,
métricas eran incorrectas,
o la memoria no se liberaba.

Tuve que reorganizar el orden de las operaciones del bucle principal.

Por qué estructuré el código así
Elegí esta estructura porque:

Separa lo visual de lo lógico
Permite agregar más algoritmos sin romper nada
Facilita depurar
Hace la simulación clara y modificable
Evita duplicar lógica

Todo está hecho para que el simulador sea escalable, fácil de leer y fácil de mejorar.

Conclusión
Este proyecto me ayudó a comprender mucho mejor cómo funciona la planificación en sistemas operativos, especialmente cuando se combina con restricciones reales como la memoria.
Aprendí a:

manejar estados complejos
dividir un problema grande en partes más pequeñas
usar Tkinter para crear interfaces
depurar código largo y con muchas condiciones
organizar el flujo de un simulador realista

Es uno de los proyectos más completos y desafiantes que he realizado.
