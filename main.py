import random
import datetime
import json
import os
import argparse
from faker import Faker

fake = Faker()

# log levels with their distribution weights, while generating sample data.
LOG_LEVELS = {
    "INFO": 0.7,
    "WARN": 0.15,
    "ERROR": 0.1,
    "DEBUG": 0.05
}

# example micro-service names
SERVICES = ["api-gateway", "authentication", "payment-service", "user-service", "notification-service"]

ENDPOINTS = [
    "/api/users",
    "/api/products",
    "/api/orders",
    "/api/payments",
    "/api/login",
    "/api/logout",
    "/api/register",
    "/api/profile",
    "/api/settings"
]

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE"]

# status codes with their distribution weights
STATUS_CODES = {
    200: 0.75,
    201: 0.05,
    400: 0.08,
    401: 0.05,
    403: 0.02,
    404: 0.03,
    500: 0.02
}

def generate_log_entry(timestamp):

    level = random.choices(list(LOG_LEVELS.keys()), weights=list(LOG_LEVELS.values()))[0]
    service = random.choice(SERVICES)
    http_method = random.choice(HTTP_METHODS)
    endpoint = random.choice(ENDPOINTS)
    status_code = random.choices(list(STATUS_CODES.keys()), weights=list(STATUS_CODES.values()))[0]
    response_time = random.randint(5, 2000)
    request_id = fake.uuid4()
    user_agent = fake.user_agent()
    ip_address = fake.ipv4()
    
    if level == "ERROR" and status_code >= 500:
        message = "Request failed with internal server error: database connection timeout"
    elif level == "ERROR" or status_code >= 400:
        message = f"Request failed with client error: {fake.sentence()}"
    elif level == "WARN":
        message = f"Performance warning: operation took {response_time}ms which exceeds threshold"
    else:
        message = f"Successfully processed {http_method} request to {endpoint}"
    
    log_entry = {
        "timestamp": timestamp.isoformat(),
        "level": level,
        "service": service,
        "request_id": request_id,
        "http_method": http_method,
        "endpoint": endpoint,
        "status_code": status_code,
        "response_time_ms": response_time,
        "client_ip": ip_address,
        "user_agent": user_agent,
        "message": message
    }
    
    return log_entry

def generate_logs(start_date, days, entries_per_day, output_dir):
    """Generate logs for a given date range"""
    current_date = start_date
    
    for day in range(days):
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        day = current_date.strftime("%d")
        
        for service in SERVICES:
            directory = os.path.join(output_dir, service, year, month, day)
            os.makedirs(directory, exist_ok=True)
            
            logs = []
            for _ in range(entries_per_day // len(SERVICES)):
                hour = random.randint(0, 23)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                microsecond = random.randint(0, 999999)
                
                timestamp = datetime.datetime(
                    current_date.year, 
                    current_date.month, 
                    current_date.day,
                    hour, minute, second, microsecond
                )
                
                log_entry = generate_log_entry(timestamp)
                logs.append(log_entry)
            
            logs.sort(key=lambda x: x["timestamp"])
            
            filename = os.path.join(directory, f"logs_{service}_{year}{month}{day}.json")
            with open(filename, 'w') as f:
                for log in logs:
                    f.write(json.dumps(log) + "\n")
            
            print(f"Generated {len(logs)} logs for {service} on {year}-{month}-{day}")
        
        current_date += datetime.timedelta(days=1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate dummy application logs in JSON format')
    parser.add_argument('--start-date', type=str, default=datetime.date.today().strftime("%Y-%m-%d"),
                        help='Start date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--days', type=int, default=7,
                        help='Number of days to generate logs for (default: 7)')
    parser.add_argument('--entries', type=int, default=1000,
                        help='Approximate number of log entries per day (default: 1000)')
    parser.add_argument('--output-dir', type=str, default='./logs',
                        help='Output directory for log files (default: ./logs)')
    
    args = parser.parse_args()
    
    start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d").date()
    
    generate_logs(start_date, args.days, args.entries, args.output_dir)
    print(f"Log generation complete. Files are in {args.output_dir}")