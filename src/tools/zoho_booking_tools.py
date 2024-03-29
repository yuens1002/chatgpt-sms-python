from langchain.tools.base import BaseTool, ToolException
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from typing import Type, Optional
from src.api.zoho_booking_api import ZohoBookingApi
import requests
import json
from os import getenv
from dotenv import load_dotenv

load_dotenv()
api = ZohoBookingApi()


class Lead(BaseModel):
    name: str
    phone_number: str
    email: str


class ZohoAppointmentInput(BaseModel):
    from_time: str = Field(
        ...,
        format="dd-mmm-yyyy hh:mm:ss",
        description="Appointment start date and time.",
    )
    customer_details: Lead = Field(
        ..., description="Required information from a lead (prospect)"
    )
    additional_fields: Optional[dict] = Field(
        default={"location": getenv("PROPERTY_ADDRESS")},
        description="Optional: additional fields for the booking (JSON).",
    )


class ZohoCreateAppointment(BaseTool):
    name: str = "ZohoCreateAppointment"
    description: str = "Use this tool to book an appointment for property showing."
    args_schema: Type[BaseModel] = ZohoAppointmentInput

    def _run(
        self,
        input: ZohoAppointmentInput,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        form_data = input.dict()  # Convert Pydantic model into a dictionary
        form_data["service_id"] = getenv("SERVICE_ID")
        form_data["staff_id"] = getenv("STAFF_ID")
        form_data["customer_details"] = json.dumps(form_data["customer_details"])
        form_data["additional_fields"] = json.dumps(form_data["additional_fields"])
        try:

            result = api.appointment("book", form_data)
            if not result:
                raise ValueError("Zoho API did not return a valid appointment response")
            result_dict = json.loads(result)  # Load JSON string into a dictionary
            return result_dict
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
        ) as e:
            raise ToolException(f"Zoho API create appointment failed: {e}")


class ZohoCheckAvailabilityInput(BaseModel):
    selected_date: str = Field(
        ...,
        format="dd-mmm-yyyy",
        description="The date on which services are checked for availability",
    )


class ZohoCheckAvailability(BaseTool):
    name = "ZohoCheckAvailability"
    description = "Check availability time slot(s) based on a given date"
    args_schema: Type[BaseModel] = ZohoCheckAvailabilityInput

    def _run(self, input: ZohoCheckAvailabilityInput) -> dict:
        params = input.dict()  # Convert Pydantic model into a dictionary
        try:
            result = api.availability("availability", params)
            if not result:
                raise ValueError(
                    "Zoho API did not return a valid availability response"
                )
            result_dict = json.loads(result)  # Load JSON string into a dictionary
            return result_dict
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
        ) as e:
            raise ToolException(f"Zoho API availability check failed: {e}")
