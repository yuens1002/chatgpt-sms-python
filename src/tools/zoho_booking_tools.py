from langchain.tools import BaseTool, ToolException
from pydantic import BaseModel, Field
from typing import Type
from api.zoho_booking_api import ZohoBookingApi
import requests


class ZohoAppointmentInput(BaseModel):
    service_id: str = Field(description="The Zoho Bookings service ID.")
    staff_id: str = Field(description="The Zoho Bookings staff ID.")
    from_time: str = Field(description="Appointment start date and time.")
    customer_details: str = Field(description="Customer details in JSON format.")
    additional_fields: str = Field(
        description="Additional fields for the booking (JSON)."
    )


class ZohoCreateAppointment(BaseTool):
    name = "ZohoCreateAppointment"
    description = "Creates a new appointment booking within Zoho Bookings."
    args_schema: Type[BaseModel] = ZohoAppointmentInput
    return_direct = True  # Assuming the Zoho response fits as a direct output

    def __init__(self, zoho_booking_api: ZohoBookingApi):
        self.zoho_booking_api = zoho_booking_api

    def _run(self, input: ZohoAppointmentInput) -> dict:
        form_data = input.model_dump()  # Convert Pydantic model into a dictionary
        try:
            result = self.zoho_booking_api.appointment("book", form_data)
            return {"result": result}
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
        ) as e:
            raise ToolException(f"Zoho appointment creation failed: {e}")
