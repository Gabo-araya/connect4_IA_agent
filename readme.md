# Connect Four con IA 🎮

Un juego clásico de Conecta 4 implementado en Python con una IA adaptativa que utiliza el algoritmo Minimax con poda Alfa-Beta. El juego incluye una interfaz gráfica construida con Pygame y almacena estadísticas del juego en una base de datos SQLite.

## Características principales 🌟

- **Interfaz gráfica intuitiva**: Diseñada con Pygame para una experiencia de usuario fluida
- **IA adaptativa**: Ajusta su dificultad basándose en el rendimiento del jugador
- **Múltiples niveles de dificultad**:
  - Fácil
  - Medio
  - Difícil
- **Tamaños de tablero personalizables**:
  - Normal (6x7)
  - Pequeño (5x4)
- **Sistema de sugerencias**: Ayuda para jugadores que necesitan orientación
- **Estadísticas detalladas**: Seguimiento de:
  - Tiempo de juego
  - Movimientos realizados
  - Nodos explorados por la IA
  - Sugerencias utilizadas
- **Persistencia de datos**: Almacenamiento de partidas y estadísticas en SQLite


Estas instrucciones te permitirán obtener una copia del proyecto en funcionamiento en tu máquina local para propósitos de desarrollo y pruebas.

## Requisitos previos 📋

_Esta es una lista de los paquetes que deben estar instalados previamente:_

* Python 3
	- Lenguaje de programación
	- [Ayuda - https://docs.microsoft.com/en-us/windows/python/beginners)](https://docs.microsoft.com/en-us/windows/python/beginners)
	- [Curso Django desde Cero en youtube](https://www.youtube.com/watch?v=vo4VF3neyrs)

* Pip
	- Gestor de instalación de paquetes PIP
	- [Ayuda - https://tecnonucleous.com/2018/01/28/como-instalar-pip-para-python-en-windows-mac-y-linux/](https://tecnonucleous.com/2018/01/28/como-instalar-pip-para-python-en-windows-mac-y-linux/)

* Virtualenv
	- Creador de entornos virtuales para Python
	- [Ayuda - https://techexpert.tips/es/windows-es/instalacion-del-entorno-virtual-de-python-en-windows/](https://techexpert.tips/es/windows-es/instalacion-del-entorno-virtual-de-python-en-windows/)

### Instalación pre-requisitos 🔧

Muchas veces tenemos ese problema común de no poder instalar ciertas librerías o realizar configuraciones para poder desarrollar en Windows para Web y es por ello que en éste tutorial vamos a ver los pasos para instalar Python y configurarlo con Pip y Virtualenv para así poder empezar a desarrollar aplicaciones basadas en éste lenguaje e instalar Django para crear aplicaciones web. [Ver video -> **https://www.youtube.com/watch?v=sG7Q-r_SZhA**](https://www.youtube.com/watch?v=sG7Q-r_SZhA)

1. Descargamos e instalamos Python 3.10 (o una versión superior) para Windows
	- [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. Agregaremos Python a las variables de entorno de nuestro sistema si es que no se agregaron durante la instalación para que así podamos ejecutarlo desde la terminal `/cmd`
	- `C:\Python34 y C:\Python34\Scripts`

3. Ejecutamos Pip para verificar que esté instalado correctamente y también la versión
	- `pip --version`

4. Instalamos Virtualenv con
	- `pip install virtualenv`

5. Verificamos la versión de Virtualenv
	- `virtualenv --version`

6. Crearemos un entorno virtual con Python
	- `virtualenv connect4-env`

7. Iniciamos el entorno virtual
	- `.\test\Scripts\activate`
	- `source /home/gabo/envs/connect4-env/bin/activate`
	- `source /home/gabo/proy/pyscripts/connect4/connect4-env/bin/activate`

8. Finalmente desactivamos el entorno virtual
	- `deactivate`

## Instalación 🔧

### Windows

1. Clonar el repositorio:
```bash
git clone https://github.com/Gabo-araya/connect4_IA_agent.git
cd connect4_IA_agent
```

2. Crear y activar el entorno virtual:
```bash
python -m venv connect4-env
connect4-env\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

### Linux/macOS

1. Clonar el repositorio:
```bash
git clone https://github.com/Gabo-araya/connect4_IA_agent.git
cd connect4_IA_agent
```

2. Crear y activar el entorno virtual:
```bash
python3 -m venv connect4-env
source connect4-env/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución del juego ▶️

1. Asegúrate de que el entorno virtual está activado
2. Ejecuta el juego:
```bash
python main.py
```

## Cómo jugar 🎲

1. Al iniciar el juego, selecciona:
   - Tamaño del tablero
   - Nivel de dificultad
   - Jugador inicial (Humano o IA)

2. Durante el juego:
   - Haz clic en una columna para soltar una ficha
   - Usa el botón "Sugerir Jugada" si necesitas ayuda
   - El objetivo es conectar 4 fichas del mismo color

3. El juego termina cuando:
   - Un jugador conecta 4 fichas
   - El tablero se llena (empate)
   - Se agota el tiempo de movimiento

## Estructura del proyecto 📁

```
connect-four/
├── main.py              # Punto de entrada y GUI
├── connect_four.py      # Lógica del juego e IA
├── requirements.txt     # Dependencias
├── connect_four.db      # Base de datos SQLite
└── README.md           # Este archivo
```

## Dependencias principales 📦

- pygame==2.6.1
- numpy==1.26.2
- sqlite3 (incluido en Python)

## Características técnicas 🔧

- Algoritmo Minimax con poda Alfa-Beta para la IA
- Caché de resultados con decorador @lru_cache
- Logging comprehensivo para debugging
- Manejo robusto de errores y excepciones
- Sistema de dificultad adaptativa

## Contribuir 🤝

1. Haz un Fork del proyecto
2. Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`)
3. Realiza tus cambios y haz commit (`git commit -am 'Agrega nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## Solución de problemas comunes ⚠️

### SQLite errors
Si encuentras errores relacionados con la base de datos:
```bash
touch connect_four.log connect_four_logic.log
chmod 666 connect_four.log connect_four_logic.log
```

### Pygame no se instala correctamente
En Linux, asegúrate de tener las dependencias necesarias:
```bash
sudo apt-get install python3-pygame
```

## Licencia 📄

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles

## Autores ✒️

* **[Gabo Araya](https://github.com/Gabo-araya/)**
* **[Hedy Herrada](https://github.com/Gabo-araya/)**
* **[Macarena Riquelme](https://github.com/mriquelmec/)**


## Agradecimientos 🎁

* Inspirado en el clásico juego Connect Four
* Agradecimientos a la comunidad de Python y Pygame
* A todos los que han contribuido con sugerencias y mejoras

---
⌨️ con ❤️ por [Tu nombre] 😊
