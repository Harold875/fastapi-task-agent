# Resumen del proyecto

Este proyecto es una API REST desarrollada con FastAPI y utiliza una base de datos de PostgreSQL.

El proyecto tambien tiene un agente de IA que permite gestionar las tareas del usuario. El agente esta desarrollado con Pydantic AI.


## Instalacion y ejecucion del proyecto

### Requisitos

- Docker

### Configuracion de variable de entorno

Para utilizar el proyecto y las funcionalidades de AI es importante agregar la variable de entorno del LLM.

Los modelos permitidos son:
- ChatGPT
- Google

> Nota: solo es necesario agregar alguna de estas variables de entorno.

Las variables entorno son:
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `GEMINI_API_KEY`

*El modelo de geminis, funciona con cualquiera de esas 2 variables (`GOOGLE_API_KEY`, `GEMINI_API_KEY`)*

Esas variables de entorno se tiene que agregar en un archivo `.env` en el directorio `backend/`

La ruta seria asi: `./backend/.env`

Comando para crear la variable de entorno (Linux / MacOS):
```bash
# Desde el directorio del proyecto fastapi-task-agent/

echo "GOOGLE_API_KEY=key-token" > ./backend/.env
```

### Ejecucion del proyecto

Ya con la variable de entorno agregada al archivo `.env`.

Ahora solo se tiene que ejecutar el comando:

```bash
docker compose up
```

Y ya con esto el proyecto se estara ejecutando en los siguientes puertos:

- `api` -> http://127.0.0.1:8000/

- `web_chat` -> http://127.0.0.1:7932/


> El `web_chat` es el interfaz que se puede utilizar para interactuar con el agente de AI.

> *Nota: En la `api` la documentacion se encuentra en la ruta http://127.0.0.1:8000/docs*