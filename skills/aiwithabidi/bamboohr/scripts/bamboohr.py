#!/usr/bin/env python3
"""BambooHR CLI — BambooHR — manage employees, time-off, reports, and company info via REST API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://api.bamboohr.com/api/gateway.php/{subdomain}/v1"

def get_env(name):
    val = os.environ.get(name, "")
    if not val:
        env_path = os.path.join(os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(name + "="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not val:
        print(f"Error: {name} not set", file=sys.stderr)
        sys.exit(1)
    return val


def get_headers():
    import base64
    key = get_env("BAMBOOHR_API_KEY")
    secret = get_env("BAMBOOHR_SUBDOMAIN") if "BAMBOOHR_SUBDOMAIN" else ""
    creds = base64.b64encode(f"{key}:{secret}".encode()).decode()
    return {"Authorization": f"Basic {creds}", "Content-Type": "application/json", "Accept": "application/json"}



def get_api_base():
    base = API_BASE
    base = base.replace("{subdomain}", get_env("BAMBOOHR_SUBDOMAIN"))
    return base

def req(method, path, data=None, params=None):
    headers = get_headers()
    if path.startswith("http"):
        url = path
    else:
        url = get_api_base() + path
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if qs:
            url = f"{url}?{qs}" if "?" not in url else f"{url}&{qs}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    for k, v in headers.items():
        r.add_header(k, v)
    try:
        resp = urllib.request.urlopen(r, timeout=30)
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {"ok": True}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(json.dumps({"error": True, "code": e.code, "message": err_body}), file=sys.stderr)
        sys.exit(1)


def try_json(val):
    if val is None:
        return None
    try:
        return json.loads(val)
    except (json.JSONDecodeError, ValueError):
        return val


def out(data, human=False):
    if human and isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
    elif human and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"  {k}: {v}")
                print()
            else:
                print(item)
    else:
        print(json.dumps(data, indent=2, default=str))


def cmd_employees(args):
    """List employees."""
    path = "/employees/directory"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_employee_get(args):
    """Get employee."""
    path = f"/employees/{args.id}/"
    params = {}
    if getattr(args, "fields", None): params["fields"] = args.fields
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_employee_create(args):
    """Create employee."""
    path = "/employees/"
    body = {}
    if getattr(args, "firstName", None): body["firstName"] = try_json(args.firstName)
    if getattr(args, "lastName", None): body["lastName"] = try_json(args.lastName)
    if getattr(args, "workEmail", None): body["workEmail"] = try_json(args.workEmail)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_employee_update(args):
    """Update employee."""
    path = f"/employees/{args.id}/"
    body = {}
    if getattr(args, "fields", None): body["fields"] = try_json(args.fields)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_employee_files(args):
    """List employee files."""
    path = f"/employees/{args.id}/files/view/"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_time_off_requests(args):
    """List time-off requests."""
    path = "/time_off/requests/"
    params = {}
    if getattr(args, "start", None): params["start"] = args.start
    if getattr(args, "end", None): params["end"] = args.end
    if getattr(args, "status", None): params["status"] = args.status
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_time_off_types(args):
    """List time-off types."""
    path = "/meta/time_off/types/"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_whois_out(args):
    """Who is out."""
    path = "/time_off/whos_out/"
    params = {}
    if getattr(args, "start", None): params["start"] = args.start
    if getattr(args, "end", None): params["end"] = args.end
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_reports(args):
    """Run report."""
    path = f"/reports/{args.id}"
    params = {}
    if getattr(args, "format", None): params["format"] = args.format
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_fields(args):
    """List fields."""
    path = "/meta/fields/"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_tables(args):
    """List tables."""
    path = f"/employees/{args.id}/tables/"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_table_get(args):
    """Get table data."""
    path = f"/employees/{args.id}/tables/{args.table}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_changed(args):
    """Changed employees."""
    path = "/employees/changed/"
    params = {}
    if getattr(args, "since", None): params["since"] = args.since
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="BambooHR CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    employees_p = sub.add_parser("employees", help="List employees")
    employees_p.set_defaults(func=cmd_employees)

    employee_get_p = sub.add_parser("employee-get", help="Get employee")
    employee_get_p.add_argument("id", help="Employee ID")
    employee_get_p.add_argument("--fields", help="Fields CSV", default=None)
    employee_get_p.set_defaults(func=cmd_employee_get)

    employee_create_p = sub.add_parser("employee-create", help="Create employee")
    employee_create_p.add_argument("--firstName", help="First name", default=None)
    employee_create_p.add_argument("--lastName", help="Last name", default=None)
    employee_create_p.add_argument("--workEmail", help="Email", default=None)
    employee_create_p.set_defaults(func=cmd_employee_create)

    employee_update_p = sub.add_parser("employee-update", help="Update employee")
    employee_update_p.add_argument("id", help="Employee ID")
    employee_update_p.add_argument("--fields", help="JSON fields", default=None)
    employee_update_p.set_defaults(func=cmd_employee_update)

    employee_files_p = sub.add_parser("employee-files", help="List employee files")
    employee_files_p.add_argument("id", help="Employee ID")
    employee_files_p.set_defaults(func=cmd_employee_files)

    time_off_requests_p = sub.add_parser("time-off-requests", help="List time-off requests")
    time_off_requests_p.add_argument("--start", help="Start date", default=None)
    time_off_requests_p.add_argument("--end", help="End date", default=None)
    time_off_requests_p.add_argument("--status", help="Status", default=None)
    time_off_requests_p.set_defaults(func=cmd_time_off_requests)

    time_off_types_p = sub.add_parser("time-off-types", help="List time-off types")
    time_off_types_p.set_defaults(func=cmd_time_off_types)

    whois_out_p = sub.add_parser("whois-out", help="Who is out")
    whois_out_p.add_argument("--start", help="Start", default=None)
    whois_out_p.add_argument("--end", help="End", default=None)
    whois_out_p.set_defaults(func=cmd_whois_out)

    reports_p = sub.add_parser("reports", help="Run report")
    reports_p.add_argument("id", help="Report ID")
    reports_p.add_argument("--format", help="JSON/CSV", default=None)
    reports_p.set_defaults(func=cmd_reports)

    fields_p = sub.add_parser("fields", help="List fields")
    fields_p.set_defaults(func=cmd_fields)

    tables_p = sub.add_parser("tables", help="List tables")
    tables_p.add_argument("id", help="Employee ID")
    tables_p.set_defaults(func=cmd_tables)

    table_get_p = sub.add_parser("table-get", help="Get table data")
    table_get_p.add_argument("id", help="Employee ID")
    table_get_p.add_argument("table", help="Table name")
    table_get_p.set_defaults(func=cmd_table_get)

    changed_p = sub.add_parser("changed", help="Changed employees")
    changed_p.add_argument("--since", help="ISO datetime", default=None)
    changed_p.set_defaults(func=cmd_changed)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
