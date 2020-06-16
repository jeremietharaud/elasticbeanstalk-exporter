## 1.5 (June 16, 2020)
BUG FIXES:

* collector.py: Prevent error `KeyError: 'LoadAverage'` when LoadAverage is empty for an application (for example when the environment is under creation)

## 1.4 (January 8, 2020)

ENHANCEMENTS:

* flake8 on python files

## 1.3 (May 28, 2019)

FEATURES:

* collector.py: Add `enhanced_global_current_requests` overall metric (Enhanced Health Reporting)
* collector.py: Add `enhanced_global_http_requests_percent` overall metric per status code (Enhanced Health Reporting)
* collector.py: Add `enhanced_current_requests` metric per instance (Enhanced Health Reporting)
* collector.py: Add `enhanced_http_requests_percent` metric per instance and status code (Enhanced Health Reporting)
* collector.py: Add `enhanced_load_average` metric per instance (Enhanced Health Reporting)
* collector.py: Add `enhanced_cpu_usage_percent` metric per instance (Enhanced Health Reporting)
* collector.py: Add `enhanced_health_status` metric per health status (Enhanced Health Reporting)
* collector.py: Add `enhanced_status` metric per status (Enhanced Health Reporting)
* collector.py: Add `collector_duration_seconds` metric

ENHANCEMENTS:

* collector.py: Ignore terminated environment
* Repository: Add CHANGELOG.md

BUG FIXES:

* collector.py: Prevent error `KeyError: 'CNAME'` when url is empty for an environment (for example when the environment is under creation)

## 1.2 (April 12, 2019)

BUG FIXES:

* collector.py: Prevent error `KeyError: 'Description'` when description is empty for an application

## 1.1 (March 22, 2019)

ENHANCEMENTS:

* collector.py: Add environment status metric based on `health` label and update suffix into `environment_status`
* collector.py: Update description of application metric

## 1.0 (March 18, 2019)

First release

FEATURES:

* Add environment and application metrics