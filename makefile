# Variables
PYTHON_VERSION=python3.8
VENV_DIR=venv
ENV_FILE=.env

# Reglas

# MAKE ALL => para configurar el entorno virtual
all: check_env venv install_deps install_manual_deps

check_env:
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "Error: El archivo $(ENV_FILE) no existe. Por favor, créalo antes de continuar."; \
		exit 1; \
	fi

venv:
	@echo "Creando el entorno virtual..."
	$(PYTHON_VERSION) -m venv $(VENV_DIR)

install_deps:
	@echo "Instalando dependencias desde requirements.txt..."
	$(VENV_DIR)/bin/pip install -r requirements.txt

install_manual_deps:
	@echo "Instalando pandas y Airflow manualmente..."
	$(VENV_DIR)/bin/pip install pandas==1.5.3 apache-airflow==2.10.1
# MAKE DOCKER_UP => para levantar el proyecto con docker compose
docker_up:
	@echo "Levantando el proyecto con Docker Compose..."
	docker-compose up
# MAKE DOCKER_DOWN => para detener los servicios
docker_down:
	@echo "Deteniendo los servicios de Docker Compose..."
	docker-compose down

clean:
	@echo "Eliminando el entorno virtual..."
	rm -rf $(VENV_DIR)
# MAKE TEST => para ejecutar pruebass
test:
	@echo "Ejecutando pruebas..."
	$(VENV_DIR)/bin/python -m unittest discover -v tests/

.PHONY: all check_env venv install_deps install_manual_deps docker_up docker_down clean test