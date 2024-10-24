# Variables
PYTHON_VERSION=python3.8
VENV_DIR=venv

# Reglas
all: venv install_deps install_manual_deps

venv:
	@echo "Creando el entorno virtual..."
	$(PYTHON_VERSION) -m venv $(VENV_DIR)

install_deps:
	@echo "Instalando dependencias desde requirements.txt..."
	$(VENV_DIR)/bin/pip install -r requirements.txt

install_manual_deps:
	@echo "Instalando pandas y Airflow manualmente..."
	$(VENV_DIR)/bin/pip install pandas==1.5.3 apache-airflow==2.10.1

docker_up:
	@echo "Levantando el proyecto con Docker Compose..."
	docker-compose up

docker_down:
	@echo "Deteniendo los servicios de Docker Compose..."
	docker-compose down

clean:
	@echo "Eliminando el entorno virtual..."
	rm -rf $(VENV_DIR)

test:
	@echo "Ejecutando pruebas..."
	$(VENV_DIR)/bin/python -m unittest discover -v tests/

.PHONY: all venv install_deps install_manual_deps docker_up docker_down clean test