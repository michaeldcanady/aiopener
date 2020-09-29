import asyncio
from aiosnow.models import TableModel, fields

class HardwareModel(TableModel):
    # Commonly modified and used entries
    sys_id = fields.String(is_primary=True)
    display_name = fields.String()
    serial_number = fields.String()
    model = fields.String()
    model_category = fields.String()
    u_type = fields.String()
    install_status = fields.IntegerMap()
    substatus = fields.StringMap()
    u_active_directory_ou = fields.String()
    ci = fields.String()
    assigned_to = fields.String()
    u_budget__index_code_ = fields.String()
    location = fields.String()
    u_last_hw_inventory_date = fields.String()
    # General Tab
    u_last_logged_in_user = fields.String()
    u_top_console_user_label = fields.String()
    u_computer_last_logged_in = fields.String()
    sys_class_name = fields.String()
    company = fields.String()
    assigned = fields.String()
    install_date = fields.String()
    comments = fields.String()
    stockroom = fields.String()
    # Order Information
    purchase_date = fields.String()
    purchase_line = fields.String()
    u_warranty_type = fields.String()
    warranty_expiration = fields.String()
