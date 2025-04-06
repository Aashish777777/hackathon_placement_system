import pandas as pd
from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import time  # Yeh add kar rha hoon slow requests ke liye

# Data load karo
containers_df = pd.read_csv('containers.csv')
items_df = pd.read_csv('input_items.csv', dtype={'item_id': str})

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
print("Loaded item IDs:", list(items.keys()))  # Yeh naya hai

# Placement function with enhanced debug
def place_item(item_id):
    print(f"Checking item: {item_id}, Exists: {item_id in items}")
    if item_id not in items:
        return {"status": "error", "message": "Item not found"}
    item = items[item_id]
    best_container = None
    best_score = -1
    total_mass = sum(items[i]['mass'] for i in containers.get(best_container, {}).get('items', [])) if best_container else 0
    for container_id, container in containers.items():
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

# Flask app setup
app = Flask(__name__)

@app.route('/api/placement', methods=['POST'])
def api_placement():
    item_id = request.json.get('item_id')
    result = place_item(item_id)
    time.sleep(0.1)  # Slow down responses to avoid overload
    return jsonify(result)

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

@app.route('/api/simulate/day', methods=['POST'])
def api_simulate_day():
    result = simulate_day()
    return jsonify(result)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)