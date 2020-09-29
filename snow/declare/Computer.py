import asyncio
from aiosnow.models import TableModel, fields

class ComputerModel(TableModel):
    sys_id = fields.String(is_primary=True)
    name = fields.String()
    serial_number = fields.String()
    warranty_expiration = fields.String()
