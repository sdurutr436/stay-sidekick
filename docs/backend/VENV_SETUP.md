# Backend - Entorno Virtual Python

## Requisitos previos

- Python 3.x instalado (`python3 --version`)
- pip instalado (`pip3 --version`)

---

## Primera vez (configuración inicial)

```bash
# 1. Instalar dependencias del sistema (solo en Linux/Pop!_OS/Ubuntu)
sudo apt install python3-venv python3-pip

# 2. Crear el entorno virtual
python3 -m venv venv

# 3. Activar el entorno virtual
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows

# 4. Instalar dependencias del proyecto
pip install -r requirements.txt

# 5. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus valores locales
```

---

## En el segundo PC (o al clonar el repo)

```bash
# El venv NO se sube a git, hay que recrearlo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Uso diario

```bash
# Activar el venv antes de trabajar
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows

# Arrancar el servidor
python run.py

# Desactivar el venv al terminar
deactivate
```

---

## Añadir nuevas dependencias

```bash
# Instalar el paquete
pip install nombre-paquete

# Actualizar requirements.txt (¡importante antes de hacer commit!)
pip freeze > requirements.txt
```

---

## Notas

- La carpeta `venv/` está en `.gitignore` y **no se sube al repositorio**
- `requirements.txt` es el equivalente al `pom.xml` de Spring Boot
- Si ves el prefijo `(venv)` en la terminal, el entorno está activo
