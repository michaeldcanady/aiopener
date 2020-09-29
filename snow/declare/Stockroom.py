import asyncio
from aiosnow.models import TableModel, fields

class StockRoomModel(TableModel):
    sys_id = fields.String(is_primary=True)
    display_name = fields.String()
