from sqlmodel import SQLModel, Field
from datetime import datetime
from datetime import date
from pydantic import validator


class OpaPropertiesPublic(SQLModel, table=True):
    __tablename__ = "opa_properties_public"

    @property
    def split_by(self) -> tuple[str, str]:
        pass

    cartodb_id: int = Field(primary_key=True)
    objectid: float = Field(primary_key=True)
    parcel_number: str = Field(primary_key=True)
    zip_code: str | None
    pin: int
    street_name: str
    house_number: str
    location: str
    owner_1: str | None
    owner_2: str | None
    the_geom: str | None
    the_geom_webmercator: str | None
    assessment_date: datetime | None
    basements: str | None
    beginning_point: str | None
    book_and_page: str | None
    building_code: str | None
    building_code_description: str | None
    category_code: str | None
    category_code_description: str | None
    census_tract: str | None
    central_air: str | None
    cross_reference: str | None
    date_exterior_condition: date | None
    depth: float | None
    exempt_building: float | None
    exempt_land: float | None
    exterior_condition: str | None
    fireplaces: float | None
    frontage: float | None
    fuel: str | None
    garage_spaces: float | None
    garage_type: str | None
    general_construction: str | None
    geographic_ward: str | None
    homestead_exemption: float
    house_extension: str | None
    interior_condition: str | None
    mailing_address_1: str | None
    mailing_address_2: str | None
    mailing_care_of: str | None
    mailing_city_state: str | None
    mailing_street: str | None
    mailing_zip: str | None
    market_value: float | None
    market_value_date: date | None
    number_of_bathrooms: float | None
    number_of_bedrooms: float | None
    number_of_rooms: float | None
    number_stories: float | None
    off_street_open: float | None
    other_building: str | None
    parcel_shape: str | None
    quality_grade: str | None
    recording_date: datetime | None
    registry_number: str | None
    sale_date: str | None  # '202-02-11T04:56:00Z'
    sale_price: float | None
    separate_utilities: str | None
    sewer: str | None
    site_type: str | None
    state_code: str | None
    street_code: str | None
    street_designation: str | None
    street_direction: str | None
    suffix: str | None
    taxable_building: float | None
    taxable_land: float | None
    topography: str | None
    total_area: float | None
    total_livable_area: float | None
    type_heater: str | None
    unfinished: str | None
    unit: str | None
    utility: str | None
    view_type: str | None
    year_built: str | None
    year_built_estimate: str | None
    zoning: str | None
    building_code_new: str | None
    building_code_description_new: str | None
    # Computed from the_geom
    lat: float | None
    lng: float | None


class BusinessLicenses(SQLModel, table=True):
    __tablename__: str = "business_licenses"

    @property
    def split_by(self) -> tuple[str, str]:
        return ("initialissuedate", "year")

    cartodb_id: int = Field(primary_key=True)
    objectid: int = Field(primary_key=True)
    posse_jobid: str = Field(primary_key=True)
    licensenum: str = Field(primary_key=True)
    the_geom: str
    revenuecode: str
    licensetype: str
    initialissuedate: str
    mostrecentissuedate: str
    licensestatus: str
    legalname: str | None
    addressobjectid: float | None
    the_geom_webmercator: str | None
    address: str | None
    unit_type: str | None
    unit_num: str | None
    zip: str | None
    censustract: str | None
    parcel_id_num: str | None
    opa_account_num: str | None
    opa_owner: str | None
    rentalcategory: str | None
    legalentitytype: str | None
    business_name: str | None
    business_mailing_address: str | None
    expirationdate: str | None
    inactivedate: str | None
    numberofunits: float | None
    owneroccupied: str | None
    legalfirstname: str | None
    legallastname: str | None
    ownercontact1name: str | None
    ownercontact1mailingaddress: str | None
    ownercontact1city: str | None
    ownercontact1state: str | None
    ownercontact1zippostalcode: str | None
    ownercontact2name: str | None
    ownercontact2mailingaddress: str | None
    ownercontact2city: str | None
    ownercontact2state: str | None
    ownercontact2zippostalcode: str | None
    geocode_x: float | None
    geocode_y: float | None
    council_district: str | None
    # Computed from the_geom
    lat: float | None
    lng: float | None


class RttSummary(SQLModel, table=True):
    __tablename__ = "rtt_summary"

    @property
    def split_by(self) -> tuple[str, str]:
        return ("recording_date", "year")

    cartodb_id: int = Field(primary_key=True)
    objectid: float = Field(primary_key=True)
    record_id: str = Field(primary_key=True)
    property_count: float
    recording_date: datetime | None
    document_id: float
    the_geom: str | None
    address_low: int | None
    display_date: (
        str | None
    )  # '171-10-19T05:00:00Z', '218-03-28T05:00:00Z', '118-06-01T05:00:00Z',
    document_type: str | None
    street_name: str | None
    street_address: str | None
    the_geom_webmercator: str | None
    ward: str | None
    grantees: str | None = Field(index=True)
    grantors: str | None = Field(index=True)
    reg_map_id: str | None
    opa_account_num: str | None
    receipt_date: str | None
    address_high: str | None
    address_low_frac: str | None
    address_low_suffix: str | None
    adjusted_assessed_value: float | None
    adjusted_cash_consideration: float | None
    adjusted_fair_market_value: float | None
    adjusted_local_tax_amount: float | None
    adjusted_other_consideration: float | None
    adjusted_state_tax_amount: float | None
    adjusted_total_consideration: float | None
    assessed_value: float | None
    cash_consideration: float | None
    common_level_ratio: float | None
    condo_name: str | None
    discrepancy: str | None
    document_date: str | None  # '171-10-19T05:00:00Z'
    fair_market_value: float | None
    legal_remarks: str | None
    local_tax_amount: float | None
    local_tax_percent: float | None
    matched_regmap: str | None
    other_consideration: float | None
    receipt_num: str | None
    state_tax_amount: float | None
    state_tax_percent: float | None
    total_consideration: float | None
    street_predir: str | None
    street_suffix: str | None
    street_postdir: str | None
    unit_num: str | None
    zip_code: str | None
    # Computed from the_geom
    lat: float | None
    lng: float | None


class CarPedStops(SQLModel, table=True):
    __tablename__ = "car_ped_stops"

    @property
    def split_by(self) -> tuple[str, str]:
        return ("datetimeoccur", "year")

    cartodb_id: int = Field(primary_key=True)
    objectid: int = Field(primary_key=True)
    id: int = Field(primary_key=True)
    datetimeoccur: datetime
    weekday: str
    location: str
    districtoccur: str | None
    psa: str | None
    stopcode: int
    stoptype: str
    inside_or_outside: str
    gender: str | None
    race: str
    age: int | None
    individual_frisked: int
    individual_searched: int
    individual_arrested: int
    individual_contraband: int
    vehicle_frisked: int
    vehicle_searched: int
    vehicle_contraband: int
    vehicle_contraband_list: str | None
    individual_contraband_list: str | None
    mvc_code: str | None
    mvc_reason: str | None
    mvc_code_sec: str | None
    mvc_code_sec_reason: str | None
    point_x: float | None
    point_y: float | None
    the_geom: str | None  # Store as WKT (Well-Known Text)
    the_geom_webmercator: str | None  # Store as WKT (Well-Known Text)
    # Computed from the_geom
    lat: float | None
    lng: float | None

    @validator("datetimeoccur", pre=True)
    def parse_datetimeoccur(cls, value):
        if isinstance(value, str):
            # Assuming the string is in ISO 8601 format, remove 'Z' if present and convert
            return datetime.fromisoformat(value.rstrip("Z"))
        return value


class Shootings(SQLModel, table=True):
    cartodb_id: int = Field(primary_key=True)
    objectid: int = Field(primary_key=True)
    date_: datetime | None = Field(primary_key=True)
    location: str = Field(primary_key=True)
    the_geom: str | None
    the_geom_webmercator: str | None
    year: int | None
    dc_key: str | None
    code: str | None
    time: str | None
    race: str | None
    sex: str | None
    age: str | None
    wound: str | None
    officer_involved: str | None
    offender_injured: str | None
    offender_deceased: str | None
    latino: int | None
    point_x: float | None
    point_y: float | None
    dist: str | None
    inside: int | None
    outside: int | None
    fatal: int | None
    # Computed from the_geom
    lat: float | None
    lng: float | None

    @validator("date_", pre=True)
    def parse_datetimeoccur(cls, value):
        if isinstance(value, str):
            # Assuming the string is in ISO 8601 format, remove 'Z' if present and convert
            return datetime.fromisoformat(value.rstrip("Z"))
        return value
