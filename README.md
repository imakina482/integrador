# TP integrador ITBA
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_DIRECTORIO_DEL_PROYECTO>
# (Opcional) Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate  
pip install -r requirements.txt
setear las variables de entorno en un archivo .env
docker-compose build
docker-compose up