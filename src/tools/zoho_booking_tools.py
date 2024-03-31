from langchain.tools.base import BaseTool, ToolException
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain_core.callbacks import CallbackManagerForToolRun
from typing import Type, Optional
from src.api.zoho_booking_api import ZohoBookingApi
import requests
import json
from os import getenv
from dotenv import load_dotenv
import re

load_dotenv()


class ZohoAppointmentInput(BaseModel):

    from_time: str = Field(
        ...,
        format="dd-mmm-yyyy hh:mm:ss",
        description="Appointment start date and time.",
    )
    name: str = Field(..., description="name on the lead")
    phone_number: str = Field(..., description="phone number on the lead")

    @validator("phone_number")  # ZOHO API fails if non-numeric char exists
    def strip_special_characters(cls, value):
        clean_number = re.sub(r"\D", "", value)  # Remove non-digits
        return clean_number

    email: str = Field(..., description="email address on the lead")


class ZohoCreateAppointment(BaseTool):

    name: str = "ZohoCreateAppointment"
    description: str = "Use this tool to book an appointment for property showing."
    args_schema: Type[BaseModel] = ZohoAppointmentInput
    api: ZohoBookingApi = ZohoBookingApi()

    def _run(
        self,
        from_time: str,
        name: str,
        phone_number: str,
        email: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            result = self.api.appointment(
                "book",
                {
                    "service_id": getenv("SERVICE_ID"),
                    "staff_id": getenv("STAFF_ID"),
                    "from_time": from_time,
                    "customer_details": json.dumps(
                        {
                            "name": name,
                            "phone_number": phone_number,
                            "email": email,
                        }
                    ),
                    "additional_fields": json.dumps(
                        {"location": getenv("PROPERTY_ADDRESS")}
                    ),
                },
            )
            if not result:
                print("not result: ", result)
                raise ValueError("Zoho API did not return a valid response")
            print("with result: ", result)
            return json.dumps(result)
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
    name: str = "ZohoCheckAvailability"
    description: str = "Check availability time slot(s) on a given date"
    args_schema: Type[BaseModel] = ZohoCheckAvailabilityInput
    api: ZohoBookingApi = ZohoBookingApi()

    def _run(self, selected_date: str) -> str:
        try:
            result = self.api.availability("availability", selected_date)
            if not result:
                raise ValueError("Zoho API did not return a valid response")
            return json.dumps(result)
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
        ) as e:
            raise ToolException(f"Zoho API request failed: {e}")
