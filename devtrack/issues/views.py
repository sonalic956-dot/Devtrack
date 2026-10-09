import json
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Reporter, Issue, CriticalIssue, LowPriorityIssue

REPORTERS_FILE = os.path.join(settings.BASE_DIR, 'reporters.json')
ISSUES_FILE = os.path.join(settings.BASE_DIR, 'issues.json')

def load_json_file(filepath):
    print(f"\n--- DJANGO LOOKING FOR FILE AT: {filepath} ---\n")
    if not os.path.exists(filepath):
        print(f"File does not exist at {filepath}")
        return []
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            print(f"LOADED DATA ({len(data)} items): {data}")
            return data
    except json.JSONDecodeError as e:
        print(f"JSON DECODE ERROR in {filepath}: {e}")
        return []


def save_json_file(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)


@csrf_exempt
def reporters_api(request):
    if request.method == 'GET':
        reporters = load_json_file(REPORTERS_FILE)
        raw_id = request.GET.get('id')
        if raw_id is not None:
            try:
                target_id = int(raw_id)
                matched = [r for r in reporters if r.get('id') == target_id]
                if matched:
                    return JsonResponse(matched[0])
                return JsonResponse({'error': 'Reporter not found'}, status=404)
            except ValueError:
                return JsonResponse({'error': 'Invalid ID format'}, status=400)
        return JsonResponse(reporters, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            reporters = load_json_file(REPORTERS_FILE)
            new_id = data.get('id') or (max([r.get('id', 0) for r in reporters], default=0) + 1)

            reporter = Reporter(
                id=new_id,
                name=data.get('name', ''),
                email=data.get('email', ''),
                team=data.get('team', '')
            )
            reporter.validate()

            reporter_dict = reporter.to_dict()
            reporters.append(reporter_dict)
            save_json_file(REPORTERS_FILE, reporters)

            return JsonResponse(reporter_dict, status=201)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def issues_api(request):
    if request.method == 'GET':
        issues = load_json_file(ISSUES_FILE)

        # GET /api/issues/?id=1
        raw_id = request.GET.get('id')
        if raw_id is not None:
            try:
                target_id = int(raw_id)
                matched = [i for i in issues if i.get('id') == target_id]
                if matched:
                    return JsonResponse(matched[0])
                return JsonResponse({'error': 'Issue not found'}, status=404)
            except ValueError:
                return JsonResponse({'error': 'Invalid ID format'}, status=400)

        # GET /api/issues/?status=open
        status_filter = request.GET.get('status')
        if status_filter:
            issues = [i for i in issues if i.get('status') == status_filter]

        return JsonResponse(issues, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            issues = load_json_file(ISSUES_FILE)
            new_id = data.get('id') or (max([i.get('id', 0) for i in issues], default=0) + 1)
            priority = str(data.get('priority', 'medium')).lower()

            if priority == 'critical':
                issue = CriticalIssue(
                    id=new_id,
                    title=data.get('title', ''),
                    description=data.get('description', ''),
                    status=data.get('status', 'open'),
                    reporter_id=data.get('reporter_id')
                )
            elif priority == 'low':
                issue = LowPriorityIssue(
                    id=new_id,
                    title=data.get('title', ''),
                    description=data.get('description', ''),
                    status=data.get('status', 'open'),
                    reporter_id=data.get('reporter_id')
                )
            else:
                issue = Issue(
                    id=new_id,
                    title=data.get('title', ''),
                    description=data.get('description', ''),
                    status=data.get('status', 'open'),
                    priority=priority,
                    reporter_id=data.get('reporter_id')
                )

            issue.validate()

            response_data = issue.to_dict()
            response_data['message'] = issue.describe()

            issues.append(response_data)
            save_json_file(ISSUES_FILE, issues)

            return JsonResponse(response_data, status=201)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    elif request.method == 'DELETE':
        issue_id = request.GET.get('id')
        if not issue_id:
            return JsonResponse({'error': 'ID parameter required'}, status=400)
        
        try:
            target_id = int(issue_id)
        except ValueError:
            return JsonResponse({'error': 'Invalid ID format'}, status=400)

        issues = load_json_file(ISSUES_FILE)
        filtered_issues = [i for i in issues if i.get('id') != target_id]

        if len(issues) == len(filtered_issues):
            return JsonResponse({'error': 'Issue not found'}, status=404)

        save_json_file(ISSUES_FILE, filtered_issues)
        return JsonResponse({'message': f'Issue {target_id} deleted successfully'}, status=200)

    return JsonResponse({'error': 'Method not allowed'}, status=405)