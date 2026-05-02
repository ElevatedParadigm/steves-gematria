    def _extract_relationships(self, results: List[Dict]):
        """Simplified relationship extraction based on domain overlap."""
        symbol_results: Dict[int, List[Dict]] = {}
        
        for result in results:
            symbol_id = result.get('symbol_id')
            if symbol_id not in symbol_results:
                symbol_results[symbol_id] = []
            symbol_results[symbol_id].append(result)
        
        # Simple cross-domain relationships
        domain_to_symbols: Dict[str, List[int]] = defaultdict(list)
        for symbol_id, s_results in symbol_results.items():
            for r in s_results:
                domain = r.get('domain')
                if domain:
                    domain_to_symbols[domain].append(symbol_id)
        
        # Create relationships between symbols sharing domains
        rel_count = 0
        for domain, symbols in domain_to_symbols.items():
            if len(symbols) >= 2:
                for i, sym1 in enumerate(symbols):
                    for sym2 in symbols[i+1:]:
                        relevance = 0.5 + (hash(f"{domain}{sym1}{sym2}") % 30) / 100
                        
                        self.db.add_relationship(str(sym1), str(sym2), relevance)
                        self.db.add_relationship(str(sym2), str(sym1), relevance)
                        
                        rel_count += 1
        
        logging.info(f"Extracted {rel_count} cross-domain relationships")

    def _detect_anomalies(self, results: List[Dict]):
        """Simplified anomaly detection."""
        domain_counts = defaultdict(int)
        for r in results:
            domain = r.get('domain')
            if domain:
                domain_counts[domain] += 1
        
        # Factor: Domain distribution variance
        counts_list = list(domain_counts.values())
        if len(counts_list) >= 2:
            mean_count = sum(counts_list) / len(counts_list)
            variance = sum((c - mean_count) ** 2 for c in counts_list) / len(counts_list)
            factor_scores.append(min(variance / 10, 1.0))
        else:
            factor_scores.append(0.3)
        
        anomaly_score = min(factor_scores[0] + (1.0 - len(domain_counts)/len(DOMAINS)), 1.0)
        
        self.anomalies = {
            'anomaly_score': round(anomaly_score, 3),
            'cross_domain_connections': [],
            'high_similarity_clusters': [r for r in results if r.get('similarity_score', 0) > 0.8][:5],
            'recommendations': ['Review domain distribution'] if anomaly_score > 0.6 else []
        }
        
        logging.info(f"Anomaly detection complete. Score: {anomaly_score:.3f}")

    def _generate_report(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        cycle_num = self.db.get_cycle_count() + 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        lines = []
        lines.append("# 🌙 Overnight Research Report #{}".format(cycle_num))
        lines.append("**Generated:** {}".format(timestamp))
        lines.append("")
        lines.append("## 📋 Executive Summary")
        lines.append("- **Total Results Processed:** {0:,}".format(len(results)))
        lines.append("- **Symbols Analyzed:** {} of {}".format(len(self.results_by_symbol), len(CORE_SYMBOLS)))
        
        domains_processed = set(r.get('domain') for r in results if r.get('domain'))
        lines.append("- **Domains Covered:** {}/{}".format(len(domains_processed), len(DOMAINS)))
        lines.append("")
        lines.append("## 🔢 Symbol Analysis Results")
        lines.append("")
        
        for symbol_id in CORE_SYMBOLS:
            count = len(self.results_by_symbol.get(symbol_id, []))
            status = "✓ {} results".format(count) if count > 0 else "○ 0 results"
            lines.append("Symbol {}: {}".format(symbol_id, status))
        lines.append("")
        
        lines.append("## 🔗 Knowledge Graph Relationships")
        lines.append("")
        lines.append("Cross-domain relationships tracked in database.")
        lines.append("")
        
        lines.append("## 📊 Analysis Summary")
        lines.append("-" * 40)
        
        if self.results_by_symbol:
            max_count = max(len(v) for v in self.results_by_symbol.values()) if self.results_by_symbol else 1
            for symbol_id in CORE_SYMBOLS:
                count = len(self.results_by_symbol.get(symbol_id, []))
                bar_width = int(30 * count / max_count) if max_count > 0 else 0
                bar = '█' * bar_width + '.' * (30 - bar_width)
                lines.append("Symbol {}: {}".format(symbol_id, bar))
        lines.append("")
        
        report_text = "\\n".join(lines)
        
        return {
            'status': 'completed',
            'timestamp': timestamp,
            'cycle': cycle_num,
            'total_results': len(results),
            'symbols_analyzed': len(self.results_by_symbol),
            'domains_processed': list(domains_processed),
            'relationships_extracted': self.db.get('relationships', []) if isinstance(self.db.get('relationships'), list) else 0,
            'anomaly_score': self.anomalies.get('anomaly_score', 0.0),
            'high_similarity_clusters': len(self.anomalies.get('high_similarity_clusters', [])),
            'cross_domain_connections': len(self.anomalies.get('cross_domain_connections', [])),
            'report_text': report_text
        }
