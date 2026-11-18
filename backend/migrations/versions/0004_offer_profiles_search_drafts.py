"""Add offer profiles and normalized multi-location search drafts."""

from alembic import op
import sqlalchemy as sa


revision = "0004_prospecting"
down_revision = "0003_user_onboarding"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "offer_profiles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("service_name", sa.String(120), nullable=False),
        sa.Column("outreach_language", sa.String(35), nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "btrim(service_name) <> ''",
            name="ck_offer_profiles_service_name",
        ),
        sa.CheckConstraint(
            "btrim(outreach_language) <> ''",
            name="ck_offer_profiles_outreach_language",
        ),
        sa.UniqueConstraint("id", "user_id", name="uq_offer_profiles_id_user_id"),
    )
    op.create_index("ix_offer_profiles_user_id", "offer_profiles", ["user_id"])
    op.create_index(
        "uq_offer_profiles_default_per_user",
        "offer_profiles",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_default"),
    )

    op.create_table(
        "search_drafts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("offer_profile_id", sa.Uuid(), nullable=False),
        sa.Column("business_category", sa.String(150), nullable=False),
        sa.Column("result_limit_per_location", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["offer_profile_id", "user_id"],
            ["offer_profiles.id", "offer_profiles.user_id"],
            name="fk_search_drafts_offer_owner",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "btrim(business_category) <> ''",
            name="ck_search_drafts_business_category",
        ),
        sa.CheckConstraint(
            "result_limit_per_location IS NULL OR result_limit_per_location > 0",
            name="ck_search_drafts_positive_result_limit",
        ),
    )
    op.create_index("ix_search_drafts_user_id", "search_drafts", ["user_id"])
    op.create_index(
        "ix_search_drafts_offer_profile_id",
        "search_drafts",
        ["offer_profile_id"],
    )

    op.create_table(
        "search_draft_locations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "search_draft_id",
            sa.Uuid(),
            sa.ForeignKey("search_drafts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("location_query", sa.String(200), nullable=False),
        sa.Column("normalized_location", sa.String(200), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "btrim(location_query) <> ''",
            name="ck_search_draft_locations_query",
        ),
        sa.CheckConstraint(
            "btrim(normalized_location) <> ''",
            name="ck_search_draft_locations_normalized",
        ),
        sa.CheckConstraint(
            "position BETWEEN 1 AND 10",
            name="ck_search_draft_locations_position",
        ),
        sa.UniqueConstraint(
            "search_draft_id",
            "normalized_location",
            name="uq_search_draft_locations_normalized",
        ),
        sa.UniqueConstraint(
            "search_draft_id",
            "position",
            name="uq_search_draft_locations_position",
        ),
    )
    op.create_index(
        "ix_search_draft_locations_search_draft_id",
        "search_draft_locations",
        ["search_draft_id"],
    )


def downgrade():
    op.drop_table("search_draft_locations")
    op.drop_table("search_drafts")
    op.drop_table("offer_profiles")
