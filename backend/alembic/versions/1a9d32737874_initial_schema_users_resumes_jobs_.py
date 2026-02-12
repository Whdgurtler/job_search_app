"""Initial schema - users, resumes, jobs, scrape_configs, scrape_runs

Revision ID: 1a9d32737874
Revises: 
Create Date: 2026-02-12 17:11:14.259577
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = '1a9d32737874'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('firebase_uid', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('quota_scrapes_per_day', sa.Integer(), server_default='5', nullable=False),
        sa.Column('plan', sa.String(), server_default="'free'", nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('firebase_uid'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_firebase_uid', 'users', ['firebase_uid'])
    op.create_index('idx_users_email', 'users', ['email'])

    # Create resumes table
    op.create_table(
        'resumes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('parsed_at', sa.DateTime(), nullable=True),
        sa.Column('parsed_data', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_resumes_user_id', 'resumes', ['user_id'])
    op.create_index('idx_resumes_is_active', 'resumes', ['is_active'])

    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('posted_date', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('remote', sa.Boolean(), nullable=True),
        sa.Column('salary', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('qualifications', sa.Text(), nullable=True),
        sa.Column('match_score', sa.Float(), nullable=True),
        sa.Column('recommendation', sa.String(), nullable=True),
        sa.Column('match_details', sa.JSON(), nullable=True),
        sa.Column('scraped_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('bookmarked', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_jobs_user_id', 'jobs', ['user_id'])
    op.create_index('idx_jobs_company', 'jobs', ['company'])
    op.create_index('idx_jobs_scraped_at', 'jobs', ['scraped_at'])
    op.create_index('idx_jobs_match_score', 'jobs', ['match_score'])
    op.create_index('idx_jobs_recommendation', 'jobs', ['recommendation'])
    op.create_index('idx_jobs_bookmarked', 'jobs', ['bookmarked'])
    op.create_index('idx_jobs_url', 'jobs', ['url'])

    # Create scrape_configs table
    op.create_table(
        'scrape_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('companies', sa.ARRAY(sa.String()), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_scrape_configs_user_id', 'scrape_configs', ['user_id'])

    # Create scrape_runs table
    op.create_table(
        'scrape_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), server_default="'pending'", nullable=False),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('jobs_found', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('celery_task_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['config_id'], ['scrape_configs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_scrape_runs_user_id', 'scrape_runs', ['user_id'])
    op.create_index('idx_scrape_runs_status', 'scrape_runs', ['status'])
    op.create_index('idx_scrape_runs_started_at', 'scrape_runs', ['started_at'])


def downgrade() -> None:
    op.drop_index('idx_scrape_runs_started_at', table_name='scrape_runs')
    op.drop_index('idx_scrape_runs_status', table_name='scrape_runs')
    op.drop_index('idx_scrape_runs_user_id', table_name='scrape_runs')
    op.drop_table('scrape_runs')
    
    op.drop_index('idx_scrape_configs_user_id', table_name='scrape_configs')
    op.drop_table('scrape_configs')
    
    op.drop_index('idx_jobs_url', table_name='jobs')
    op.drop_index('idx_jobs_bookmarked', table_name='jobs')
    op.drop_index('idx_jobs_recommendation', table_name='jobs')
    op.drop_index('idx_jobs_match_score', table_name='jobs')
    op.drop_index('idx_jobs_scraped_at', table_name='jobs')
    op.drop_index('idx_jobs_company', table_name='jobs')
    op.drop_index('idx_jobs_user_id', table_name='jobs')
    op.drop_table('jobs')
    
    op.drop_index('idx_resumes_is_active', table_name='resumes')
    op.drop_index('idx_resumes_user_id', table_name='resumes')
    op.drop_table('resumes')
    
    op.drop_index('idx_users_email', table_name='users')
    op.drop_index('idx_users_firebase_uid', table_name='users')
    op.drop_table('users')
