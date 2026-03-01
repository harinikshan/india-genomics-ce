#!/usr/bin/env python3
"""
VCF to 23andMe Format Converter

Converts a standard VCF file (e.g., from clinical WGS/WES) into 23andMe-compatible
tab-separated format so it can be processed by the genetic analysis pipeline.

VCF genotypes (0/0, 0/1, 1/1) are converted to allele strings (AA, AG, GG).
Only SNPs with rsIDs and PASS/common filters are included.
Chromosome names are stripped of 'chr' prefix to match 23andMe format.
"""

import sys
from pathlib import Path


def convert_vcf_to_23andme(vcf_path: str, output_path: str, filter_pass_only: bool = False):
    """Convert a VCF file to 23andMe format.

    Args:
        vcf_path: Path to input VCF file
        output_path: Path to output 23andMe-format file
        filter_pass_only: If True, only include PASS variants. If False, include
                          all variants (some clinical VCFs mark many real variants
                          with quality filters).
    """
    vcf_path = Path(vcf_path)
    output_path = Path(output_path)

    if not vcf_path.exists():
        print(f"Error: VCF file not found: {vcf_path}")
        sys.exit(1)

    total_lines = 0
    converted = 0
    skipped_no_rsid = 0
    skipped_indel = 0
    skipped_multiallelic = 0
    skipped_no_call = 0
    skipped_filter = 0

    with open(vcf_path, 'r') as vcf, open(output_path, 'w') as out:
        # Write 23andMe-style header
        out.write("# rsid\tchromosome\tposition\tgenotype\n")
        out.write(f"# Converted from VCF: {vcf_path.name}\n")

        for line in vcf:
            # Skip VCF headers
            if line.startswith('#'):
                continue

            total_lines += 1
            parts = line.strip().split('\t')
            if len(parts) < 10:
                continue

            chrom = parts[0]
            pos = parts[1]
            rsid = parts[2]
            ref = parts[3]
            alt = parts[4]
            filt = parts[6]
            format_field = parts[8]
            sample_field = parts[9]

            # Skip variants without rsID
            if rsid == '.' or not rsid.startswith('rs'):
                skipped_no_rsid += 1
                continue

            # Skip multiallelic sites (comma-separated ALT)
            if ',' in alt:
                skipped_multiallelic += 1
                continue

            # Skip indels - only keep SNPs (single nucleotide changes)
            if len(ref) != 1 or len(alt) != 1:
                skipped_indel += 1
                continue

            # Optionally filter on FILTER column
            if filter_pass_only and filt not in ('PASS', '.'):
                skipped_filter += 1
                continue

            # Parse genotype from FORMAT and sample fields
            format_keys = format_field.split(':')
            sample_values = sample_field.split(':')

            gt_index = None
            for i, key in enumerate(format_keys):
                if key == 'GT':
                    gt_index = i
                    break

            if gt_index is None or gt_index >= len(sample_values):
                skipped_no_call += 1
                continue

            gt = sample_values[gt_index]

            # Skip no-calls
            if '.' in gt:
                skipped_no_call += 1
                continue

            # Parse genotype: 0/0 = REF/REF, 0/1 = REF/ALT, 1/1 = ALT/ALT
            # Handle both / and | (phased) separators
            alleles_idx = gt.replace('|', '/').split('/')

            allele_map = {'0': ref, '1': alt}

            try:
                allele1 = allele_map[alleles_idx[0]]
                allele2 = allele_map[alleles_idx[1]]
            except (KeyError, IndexError):
                skipped_no_call += 1
                continue

            genotype = allele1 + allele2

            # Convert chromosome: strip 'chr' prefix, handle X/Y/MT
            chrom_clean = chrom.replace('chr', '')
            if chrom_clean == 'M':
                chrom_clean = 'MT'

            # Write in 23andMe format
            out.write(f"{rsid}\t{chrom_clean}\t{pos}\t{genotype}\n")
            converted += 1

    print(f"\nConversion complete:")
    print(f"  Total variant lines: {total_lines}")
    print(f"  Converted (SNPs with rsID): {converted}")
    print(f"  Skipped (no rsID): {skipped_no_rsid}")
    print(f"  Skipped (indels): {skipped_indel}")
    print(f"  Skipped (multiallelic): {skipped_multiallelic}")
    print(f"  Skipped (no call): {skipped_no_call}")
    if filter_pass_only:
        print(f"  Skipped (filter): {skipped_filter}")

    return converted


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python vcf_to_23andme.py <input.vcf> <output.txt>")
        sys.exit(1)

    convert_vcf_to_23andme(sys.argv[1], sys.argv[2])
