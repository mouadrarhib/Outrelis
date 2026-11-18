"""Add the user's selected onboarding path."""

from alembic import op
import sqlalchemy as sa


revision = "0003_user_onboarding"
down_revision = "0002_user_full_name"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_onboarding",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("starting_path", sa.String(32), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
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
            "starting_path IN ('find_first_leads', 'grow_pipeline')",
            name="ck_user_onboarding_starting_path",
        ),
        sa.UniqueConstraint("user_id", name="uq_user_onboarding_user_id"),
    )


def downgrade():
    op.drop_table("user_onboarding")
