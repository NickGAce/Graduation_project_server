from sqlalchemy import Table, Column, Integer, Float, Date, ForeignKey, MetaData

from app.database import metadata

residents_ratings = Table(
    "residents_ratings",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("resident_id", Integer, ForeignKey("residents.id"), nullable=False),
    Column("achievement_score", Float, nullable=True),
    Column("infraction_score", Float, nullable=True),
    Column("overall_score", Float, nullable=False),
)


