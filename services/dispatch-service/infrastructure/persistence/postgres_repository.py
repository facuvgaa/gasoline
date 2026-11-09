from typing import Optional
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from domain.models.dispatch import Dispatch, FuelType
from domain.ports.repository import DispatchRepositoryPort

class PostgresDispatchRepository(DispatchRepositoryPort):
    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def save(self, dispatch: Dispatch) -> None:
        query = """
            INSERT INTO dispatches (
                id, truck_plate, driver_id, fuel_type,
                volume_liters, temperature_c, status, created_at
            ) VALUES (
                %(id)s, %(truck_plate)s, %(driver_id)s, %(fuel_type)s,
                %(volume_liters)s, %(temperature_c)s, %(status)s, %(created_at)s
            )
        """
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, {
                    "id": dispatch.id,
                    "truck_plate": dispatch.truck_plate,
                    "driver_id": dispatch.driver_id,
                    "fuel_type": dispatch.fuel_type.value,
                    "volume_liters": dispatch.volume_liters,
                    "temperature_c": dispatch.temperature_c,
                    "status": dispatch.status,
                    "created_at": dispatch.created_at,
                })
            conn.commit()

    def find_by_id(self, dispatch_id: str) -> Optional[Dispatch]:
        query = """
            SELECT id, truck_plate, driver_id, fuel_type,
                   volume_liters, temperature_c, status, created_at
            FROM dispatches
            WHERE id = %(id)s
        """
        with self._pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, {"id": dispatch_id})
                row = cur.fetchone()
                if not row:
                    return None

                return Dispatch(
                    id=row["id"],
                    truck_plate=row["truck_plate"],
                    driver_id=row["driver_id"],
                    fuel_type=FuelType(row["fuel_type"]),
                    volume_liters=row["volume_liters"],
                    temperature_c=row["temperature_c"],
                    status=row["status"],
                    created_at=row["created_at"],
                )

