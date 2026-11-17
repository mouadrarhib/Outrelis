"""Add full name without inventing names for existing accounts."""
from alembic import op
import sqlalchemy as sa

revision = "0002_user_full_name"
down_revision = "0001_authentication"
branch_labels = None
depends_on = None


def upgrade():
    # New registrations require a name; pre-existing accounts retain null.
    op.add_column("users", sa.Column("full_name", sa.String(100), nullable=True))


def downgrade():
    op.drop_column("users", "full_name")
