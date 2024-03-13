@echo off

rem Instalar dependencias generales
echo Instalando dependencias generales...
pip install -r "dependencias.txt"

rem Iniciando el proyecto web
echo Inciando el proyecto web
cd safezone

rem Creando el entorno virtual
echo Creando entorno virtual...
python -m virtualenv venv

rem Activar el entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate

rem Instalar requerimientos
echo Instalando requerimientos...
pip install -r "requirements.txt"

cd ..

cls

echo Proyecto completado

echo use el comando "runserver" para iniciar el servidor web
echo use el comando "notificacion" para iniciar las notificaciones

rem Desactivar el entorno virtual
deactivate