## 1.3 (Unreleased)

FEATURES:

* collector.py: Add `current_requests` metric (Enhanced Health Reporting)
* collector.py: Add `http_requests` metric per status code (Enhanced Health Reporting)
* collector.py: Add `load_average` metric per instance (Enhanced Health Reporting)
* collector.py: Add `cpu_usage` metric per instance (Enhanced Health Reporting)

IMPROVEMENT:

* collector/py: Ignore terminated environment
* Repository: Add CHANGELOG.md

## 1.2 (April 11, 2019)

BUG FIXES:

* collector.py: Prevent error `KeyError: 'Description'` when description is empty for an application

## 1.1 (March 22, 2019)

IMPROVEMENT:

* collector.py: Add environment status metric based on `health` label and update suffix into `environment_status`
* collector.py: Update description of application metric

## 1.0 (March 18, 2019)

First release

FEATURES:

* Add environment and application metrics