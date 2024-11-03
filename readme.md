# Connect4

_Proyecto de juego Connect4 con Agente IA usando algoritmos minimax y poda alpha-beta._

Estas instrucciones te permitirán obtener una copia del proyecto en funcionamiento en tu máquina local para propósitos de desarrollo y pruebas.

## Pre-requisitos

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

### Instalación pre-requisitos

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

### Instalación Local

Seguir los siguientes pasos para la instalación local.

1. Clonar el repositorio o subir/descargar los archivos.

	- `git clone https://github.com/Gabo-araya/Connect4-IA/`

2. Instalar los requerimientos.

	- `python3 -m pip install -r requirements.txt`

	Alternativamente, instalar
	- numpy
	- pygame
	-

3. (CONTINUAR)


## Funcionalidades

1. Navegación por contenidos del sitio
   - Muestra un resumen del propósito del sitio y sus funcionalidades.
   - Cuenta con las siguientes páginas: Nosotros, Servicios, Proyectos, Blog, Visión y Footer.
   - Acceso a lista de artículos desde el footer

2. Buscador de artículos
	- Permite hacer una búsqueda de artículos.
	- Está presente en la landing page, en la lista de artículos y en cada artículo individual.

3. Envío de mensajes
   - Formulario de contacto desde landing page.
   - Permite guardar mensajes en base de datos para posterior revisión desde el Panel de Aministración.

4. Panel de Administración de contenidos
   - Acceso al Panel desde el footer
   - Permite realizar CRUD sobre Personas, Servicios, Proyectos, Mensajes, Páginas, Artículos, Categorías, Imágenes.

## Herramientas de construcción

_Estas son las herramientas que hemos utilizado en nuestro proyecto_

* [Django](https://www.djangoproject.com/) - El framework web usado


## Autores

* **[Gabo Araya](https://github.com/Gabo-araya/)**
* **[Hedy Herrada](https://github.com/Gabo-araya/)**
* **[Macarena Riquelme](https://github.com/Gabo-araya/)**
