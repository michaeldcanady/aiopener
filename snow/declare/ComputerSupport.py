import asyncio
from aiosnow.models import TableModel, fields

# table for u_computer_support (CS tickets)
class CompSupModel(TableModel):
    sys_id = fields.String(is_primary=True)
    description = fields.String()
    opened_by = fields.String()
    number = fields.String()
    impact = fields.IntegerMap()
    priority = fields.Integer()
    assignment_group = fields.StringMap()
    sys_created_on = fields.DateTime()
    made_sla = fields.Boolean()
    work_notes = fields.String()
    work_notes_list = fields.String()
    opened_by = fields.String()
    assigned_to = fields.String()
    u_device_type = fields.String()
    serial_number = fields.String()
    u_asset = fields.String()
    cat_item = fields.String()
    parent = fields.String()
    requested_for = fields.String()
    u_depot_location = fields.String()
    u_contact_number = fields.String()
    u_department = fields.String()
    short_description = fields.String()
    comments = fields.String()
    u_wi_primary_tech = fields.String()
    assignment_group = fields.String()
    state = fields.IntegerMap()
    u_substate = fields.String()
    u_disposition = fields.String()
    u_accessories = fields.String()
    u_manufacturer = fields.String()
    u_device_problem = fields.String()
    u_authorized_person = fields.String()
    u_asset_returned = fields.String()
    
    
