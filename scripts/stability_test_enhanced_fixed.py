#!/usr/bin/env python3
"""
🧪 Enhanced Stability Test on Gematria Database
=====================================================

Comprehensive integrity checks for gematria database system.
Runs as part of overnight research loop.

Usage:
    python3 stability_test_enhanced_fixed.py --timeout 2700

Phase marker format in logs: === PHASE: STABILITY_TEST ===
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any
import time

# Auto-detect gematria directory location
HERE = Path(__file__).resolve().parent.parent
GEMATRIA_DIR = HERE

DB_DIR = GEMATRIA_DIR / "database"
SYMBOLS_FILE = DB_DIR / "symbols.json"
FORCES_FILE = DB_DIR / "forces.json"


def log(output: str):
    """Log to stdout with timestamp"""
    ts = datetime.now(timezone.utc).strftime('%H:%M:%S UTC')
    print(f"[{ts}] {output}")


class StabilityTest:
    """Enhanced stability test for gematria database"""
    
    def __init__(self, db_dir: Path):
        self.db_dir = db_dir
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_total = 0
    
    def run(self, timeout: int = 2700) -> Dict[str, Any]:
        """Run comprehensive stability test"""
        
        # Check 1: Directory Structure exists and has required files
        
        print("\n📁 Checking Directory Structure...")
        
        checks_passed = False
        errors = []
        warnings = []
        
        try:
            # Verify the base directory has all required file paths (not subdirectories!)
            self.check_1_directory_structure()
            
            # Test 2: JSON file integrity
            self.check_2_json_integrity()
            
            # Test 3: Symbol data completeness
            self.check_3_symbol_completeness()
            
            # Test 4: Force data consistency
            self.check_4_force_consistency()
            
            # Test 5: Relationship matrix validity
            self.check_5_relationship_matrix()
            
            # Test 6: Cross-domain pattern integrity
            self.check_6_cross_domain_patterns()
            
            # Test 7: File timestamps (database freshness)
            self.check_7_database_freshness()
            
            # Generate summary report
            return {
                "success": len(self.errors) == 0,
                "errors": self.errors,
                "warnings": self.warnings,
                "checks_passed": self.checks_passed,
                "checks_total": self.checks_total,
                "passed_percentage": round((self.checks_passed / max(self.checks_total, 1)) * 100, 2)
            }
            
        except Exception as e:
            log(f"❌ STABILITY TEST EXCEPTION: {str(e)[:200]}")
            return {"success": False, "error": str(e), "errors": [str(e)]}
    
    def check_1_directory_structure(self) -> None:
        """Verify directory structure exists and is accessible"""
        self.checks_total += 1
        
        log("\n   → Check 1/7: Directory Structure")
        
        # Actual database layout based on filesystem inspection
        required_paths = [
            "database/gematria_database.json",
            "database/symbols.json",
            "database/forces.json"
        ]
        
        missing_paths = []
        for path_str in required_paths:
            full_path = GEMATRIA_DIR / path_str
            if not full_path.exists():
                missing_paths.append(path_str)
                error_msg = f"❌ Missing path: {path_str}"
                log(error_msg)
                self.errors.append(error_msg)
        
        if len(missing_paths) == 0:
            log("   ✅ Directory structure verified")
            self.checks_passed += 1
    
    def check_2_json_integrity(self) -> None:
        """Verify JSON files are valid and readable"""
        self.checks_total += 1
        
        log("\n   → Check 2/7: JSON File Integrity")
        
        for filepath in [SYMBOLS_FILE, FORCES_FILE]:
            if not filepath.exists():
                error_msg = f"❌ Missing file: {filepath.name}"
                log(error_msg)
                self.errors.append(error_msg)
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if not isinstance(data, dict):
                    error_msg = f"❌ {filepath.name}: JSON root is not an object"
                    log(error_msg)
                    self.errors.append(error_msg)
                    continue
                
                log(f"   ✅ {filepath.name} - Valid JSON ({len(json.dumps(data))} bytes)")
                self.checks_passed += 1
                
            except json.JSONDecodeError as e:
                error_msg = f"❌ {filepath.name}: JSON parse error - {str(e)[:50]}"
                log(error_msg)
                self.errors.append(error_msg)
            
            except Exception as e:
                error_msg = f"❌ {filepath.name}: Read error - {str(e)[:50]}"
                log(error_msg)
                self.errors.append(error_msg)
    
    def check_3_symbol_completeness(self) -> None:
        """Verify symbol data has required fields"""
        self.checks_total += 1
        
        log("\n   → Check 3/7: Symbol Data Completeness")
        
        if not SYMBOLS_FILE.exists():
            error_msg = "❌ Cannot verify symbols - file missing"
            log(error_msg)
            self.errors.append(error_msg)
            return
        
        try:
            with open(SYMBOLS_FILE, 'r') as f:
                data = json.load(f)
            
            required_fields = ["symbol_id", "name", "domains"]
            missing_symbols = 0
            incomplete_fields = []
            
            for symbol in data.get("analyzed_symbols", []):
                for field in required_fields:
                    if field not in symbol:
                        incomplete_fields.append(f"{symbol.get('symbol_id', '?')}-{field}")
                        missing_symbols += 1
            
            if missing_symbols > 0:
                error_msg = f"❌ {missing_symbols} symbols missing required fields: {incomplete_fields}"
                log(error_msg)
                self.errors.append(error_msg)
            else:
                log(f"   ✅ All {len(data.get('analyzed_symbols', []))} symbols have complete data")
                self.checks_passed += 1
                
        except Exception as e:
            error_msg = f"❌ Symbol check exception: {str(e)[:100]}"
            log(error_msg)
            self.errors.append(error_msg)
    
    def check_4_force_consistency(self) -> None:
        """Verify force data is consistent"""
        self.checks_total += 1
        
        log("\n   → Check 4/7: Force Data Consistency")
        
        if not FORCES_FILE.exists():
            error_msg = "❌ Cannot verify forces - file missing"
            log(error_msg)
            self.errors.append(error_msg)
            return
        
        try:
            with open(FORCES_FILE, 'r') as f:
                data = json.load(f)
            
            # Check each force definition
            for force_name, force_data in data.get("forces", {}).items():
                required_fields = ["name", "characteristics", "element_type"]
                missing_fields = [f for f in required_fields if f not in force_data]
                
                if missing_fields:
                    error_msg = f"❌ Force '{force_name}' missing fields: {missing_fields}"
                    log(error_msg)
                    self.errors.append(error_msg)
            
            # Verify compatibility matrix exists
            if "compatibility_matrix" not in data:
                warning_msg = f"⚠️ Compatibility matrix missing from forces.json (non-critical)"
                log(warning_msg)
                self.warnings.append(warning_msg)
                
            log(f"   ✅ Verified {len(data.get('forces', {}))} force definitions")
            self.checks_passed += 1
            
        except Exception as e:
            error_msg = f"❌ Force check exception: {str(e)[:100]}"
            log(error_msg)
            self.errors.append(error_msg)
    
    def check_5_relationship_matrix(self) -> None:
        """Verify relationship references are valid"""
        self.checks_total += 1
        
        log("\n   → Check 5/7: Relationship Matrix Validity")
        
        if not SYMBOLS_FILE.exists():
            error_msg = "❌ Cannot verify relationships - symbols file missing"
            log(error_msg)
            self.errors.append(error_msg)
            return
        
        try:
            with open(SYMBOLS_FILE, 'r') as f:
                data = json.load(f)
            
            all_symbols = {s["symbol_id"]: s for s in data.get("analyzed_symbols", [])}
            invalid_refs = []
            
            for symbol in data.get("analyzed_symbols", []):
                refs = symbol.get("relationships", [])
                for ref_id in refs:
                    if ref_id not in all_symbols:
                        invalid_refs.append(f"{symbol['symbol_id']} -> {ref_id}")
            
            if invalid_refs:
                error_msg = f"❌ Invalid relationship references: {invalid_refs[:5]}"
                log(error_msg)
                self.errors.append(error_msg)
            else:
                log("   ✅ All relationship references are valid")
                self.checks_passed += 1
                
        except Exception as e:
            error_msg = f"❌ Relationship check exception: {str(e)[:100]}"
            log(error_msg)
            self.errors.append(error_msg)
    
    def check_6_cross_domain_patterns(self) -> None:
        """Verify cross-domain pattern data exists"""
        self.checks_total += 1
        
        log("\n   → Check 6/7: Cross-Domain Patterns")
        
        # Check for research patterns file
        patterns_file = self.db_dir.parent / "research" / "patterns.json"
        
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
                
                required_keys = ["pattern_id", "symbol_ids"]
                valid_patterns = 0
                
                for pattern in data.get("patterns", []):
                    if all(k in pattern for k in required_keys):
                        valid_patterns += 1
                
                log(f"   ✅ Validated {valid_patterns}/{len(data.get('patterns', []))} cross-domain patterns")
                self.checks_passed += 1
                
            except Exception as e:
                error_msg = f"❌ Patterns file check exception: {str(e)[:100]}"
                log(error_msg)
                self.errors.append(error_msg)
        else:
            warning_msg = f"⚠️ Cross-domain patterns file not found (non-critical)"
            log(warning_msg)
            self.warnings.append(warning_msg)
    
    def check_7_database_freshness(self) -> None:
        """Check database file timestamps"""
        self.checks_total += 1
        
        log("\n   → Check 7/7: Database Freshness")
        
        now = datetime.now(timezone.utc)
        
        for filepath in [SYMBOLS_FILE, FORCES_FILE]:
            if filepath.exists():
                stat = filepath.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc)
                age_hours = (now - mtime).total_seconds() / 3600
                
                if age_hours > 72:
                    warning_msg = f"⚠️ {filepath.name} is {age_hours:.1f} hours old (> 3 days)"
                    log(warning_msg)
                    self.warnings.append(warning_msg)
                else:
                    log(f"   ✅ {filepath.name} updated {age_hours:.1f}h ago")
        
        log("   → Database freshness check complete")
        self.checks_passed += 1


def main():
    """Main entry point"""
    
    # Parse arguments
    timeout = 2700
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.startswith("--timeout"):
            try:
                timeout = int(arg.split("=")[1])
                print(f"Timeout set from argument to: {timeout} seconds")
            except (ValueError, IndexError):
                pass
    
    # Run stability test
    config = StabilityTest(GEMATRIA_DIR)
    result = config.run(timeout=timeout)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🧪 STABILITY TEST SUMMARY")
    print("=" * 60)
    
    if result["success"]:
        print(f"✅ ALL CHECKS PASSED ({result['checks_passed']}/{result['checks_total']})")
        if result["warnings"]:
            print(f"⚠️ Warnings: {len(result['warnings'])}")
        for warning in result["warnings"][:3]:
            print(f"   → {warning}")
    else:
        print(f"❌ TEST FAILED ({result['checks_passed']}/{result['checks_total']} checks passed)")
        print(f"Errors: {len(result['errors'])}, Warnings: {len(result['warnings'])}")
    
    for error in result["errors"][:5]:
        print(f"   → Error: {error}")
    
    print("=" * 60)
    print(f"Passed percentage: {result.get('passed_percentage', 0)}%")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
