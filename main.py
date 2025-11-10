from fastapi import FastAPI, Query
import psycopg2
import psycopg2.extras
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permite que o site no GitHub Pages acesse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois dá pra restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    return psycopg2.connect(
        host="trolley.proxy.rlwy.net",
        port="39108",
        dbname="railway",
        user="view_only",
        password="AH#9p143xS@2Jk$Q"
    )

@app.get("/latest")
def get_latest(station_id: int = Query(1), limit: int = Query(50)):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT "date", air_temperature, air_humid, air_pressure, water_level, water_temperature
        FROM public.datalogger_treated
        WHERE station_id = %s
        ORDER BY "date" DESC
        LIMIT %s;
    """, (station_id, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": rows}
