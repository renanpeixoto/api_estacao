import os
from fastapi import FastAPI, Query, HTTPException
import psycopg2
import psycopg2.extras
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "✅ API da Estação de Monitoramento está online. Use /latest?station_id=1 para ver dados."
    }

# liberar acesso do GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# variáveis de conexão – na Railway devem estar setadas como ENV VARS
DB_HOST = os.getenv("DB_HOST", "trolley.proxy.rlwy.net")
DB_PORT = os.getenv("DB_PORT", "39108")
DB_NAME = os.getenv("DB_NAME", "railway")
DB_USER = os.getenv("DB_USER", "view_only")
DB_PASSWORD = os.getenv("DB_PASSWORD", "MUDAR_SE_NAO_PUSER_ENV")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

@app.get("/latest")
def get_latest(
    station_id: int = Query(1),
    limit: int = Query(50, ge=1, le=500)
):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """
        SELECT 
            "date",
            air_temperature,
            air_humid,
            air_pressure,
            precipitation,
            wind_speed_min,
            wind_speed_max,
            wind_speed_mean,
            wind_direction,
            water_level,
            water_temperature,
            battery_volt,
            intern_temperature,
            solar_radiance
        FROM public.datalogger_treated
        WHERE station_id = %s
        ORDER BY "date" DESC
        LIMIT %s;
        """,
        (station_id, limit),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": rows}

@app.get("/tide_prediction")
def get_tide_prediction(
    station_id: int = Query(1),
    limit: int = Query(200, ge=1, le=1000)
):
    """
    Retorna previsões de maré da tabela soure_tide_prediction
    para uma estação específica.
    """
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            """
            SELECT
                "date",
                water_level,
                station_id,
                id
            FROM public.soure_tide_prediction
            WHERE station_id = %s
            ORDER BY "date" ASC
            LIMIT %s;
            """,
            (station_id, limit),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {"data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

