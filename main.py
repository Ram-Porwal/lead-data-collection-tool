from pydantic import ValidationError

from src.lead_collector.models import Lead


# Valid lead
lead = Lead(
    company_name="ABC Technologies",
    website="https://example.com",
    industry="Software",
    city="Ahmedabad",
    state="Gujarat",
    country="India",
    email="hello@example.com",
    lead_score=80,
)

print("VALID LEAD")
print(lead)
print()


# Invalid email
try:
    Lead(
        company_name="ABC Technologies",
        email="not-an-email",
    )
except ValidationError as error:
    print("INVALID EMAIL")
    print(error)
    print()


# Invalid lead score
try:
    Lead(
        company_name="ABC Technologies",
        lead_score=150,
    )
except ValidationError as error:
    print("INVALID LEAD SCORE")
    print(error)
    print()


# Missing company name
try:
    Lead(
        company_name="",
    )
except ValidationError as error:
    print("INVALID COMPANY NAME")
    print(error)


def main() -> None:
    lead = Lead(
        company_name="ABC Technologies",
        website="https://example.com",
        industry="Software",
        city="Ahmedabad",
        state="Gujarat",
        country="India",
        email="hello@example.com",
        lead_score=80,
    )

    print(lead)


if __name__ == "__main__":
    main()