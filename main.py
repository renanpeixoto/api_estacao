import os
from fastapi import FastAPI, Query
import psycopg2
import psycopg2.extras
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# liberar acesso do GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# pega dados do banco das VARIÁVEIS DE AMBIENTE da Railway
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
