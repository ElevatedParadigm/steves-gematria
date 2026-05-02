#!/usr/bin/env python3
"""
Huffman & Delta Compression for Gematria Research Data
Reduces storage for symbol patterns, domain mappings, and sequence data.
"""

import json
import sys
from collections import Counter
import heapq


class HuffmanCoder:
    """
    Huffman coding for frequent symbols/terms in gematria research.
    Example: '124' → '0', '666' → '101', '55' → '110' (shorter codes for common symbols)
    """
    
    def __init__(self):
        self.codes = {}
        self.code_to_symbol = {}
        self.min_freq = 3  # Only encode symbols appearing 3+ times
    
    @staticmethod
    def build_huffman_tree(frequency_dict):
        """Build Huffman tree from symbol frequencies."""
        if not frequency_dict:
            return [], {}
        
        # Create leaf nodes
        heap = [(freq, {'freq': freq, 'symbol': sym}) 
                for sym, freq in frequency_dict.items()]
        heapq.heapify(heap)
        
        # Build tree
        while len(heap) > 1:
            freq1, node1 = heapq.heappop(heap)
            freq2, node2 = heapq.heappop(heap)
            
            # Create internal node
            merged = {'freq': freq1 + freq2}
            
            if 'symbol' in node1:
                node1['is_leaf'] = True
                merged['left'] = node1
            else:
                merged['left'] = node1
            
            if 'symbol' in node2:
                node2['is_leaf'] = True
                merged['right'] = node2
            else:
                merged['right'] = node2
            
            heapq.heappush(heap, (merged['freq'], merged))
        
        return heap[0][1] if heap else None
    
    def encode(self, symbol_sequence):
        """Encode a sequence using Huffman codes."""
        if not self.codes and symbol_sequence:
            # Build from current data
            freq = Counter(symbol_sequence)
            tree = self.build_huffman_tree(freq)
            
            if tree:
                self._generate_codes(tree, '')
        
        if not self.codes:
            raise ValueError("Need data to build Huffman codes first!")
        
        # Encode with fallback for unknown symbols
        encoded = []
        for symbol in symbol_sequence:
            if symbol in self.codes:
                encoded.append(self.codes[symbol])
            else:
                # Fallback: use fixed 3-bit code
                idx = len([s for s in self.codes])
                encoded.append(f'{idx:03b}')
        
        return ''.join(encoded)
    
    def decode(self, encoded_bits):
        """Decode bits back to symbols."""
        if not encoded_bits:
            return []
        
        decoded = []
        current_code = ''
        
        for bit in encoded_bits:
            current_code += bit
            
            if current_code in self.code_to_symbol:
                decoded.append(self.code_to_symbol[current_code])
                current_code = ''
            
            # Safety limit to prevent infinite loop on malformed data
            if len(current_code) > 20:
                raise ValueError("Malformed encoded data")
        
        return decoded
    
    def _generate_codes(self, node, prefix):
        """Generate Huffman codes from tree structure."""
        if 'symbol' in node:
            symbol = node['symbol']
            freq = node.get('freq', 1)
            self.codes[symbol] = prefix or '0'  # Single symbol case
            self.code_to_symbol[prefix or '0'] = symbol
        elif 'left' in node:
            self._generate_codes(node['left'], prefix + '0')
            self._generate_codes(node['right'], prefix + '1')


class DeltaEncoder:
    """
    Delta encoding for sequential pattern data.
    Stores differences between consecutive values instead of full values.
    Example: [124, 666, 55] → [0, 542, -611] (first value = 0, rest are deltas)
    """
    
    def __init__(self, max_bits=16):
        self.max_bits = max_bits
        self.min_delta = -(2 ** (max_bits - 1))
        self.max_delta = 2 ** (max_bits - 1) - 1
    
    def encode_sequence(self, sequence):
        """Encode a numeric sequence using deltas."""
        if not sequence:
            return []
        
        # First element is absolute (or delta from base)
        encoded = [sequence[0] % (2 ** self.max_bits)]
        
        # Encode differences
        for i in range(1, len(sequence)):
            diff = sequence[i] - sequence[i - 1]
            # Wrap if exceeds max_delta range
            if diff > self.max_delta:
                diff -= 2 ** self.max_bits
            elif diff < self.min_delta:
                diff += 2 ** self.max_bits
            encoded.append(diff % (2 ** self.max_bits))
        
        return encoded
    
    def decode_sequence(self, deltas):
        """Decode delta-encoded sequence."""
        if not deltas:
            return []
        
        # First element is absolute value
        result = [deltas[0]]
        
        # Reconstruct from deltas
        for delta in deltas[1:]:
            prev = result[-1]
            reconstructed = (prev + delta) % (2 ** self.max_bits)
            result.append(reconstructed)
        
        return result


def compress_gematria_data(data_type, data):
    """
    Compress gematria research data using appropriate technique.
    
    Args:
        data_type: 'symbols' (Huffman), 'sequences' (Delta), or 'text' (both)
        data: Raw data to compress
    
    Returns dict with compressed bytes and metadata
    """
    
    if data_type == 'symbols':
        # Extract symbol frequencies first
        freq = Counter(data)
        
        # Only encode frequent symbols
        filtered_freq = {k: v for k, v in freq.items() if v >= 3}
        
        huffman = HuffmanCoder()
        # Build codes from filtered data
        tree = huffman.build_huffman_tree(filtered_freq)
        if tree:
            huffman._generate_codes(tree, '')
        
        # Encode the sequence
        try:
            compressed = huffman.encode(data)
        except ValueError:
            compressed = ''
        
        metadata = {
            'technique': 'huffman',
            'unique_symbols': len(set(data)),
            'frequent_symbols': len(filtered_freq),
            'compression_bits': len(compressed)
        }
        
    elif data_type == 'sequences':
        encoder = DeltaEncoder()
        compressed = encoder.encode_sequence(data)
        
        metadata = {
            'technique': 'delta',
            'original_elements': len(data),
            'compressed_elements': len(compressed),
            'max_abs_value': max(abs(x) for x in data) if data else 0,
            'max_delta': max(abs(compressed[i] - compressed[i-1]) 
                            for i in range(1, len(compressed)) if len(compressed) > 1)
                             .__class__.__dict__.get('__self__', 0)
        }
        
        # Actually calculate max delta properly
        deltas = [data[0]] + [data[i] - data[i-1] for i in range(1, len(data))]
        metadata['max_delta'] = max(abs(d) for d in deltas)
    
    elif data_type == 'text':
        # Text with symbol sequences mixed
        compressed = ''
        symbols_only = []
        text_parts = []
        
        current_text = ""
        for char in data:
            if char.isdigit():
                current_text += char
            else:
                if current_text:
                    if len(current_text) >= 2 and all(c.isdigit() for c in current_text):
                        symbols_only.append(int(current_text))
                    else:
                        text_parts.append(char)
                current_text = ""
        
        # Add remaining
        if current_text and all(c.isdigit() for c in current_text):
            try:
                symbols_only.append(int(current_text))
            except ValueError:
                text_parts.append(current_text)
        
        # Compress each separately
        if symbols_only:
            huffman = HuffmanCoder()
            tree = huffman.build_huffman_tree(Counter(symbols_only))
            if tree:
                huffman._generate_codes(tree, '')
            compressed_symbols = huffman.encode(symbols_only)
        
        if text_parts:
            encoded_text = ''.join([str(ord(c)) for c in text_parts])
        
        metadata = {
            'technique': 'hybrid',
            'symbol_sequences': len(symbols_only),
            'text_length': len(text_parts)
        }
    else:
        raise ValueError(f"Unknown data type: {data_type}")
    
    return {
        'compressed': compressed if isinstance(compressed, str) else 
                  ', '.join(map(str, compressed)),
        'metadata': metadata,
        'original_size_bytes': len(data)
    }


def decompress_gematria_data(compressed_str, metadata):
    """
    Decompress data and return original sequence.
    
    Args:
        compressed_str: Compressed string (bits or comma-separated deltas)
        metadata: Compression metadata from compress function
    """
    
    technique = metadata.get('technique', '')
    
    if technique == 'huffman':
        decoder = HuffmanCoder()
        decoded = decoder.decode(compressed_str)
        
    elif technique == 'delta':
        encoder = DeltaEncoder()
        decoded = encoder.decode_sequence(
            [int(x) for x in compressed_str.split(',')]
        )
    
    return decoded


def main():
    """Demonstration and testing."""
    
    # Example 1: Symbol frequency compression
    print("=" * 60)
    print("Huffman Coding Example - Symbol Frequency Compression")
    print("=" * 60)
    
    sample_symbols = [
        '124', '124', '124', '963', '55', 
        '124', '666', '963', '963', '55',
        '124', '55', '963', '124', '111'
    ]
    
    print(f"\nOriginal sequence: {sample_symbols}")
    print(f"Length: {len(sample_symbols)} symbols")
    
    huffman = HuffmanCoder()
    # Build codes from sample data
    tree = huffman.build_huffman_tree(Counter(sample_symbols))
    if tree:
        huffman._generate_codes(tree, '')
    
    compressed = huffman.encode(sample_symbols)
    print(f"\nHuffman Codes generated:")
    for sym, code in sorted(huffman.codes.items(), 
                           key=lambda x: len(x[1])):
        print(f"  '{sym}' → '{code}' ({len(code)} bits)")
    
    print(f"\nCompressed: {compressed} ({len(compressed)} bits)")
    print(f"Original size: {len(sample_symbols) * 3} chars (assuming 3-char codes)")
    print(f"Compression ratio: {len(compressed) / (len(sample_symbols) * 3):.2%}")
    
    # Example 2: Delta encoding for sequence tracking
    print("\n" + "=" * 60)
    print("Delta Encoding Example - Pattern Trail Compression")
    print("=" * 60)
    
    pattern_sequence = [124, 124, 666, 55, 124, 963, 55]
    
    print(f"\nOriginal sequence: {pattern_sequence}")
    
    delta_encoder = DeltaEncoder(max_bits=16)
    compressed_delta = delta_encoder.encode_sequence(pattern_sequence)
    
    print(f"Delta encoded: {compressed_delta}")
    print(f"Deltas from original:")
    for i, (orig, delta) in enumerate(zip([0] + pattern_sequence[:-1], 
                                         compressed_delta)):
        print(f"  [{i}]: orig={orig}, delta={delta:+d}, result={orig+delta}")
    
    # Verify round-trip
    decompressed = delta_encoder.decode_sequence(compressed_delta)
    print(f"\nDecompressed: {decompressed}")
    print(f"Match: {decompressed == pattern_sequence}")
    
    # Example 3: Combined compression for research database
    print("\n" + "=" * 60)
    print("Combined Compression - Visual Archive Database Entry")
    print("=" * 60)
    
    research_entry = {
        'domain': 'ancient_symbols',
        'anchor_terms': ['124', '963', '55', '666'],
        'pattern_trail': [124, 666, 55, 963, 111, 124],
        'description': 'ancient symbol cluster with cycle completion'
    }
    
    # Compress anchor terms
    print(f"\nCompressing anchor_terms: {research_entry['anchor_terms']}")
    huffman = HuffmanCoder()
    tree = huffman.build_huffman_tree(Counter(research_entry['anchor_terms']))
    if tree:
        huffman._generate_codes(tree, '')
    compressed_anchor = ','.join(huffman.encode(research_entry['anchor_terms']))
    
    # Compress pattern trail with delta
    print(f"Compressing pattern_trail: {research_entry['pattern_trail']}")
    delta_encoder = DeltaEncoder()
    compressed_trail = delta_encoder.encode_sequence(
        research_entry['pattern_trail']
    )
    
    # Store compressed metadata
    compressed_entry = {
        'domain': research_entry['domain'],
        'compressed_anchor_terms': compressed_anchor,
        'anchor_metadata': f"technique=huffman,symbols={len(research_entry['anchor_terms'])}",
        'compressed_pattern_trail': ','.join(map(str, compressed_trail)),
        'trail_metadata': f"technique=delta,max_bits=16,original_length={len(research_entry['pattern_trail'])}",
        'description': research_entry['description']
    }
    
    print(f"\nCompressed entry stored:")
    for key, value in compressed_entry.items():
        if isinstance(value, str):
            print(f"  {key}: '{value[:50]}...' (if > 50 chars)")
        else:
            print(f"  {key}: {value}")
    
    print("\n✅ Compression tools ready for Visual Archive storage!")
    print("   - Use compress_gematria_data() for database entries")
    print("   - Decompress before visualization display")


if __name__ == "__main__":
    main()
