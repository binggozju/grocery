#!/usr/bin/python

# configuration for development env
_dev_app_settings = {
        "kafka_hosts": "127.0.0.1:9092,127.0.0.1:9093",
        "zk_hosts": "127.0.0.1:2181",

        "api_log_consumer": {
            "topic": "api_monitor",
            "consumer_group": "api_monitor_group"
        },

        "log": {
            "log_consumer_app": {
                "home": "./logs/log_consumer_app/",
                "file": "log_consumer.log"
            },
            "report_generator_app": {
                "home": "./logs/report_generator_app/",
                "file": "report_generator.log"
            }
        },

        "report_receivers": "ybzhan@ibenben.com",
        "report": {
            "daily_report_dir": "./reports/daily_report/",
            "error_log_dir": "./reports/error_log/"
        }

    }


# configuration for production env
_app_settings = {
        "kafka_hosts": "10.168.72.226:9092,10.168.76.90:9092,10.168.59.183:9092",
        "zk_hosts": "10.168.72.226:2181,10.168.76.90:2181,10.168.59.183:2181",

        "api_log_consumer": {
            "topic": "api_monitor",
            "consumer_group": "api_monitor_group"
        },

        "log": {
            "log_consumer_app": {
                "home": "/data0/log_service/log_consumer_app/",
                "file": "log_consumer.log"
            },
            "report_generator_app": {
                "home": "/data0/log_service/report_generator_app/",
                "file": "report_generator.log"
            }
        },

        "report_receivers": "wms@ibenben.com",
        "report": {
            "daily_report_dir": "/data0/log_service/reports/daily_report/",
            "error_log_dir": "/data0/log_service/reports/error_log/"
        }

    }

def get_app_settings(env):
    if env == "dev":
        return _dev_app_settings
    elif env == "production":
        return _app_settings
    else:
        return None


if __name__ == "__main__":
    print _app_settings

