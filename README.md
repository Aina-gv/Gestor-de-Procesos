Simulador de planificación de procesos

Este proyecto contiene un simulador simple con interfaz gráfica (Tkinter) que permite probar algoritmos de planificación:

- FIFO (FCFS)
- SJF (no preemptivo)
- SJF preemptivo (SRTF)
- Round Robin (RR)

Cómo ejecutar (Windows / PowerShell):

1. Asegúrate de tener Python 3 instalado.
2. Desde la carpeta del proyecto ejecuta:

```powershell
python main.py
```

Uso:
- Añade procesos indicando un PID (texto), tiempo de llegada (entero) y ráfaga (entero).
- Selecciona un algoritmo y pulsa "Ejecutar simulación".
- Verás un diagrama de Gantt y las métricas de cada proceso (espera y retorno) y los promedios.

Notas:
- No requiere dependencias externas (Tkinter viene con muchas instalaciones de Python).
- Quantum aplicable solo para RR.
