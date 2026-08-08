from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from fastapi import HTTPException

app = FastAPI()

class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = "in-person"
    senior_citizen: bool = False

class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience_years: int = Field(..., gt=0)
    is_available: bool = True

# -----------------------------
# Q2: Doctors Data
# -----------------------------
doctors = [
    {
        "id": 1,
        "name": "Dr. Arjun Mehta",
        "specialization": "Cardiologist",
        "fee": 800,
        "experience_years": 12,
        "is_available": True
    },
    {
        "id": 2,
        "name": "Dr. Priya Sharma",
        "specialization": "Dermatologist",
        "fee": 500,
        "experience_years": 8,
        "is_available": True
    },
    {
        "id": 3,
        "name": "Dr. Rahul Verma",
        "specialization": "Pediatrician",
        "fee": 600,
        "experience_years": 10,
        "is_available": False
    },
    {
        "id": 4,
        "name": "Dr. Sneha Iyer",
        "specialization": "General",
        "fee": 300,
        "experience_years": 5,
        "is_available": True
    },
    {
        "id": 5,
        "name": "Dr. Kiran Patel",
        "specialization": "Cardiologist",
        "fee": 900,
        "experience_years": 15,
        "is_available": False
    },
    {
        "id": 6,
        "name": "Dr. Anjali Gupta",
        "specialization": "Dermatologist",
        "fee": 450,
        "experience_years": 7,
        "is_available": True
    }
]

# -----------------------------
# Helper: Find Doctor
# -----------------------------
def find_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor
    return None

# -----------------------------
# Helper: Filter Doctors
# -----------------------------
def filter_doctors_logic(specialization=None, max_fee=None, min_experience=None, is_available=None):
    result = doctors

    if specialization is not None:
        result = [d for d in result if d["specialization"].lower() == specialization.lower()]

    if max_fee is not None:
        result = [d for d in result if d["fee"] <= max_fee]

    if min_experience is not None:
        result = [d for d in result if d["experience_years"] >= min_experience]

    if is_available is not None:
        result = [d for d in result if d["is_available"] == is_available]

    return result

# -----------------------------
# Helper: Calculate Fee
# -----------------------------
def calculate_fee(base_fee: int, appointment_type: str, senior_citizen: bool):
    fee = base_fee

    if appointment_type == "video":
        fee = base_fee * 0.8
    elif appointment_type == "emergency":
        fee = base_fee * 1.5
    elif appointment_type == "in-person":
        fee = base_fee

    original_fee = fee

    # Senior citizen discount (15%)
    if senior_citizen:
        fee = fee * 0.85

    return round(original_fee), round(fee)

# -----------------------------
# Q4: Appointments Data
# -----------------------------
appointments = []
appt_counter = 1


# -----------------------------
# Q1: Root Endpoint
# -----------------------------
@app.get("/")
def home():
    return {"message": "Welcome to MediCare Clinic"}


# -----------------------------
# Q2: Get All Doctors
# -----------------------------
@app.get("/doctors")
def get_doctors():
    total = len(doctors)
    available_count = sum(1 for d in doctors if d["is_available"])

    return {
        "total": total,
        "available_count": available_count,
        "doctors": doctors
    }

@app.post("/doctors", status_code=201)
def add_doctor(new_doc: NewDoctor):
    # check duplicate name
    for d in doctors:
        if d["name"].lower() == new_doc.name.lower():
            raise HTTPException(status_code=400, detail="Doctor with this name already exists")

    new_id = max(d["id"] for d in doctors) + 1

    doctor = {
        "id": new_id,
        "name": new_doc.name,
        "specialization": new_doc.specialization,
        "fee": new_doc.fee,
        "experience_years": new_doc.experience_years,
        "is_available": new_doc.is_available
    }

    doctors.append(doctor)
    return doctor

@app.put("/doctors/{doctor_id}")
def update_doctor(
    doctor_id: int,
    fee: Optional[int] = None,
    is_available: Optional[bool] = None
):
    doctor = find_doctor(doctor_id)

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if fee is not None:
        doctor["fee"] = fee

    if is_available is not None:
        doctor["is_available"] = is_available

    return doctor

@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # check active appointments
    for appt in appointments:
        if appt["doctor"] == doctor["name"] and appt["status"] == "scheduled":
            raise HTTPException(status_code=400, detail="Doctor has active appointments")

    doctors.remove(doctor)

    return {"message": "Doctor deleted successfully"}

# -----------------------------
# Q5: Doctors Summary
# -----------------------------
@app.get("/doctors/summary")
def doctors_summary():
    total = len(doctors)
    available = sum(1 for d in doctors if d["is_available"])

    most_exp = max(doctors, key=lambda d: d["experience_years"])

    cheapest = min(d["fee"] for d in doctors)

    specialization_count = {}
    for d in doctors:
        spec = d["specialization"]
        specialization_count[spec] = specialization_count.get(spec, 0) + 1

    return {
        "total_doctors": total,
        "available_doctors": available,
        "most_experienced_doctor": most_exp["name"],
        "cheapest_fee": cheapest,
        "specialization_count": specialization_count
    }


@app.get("/doctors/filter")
def filter_doctors(
    specialization: Optional[str] = None,
    max_fee: Optional[int] = None,
    min_experience: Optional[int] = None,
    is_available: Optional[bool] = None
):
    filtered = filter_doctors_logic(
        specialization,
        max_fee,
        min_experience,
        is_available
    )

    return {
        "total": len(filtered),
        "doctors": filtered
    }

@app.get("/doctors/search")
def search_doctors(keyword: str):
    keyword = keyword.lower()

    results = [
        d for d in doctors
        if keyword in d["name"].lower() or keyword in d["specialization"].lower()
    ]

    if not results:
        return {"message": "No doctors found matching your search", "total_found": 0}

    return {
        "total_found": len(results),
        "doctors": results
    }

@app.get("/doctors/sort")
def sort_doctors(sort_by: str = "fee", order: str = "asc"):
    valid_fields = ["fee", "name", "experience_years"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order")

    reverse = True if order == "desc" else False

    sorted_list = sorted(doctors, key=lambda d: d[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_list),
        "doctors": sorted_list
    }

@app.get("/doctors/page")
def paginate_doctors(page: int = 1, limit: int = 3):
    total = len(doctors)
    total_pages = (total + limit - 1) // limit  # ceiling division

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "doctors": doctors[start:end]
    }

@app.get("/doctors/browse")
def browse_doctors(
    keyword: Optional[str] = None,
    sort_by: str = "fee",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    result = doctors.copy()

    # 🔹 FILTER
    if keyword:
        keyword = keyword.lower()
        result = [
            d for d in result
            if keyword in d["name"].lower() or keyword in d["specialization"].lower()
        ]

    # 🔹 SORT
    valid_fields = ["fee", "name", "experience_years"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda d: d[sort_by], reverse=reverse)

    # PAGINATION
    total = len(result)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    paginated = result[start:end]

    return {
        "filters": {"keyword": keyword},
        "sort": {"sort_by": sort_by, "order": order},
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        },
        "results": paginated
    }

# -----------------------------
# Q3: Get Doctor by ID
# -----------------------------
@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor

    return {"error": "Doctor not found"}


# -----------------------------
# Q4: Get Appointments
# -----------------------------
@app.get("/appointments")
def get_appointments():
    return {
        "total": len(appointments),
        "appointments": appointments
    }

@app.get("/appointments/search")
def search_appointments(patient_name: str):
    keyword = patient_name.lower()

    results = [
        a for a in appointments
        if keyword in a["patient"].lower()
    ]

    return {
        "total_found": len(results),
        "appointments": results
    }

@app.get("/appointments/sort")
def sort_appointments(sort_by: str = "date"):
    valid_fields = ["date", "final_fee"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    sorted_list = sorted(appointments, key=lambda a: a[sort_by])

    return {
        "sort_by": sort_by,
        "total": len(sorted_list),
        "appointments": sorted_list
    }

@app.get("/appointments/page")
def paginate_appointments(page: int = 1, limit: int = 3):
    total = len(appointments)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "appointments": appointments[start:end]
    }

# -----------------------------
# POST: Book Appointment
# -----------------------------
@app.post("/appointments")
def book_appointment(request: AppointmentRequest):
    global appt_counter

    doctor = find_doctor(request.doctor_id)

    if not doctor:
        return {"error": "Doctor not found"}

    if not doctor["is_available"]:
        return {"error": "Doctor not available"}

    original_fee, final_fee = calculate_fee(
        doctor["fee"],
        request.appointment_type,
        request.senior_citizen
    )

    appointment = {
        "appointment_id": appt_counter,
        "patient": request.patient_name,
        "doctor": doctor["name"],
        "date": request.date,
        "type": request.appointment_type,
        "original_fee": original_fee,
        "final_fee": final_fee,
        "status": "scheduled"
    }

    appointments.append(appointment)
    appt_counter += 1

    return appointment

@app.get("/appointments/active")
def get_active_appointments():
    active = [
        a for a in appointments
        if a["status"] in ["scheduled", "confirmed"]
    ]

    return {
        "total": len(active),
        "appointments": active
    }

@app.get("/appointments/by-doctor/{doctor_id}")
def get_appointments_by_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    result = [
        a for a in appointments
        if a["doctor"] == doctor["name"]
    ]

    return {
        "doctor": doctor["name"],
        "total": len(result),
        "appointments": result
    }

@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            appt["status"] = "confirmed"
            return appt

    raise HTTPException(status_code=404, detail="Appointment not found")


@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            appt["status"] = "cancelled"

            # make doctor available again
            for doc in doctors:
                if doc["name"] == appt["doctor"]:
                    doc["is_available"] = True

            return appt

    raise HTTPException(status_code=404, detail="Appointment not found")

@app.post("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            appt["status"] = "completed"
            return appt

    raise HTTPException(status_code=404, detail="Appointment not found")
