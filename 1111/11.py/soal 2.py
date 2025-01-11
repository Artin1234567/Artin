@app.route('/scrape', methods=['POST'])
def scrape_and_save():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    # Scraping the URL content
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve the URL"}), 500
    
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string if soup.title else 'No title'
    description = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
    description = description['content'] if description else 'No description available'

    # Check if URL already exists
    existing_url = URLData.query.filter_by(url=url).first()
    if existing_url:
        return jsonify({"message": "URL already exists"}), 400

    # Save data to DB
    new_data = URLData(url=url, title=title, description=description)
    db.session.add(new_data)
    db.session.commit()

    return jsonify({"message": "Data saved successfully!"}), 201
@app.route('/get', methods=['GET'])
def get_url_data():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    data = URLData.query.filter_by(url=url).first()
    if not data:
        return jsonify({"error": "Data not found"}), 404

    return jsonify({
        "url": data.url,
        "title": data.title,
        "description": data.description
    })
@app.route('/all', methods=['GET'])
def get_all_urls():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    data = URLData.query.paginate(page, per_page, False)
    
    results = []
    for item in data.items:
        results.append({
            "url": item.url,
            "title": item.title,
            "description": item.description
        })
    
    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": data.total,
        "data": results
    })
@app.route('/delete', methods=['DELETE'])
def delete_url_data():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    data = URLData.query.filter_by(url=url).first()
    if not data:
        return jsonify({"error": "Data not found"}), 404

    db.session.delete(data)
    db.session.commit()

    return jsonify({"message": "Data deleted successfully!"}), 200
@app.route('/count', methods=['GET'])
def count_records():
    count = URLData.query.count()
    return jsonify({"record_count": count})
