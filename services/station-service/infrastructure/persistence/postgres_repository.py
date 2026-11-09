from typing import Optional
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from domain.models.discharge import Discharge
from domain.ports.repository import DischargeRepositoryPort

class PostgresDischargeRepository(DischargeRepositoryPort):
    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def save(self, discharge: Discharge) -> None:
        query = """
            INSERT INTO discharges (
                id, dispatch_id, station_id, tank_id,
                received_volume_liters, received_temperature_c, discharged_at
            ) VALUES (
                %(id)s, %(dispatch_id)s, %(station_id)s, %(tank_id)s,
                %(received_volume_liters)s, %(received_temperature_c)s, %(discharged_at)s
            )
        """
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, {
                    "id": discharge.id,
                    "dispatch_id": discharge.dispatch_id,
                    "station_id": discharge.station_id,
                    "tank_id": discharge.tank_id,
                    "received_volume_liters": discharge.received_volume_liters,
                    "received_temperature_c": discharge.received_temperature_c,
                    "discharged_at": discharge.discharged_at,
                })
            conn.commit()

    def find_by_id(self, discharge_id: str) -> Optional[Discharge]:
        query = """
            SELECT id, dispatch_id, station_id, tank_id,
                   received_volume_liters, received_temperature_c, discharged_at
            FROM discharges
            WHERE id = %(id)s
        """
        return self._fetch_one(query, {"id": discharge_id})

    def find_by_dispatch_id(self, dispatch_id: str) -> Optional[Discharge]:
        query = """
            SELECT id, dispatch_id, station_id, tank_id,
                   received_volume_liters, received_temperature_c, discharged_at
            FROM discharges
            WHERE dispatch_id = %(dispatch_id)s
        """
        return self._fetch_one(query, {"dispatch_id": dispatch_id})

    def _fetch_one(self, query: str, params: dict) -> Optional[Discharge]:
        with self._pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, params)
                row = cur.fetchone()
                if not row:
                    return None

                return Discharge(
                    id=row["id"],
                    dispatch_id=row["dispatch_id"],
                    station_id=row["station_id"],
                    tank_id=row["tank_id"],
                    received_volume_liters=row["received_volume_liters"],
                    received_temperature_c=row["received_temperature_c"],
                    discharged_at=row["discharged_at"],
                )
