import pandas as pd
from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta

# Load CSV files
try:
    containers_df = pd.read_csv('containers.csv')
    items_df = pd.read_csv('input_items.csv', dtype={'item_id': str})
except FileNotFoundError as e:
    print(f"Error: {e}. Please ensure containers.csv and input_items.csv are in the folder.")
    exit(1)

# Initialize containers and items dictionaries
containers = {}
for _, row in containers_df.iterrows():
    containers[row['container_id']] = {
        'zone': row['zone'],
        'width': row['width_cm'],
        'depth': row['depth_cm'],
        'height': row['height_cm'],
        'items': []
    }

items = {}
for _, row in items_df.iterrows():
    items[row['item_id']] = {
        'name': row['name'],
        'width': row['width_cm'],
        'depth': row['depth_cm'],
        'height': row['height_cm'],
        'mass': row['mass_kg'],
        'priority': row['priority'],
        'expiry_date': row['expiry_date'] if row['expiry_date'] != 'N/A' else None,
        'usage_limit': row['usage_limit'],
        'preferred_zone': row['preferred_zone'],
        'container': None
    }
print("Loaded item IDs:", list(items.keys()))

# Placement function with enhanced debug
def place_item(item_id):
    if item_id not in items:
        return {"status": "error", "message": "Item not found"}
    item = items[item_id]
    best_container = None
    best_score = -1
    for container_id, container in containers.items():
        total_mass = sum(items[i]['mass'] for i in container.get('items', [])) if container.get('items') else 0
        if (item['width'] <= container['width'] and 
            item['depth'] <= container['depth'] and 
            item['height'] <= container['height'] and 
            len(container['items']) < 10 and
            total_mass + item['mass'] <= 100):
            score = 0
            if container['zone'] == item['preferred_zone']:
                score += 100
            score += item['priority']
            if score > best_score:
                best_score = score
                best_container = container_id
    if best_container:
        containers[best_container]['items'].append(item_id)
        items[item_id]['container'] = best_container
        print(f"Item {item_id} placed in {best_container}")
        return {"status": "success", "container_id": best_container}
    print(f"No suitable container found for {item_id}")
    return {"status": "error", "message": "No suitable container found"}

# Search function
def search_item(query):
    results = []
    for item_id, item in items.items():
        if query in item_id or query.lower() in item['name'].lower():
            results.append({
                'item_id': item_id,
                'name': item['name'],
                'container': item['container']
            })
    return results if results else {"status": "error", "message": "Item not found"}

# Retrieve function
def retrieve_item(item_id):
    if item_id not in items:
        return {"status": "error", "message": "Item not found"}
    item = items[item_id]
    container_id = item['container']
    if container_id and item_id in containers[container_id]['items']:
        containers[container_id]['items'].remove(item_id)
        items[item_id]['container'] = None
        return {"status": "success", "item_id": item_id}
    return {"status": "error", "message": "Item not in any container"}

# Waste identify function
def identify_waste():
    current_date = datetime.now()
    waste_items = []
    for item_id, item in items.items():
        if item['expiry_date']:
            if isinstance(item['expiry_date'], str):
                expiry = datetime.strptime(item['expiry_date'], '%Y-%m-%d')
                if expiry < current_date:
                    waste_items.append(item_id)
            else:
                print(f"Warning: {item_id} ka expiry_date galat hai: {item['expiry_date']}")
    return waste_items

# Waste return plan function
def waste_return_plan():
    waste = identify_waste()
    return {"return_plan": waste, "status": "success"}

# Waste complete undocking function
def waste_complete_undocking():
    waste = identify_waste()
    for item_id in waste:
        if items[item_id]['container']:
            containers[items[item_id]['container']]['items'].remove(item_id)
            items[item_id]['container'] = None
    return {"status": "success", "undocked": waste}

# Import items function
def import_items(data):
    for item in data:
        items[item['item_id']] = item
    return {"status": "success", "imported": len(data)}

# Import containers function
def import_containers(data):
    for container in data:
        containers[container['container_id']] = container
    return {"status": "success", "imported": len(data)}

# Export arrangement function
def export_arrangement():
    arrangement = {cid: c['items'] for cid, c in containers.items()}
    return {"arrangement": arrangement, "status": "success"}

# Simulate day function with waste removal
def simulate_day():
    current_date = datetime.now()
    waste_removed = []
    for item_id, item in items.items():
        if item['expiry_date']:
            if isinstance(item['expiry_date'], str):
                expiry = datetime.strptime(item['expiry_date'], '%Y-%m-%d')
                if expiry < current_date:
                    if item['container'] and item_id in containers[item['container']]['items']:
                        containers[item['container']]['items'].remove(item_id)
                        waste_removed.append(item_id)
                    items[item_id]['container'] = None
    return {"status": "success", "message": "Day simulated", "waste_removed": waste_removed}

# Simple logging function
def get_logs():
    return {"logs": [f"Item {item_id} placed in {containers.get(items[item_id]['container'], 'None')} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" for item_id in items if items[item_id]['container']], "status": "success"}

# Flask app setup
app = Flask(__name__)

@app.route('/api/placement', methods=['GET', 'POST'])
def api_placement():
    if request.method == 'POST':
        item_id = request.json.get('item_id')
        result = place_item(item_id)
        return jsonify(result)
    elif request.method == 'GET':
        return jsonify({"message": "Use POST method with JSON body {'item_id': '000001'} to place an item.", "status": "info"})

@app.route('/api/search', methods=['GET'])
def api_search():
    query = request.args.get('query')
    result = search_item(query)
    return jsonify(result)

@app.route('/api/retrieve', methods=['POST'])
def api_retrieve():
    item_id = request.json.get('item_id')
    result = retrieve_item(item_id)
    return jsonify(result)

@app.route('/api/waste/identify', methods=['GET'])
def api_waste_identify():
    waste = identify_waste()
    return jsonify({"waste_items": waste})

@app.route('/api/waste/return-plan', methods=['GET'])
def api_waste_return_plan():
    result = waste_return_plan()
    return jsonify(result)

@app.route('/api/waste/complete-undocking', methods=['POST'])
def api_waste_complete_undocking():
    result = waste_complete_undocking()
    return jsonify(result)

@app.route('/api/import/items', methods=['POST'])
def api_import_items():
    data = request.json.get('items', [])
    result = import_items(data)
    return jsonify(result)

@app.route('/api/import/containers', methods=['POST'])
def api_import_containers():
    data = request.json.get('containers', [])
    result = import_containers(data)
    return jsonify(result)

@app.route('/api/export/arrangement', methods=['GET'])
def api_export_arrangement():
    result = export_arrangement()
    return jsonify(result)

@app.route('/api/simulate/day', methods=['POST'])
def api_simulate_day():
    result = simulate_day()
    return jsonify(result)

@app.route('/api/logs', methods=['GET'])
def api_logs():
    result = get_logs()
    return jsonify(result)

@app.route('/')
def home():
    sample_items = list(items.keys())[:5]  # First 5 items as sample
    return render_template('index.html', items=sample_items)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
