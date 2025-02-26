from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth0, init_components, equipos, integrantes

app = FastAPI(title='newo2 b2b api')

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes (puedes restringirlo a 'http://localhost:8100' si lo deseas)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

# Middleware para deshabilitar caché en las respuestas
@app.middleware("http")
async def no_cache_middleware(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


app.include_router(auth0.query, prefix='/auth')
app.include_router(init_components.query, prefix='/init_components')
app.include_router(equipos.query, prefix='/equipos')
app.include_router(integrantes.query, prefix='/integrantes')



