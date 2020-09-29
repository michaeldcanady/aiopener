import asyncio
from aiosnow.models import TableModel, fields

class SysUserModel(TableModel):
    sys_id = fields.String(is_primary=True)
    user_name = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    name = fields.String()
    title = fields.String()
    active = fields.Boolean()
    employee_number = fields.String()
    email = fields.String()
    manager = fields.String()
    company = fields.String()
    department_label = fields.String()
    u_default_group = fields.String()
    calendar_integration = fields.String()
    time_zone = fields.String()
    phone = fields.String()
    mobile_phone = fields.String()
    u_team = fields.String()
    u_division = fields.String()
    u_organization = fields.String()
