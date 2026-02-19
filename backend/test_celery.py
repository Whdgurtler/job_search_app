#!/usr/bin/env python
"""Test Celery task registration"""
import sys
sys.path.insert(0, ".")

from app.tasks import celery_app, run_scrape

print("Celery App:", celery_app)
print("\nRegistered tasks:")
for task_name in sorted(celery_app.tasks.keys()):
    print(f"  - {task_name}")

print("\nScrape task:", run_scrape)
