"""
config.py - Application Configuration
AICTE Activity & Points Management System

Contains database credentials, Flask settings, and path configurations.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()


# ==============================================================================
# Base directory of the application
# ==============================================================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# Flask Configuration
# ==============================================================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-secret-key-do-not-use-in-prod')
SESSION_TYPE = 'filesystem'
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour session timeout

# ==============================================================================
# MySQL Database Configuration
# ==============================================================================
MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'port': int(os.environ.get('MYSQL_PORT', 3306)),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DATABASE', 'aicte_db'),
    'pool_name': 'aicte_pool',
    'pool_size': 5,
    'autocommit': False
}

# ==============================================================================
# Upload / Generated File Paths
# ==============================================================================
QR_CODE_DIR = os.path.join(BASE_DIR, 'static', 'qrcodes')
CERTIFICATE_DIR = os.path.join(BASE_DIR, 'static', 'certificates')
REPORT_DIR = os.path.join(BASE_DIR, 'static', 'reports')

# Ensure directories exist
for directory in [QR_CODE_DIR, CERTIFICATE_DIR, REPORT_DIR]:
    os.makedirs(directory, exist_ok=True)

# ==============================================================================
# AICTE Points Configuration
# ==============================================================================
MAX_AICTE_POINTS = 100  # Target points for students

# ==============================================================================
# Application Settings
# ==============================================================================
ITEMS_PER_PAGE = 12
ALLOWED_CATEGORIES = ['technical', 'cultural', 'social', 'sports']
