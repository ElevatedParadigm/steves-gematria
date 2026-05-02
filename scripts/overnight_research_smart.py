    SIMILARITY_THRESHOLD = 0.35
    
    class DatabaseManager:
        def __init__(self, config):
            self.config = config
            self.db_path = config.DB_PATH
            self.initialize_database()
        
        def initialize_database(self):
            if not self.db_path.exists():
                logging.info(f"Creating database at {self.db_path}")
                data = {
                    'schema_version': self.config.SCHEMA_VERSION,
                    'symbols': [],
                    'results': [],
                    'relationships': [],
                    'current_cycle': 0,
                    'last_run': None,
                    'coverage_history': []
                }
                for symbol_id in self.config.CORE_SYMBOLS:
                    data['symbols'].append({
                        'symbol_id': symbol_id,
                        'name': f"Symbol_{symbol_id}",
                        'domains': [],
                        'relationships': []
                    })
                with open(self.db_path, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                if data.get('schema_version', '0.0') < self.config.SCHEMA_VERSION:
                    data['schema_version'] = self.config.SCHEMA_VERSION
                    with open(self.db_path, 'w') as f:
                        json.dump(data, f, indent=2)
        
        def get_all_symbols(self):
            with open(self.db_path, 'r') as f:
                return json.load(f).get('symbols', [])
        
        def add_result(self, result_data):
            with open(self.db_path, 'r') as f:
                data = json.load(f)
            data['current_cycle'] = data.get('current_cycle', 0) + 1
            data['last_run'] = datetime.now().isoformat()
            result_entry = {
                'timestamp': datetime.now().isoformat(),
                'symbol_id': result_data.get('symbol_id'),
                'source_url': result_data.get('source_url'),
                'analysis_summary': result_data.get('analysis_summary', '')[:500]
            }
            data['results'].append(result_entry)
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
    
    class CacheManager:
        def __init__(self, config):
            self.config = config
            self.cache_path = config.CACHE_PATH
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            self._ensure_empty()
        
        def _ensure_empty(self):
            if not self.cache_path.exists():
                with open(self.cache_path, 'w') as f:
                    json.dump({'version': '1.0', 'queries': {}}, f)
        
        def load_cache(self):
            try:
                if self.cache_path.exists():
                    with open(self.cache_path, 'r') as f:
                        return json.load(f)
            except:
                pass
            return {'version': '1.0', 'queries': {}}
        
        def save_cache(self, data):
            try:
                with open(self.cache_path, 'w') as f:
                    json.dump(data, f)
            except Exception as e:
                logging.error(f"Cache save error: {e}")
        
        def is_cached(self, query_text):
            cache = self.load_cache()
            query_hash = hashlib.md5(query_text.encode()).hexdigest()
            current_time = datetime.now()
            
            for q_hash, q_data in cache.get('queries', {}).items():
                if q_hash == query_hash:
                    timestamp_str = q_data.get('timestamp', '')
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        age_hours = (current_time - timestamp).total_seconds() / 3600
                        ttl_hours = float(cache.get('ttl_hours', self.config.CACHE_TTL_HOURS))
                        if age_hours <= ttl_hours:
                            return q_data
                    except:
                        pass
            return None
        
        def cache_result(self, query_text, results):
            cache = self.load_cache()
            query_hash = hashlib.md5(query_text.encode()).hexdigest()
            
            # Remove expired entries
            current_time = datetime.now()
            for q_hash in list(cache['queries'].keys()):
                try:
                    timestamp_str = cache['queries'][q_hash].get('timestamp', '')
                    timestamp = datetime.fromisoformat(timestamp_str)
                    age_hours = (current_time - timestamp).total_seconds() / 3600
                    ttl_hours = float(cache.get('ttl_hours', self.config.CACHE_TTL_HOURS))
                    if age_hours > ttl_hours:
                        del cache['queries'][q_hash]
                except:
                    pass
            
            cache['queries'][query_hash] = {
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
            # Limit to 50 entries
            if len(cache['queries']) > 50:
                cache['queries'] = dict(list(cache['queries'].items())[-50:])
            
            self.save_cache(cache)
